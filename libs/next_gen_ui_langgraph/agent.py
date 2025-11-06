import asyncio
import logging
import uuid
from typing import Literal, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, ToolCall, ToolMessage
from langchain_core.runnables.config import RunnableConfig
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.types import Command
from next_gen_ui_agent import InputData, NextGenUIAgent, UIComponentMetadata
from next_gen_ui_agent.data_transform.types import ComponentDataBase
from next_gen_ui_agent.model import InferenceBase, LangChainModelInference
from next_gen_ui_agent.types import AgentConfig, UIBlock, UIBlockRendering
from typing_extensions import TypedDict

logger = logging.getLogger(__name__)


# Graph State Schema
class AgentState(MessagesState):
    backend_data: list[InputData]
    user_prompt: str
    components: list[UIComponentMetadata]
    components_data: list[ComponentDataBase]
    renditions: list[UIBlockRendering]
    ui_blocks: list[UIBlock]
    errors: list[str]


class AgentInputState(MessagesState):
    backend_data: list[InputData]
    user_prompt: str


class AgentOutputState(MessagesState):
    components: list[UIComponentMetadata]
    components_data: list[ComponentDataBase]
    renditions: list[UIBlockRendering]
    ui_blocks: list[UIBlock]
    errors: list[str]


# Graph Config Schema
class GraphConfig(TypedDict):
    model: Optional[str]
    model_api_base_url: Optional[str]
    model_api_token: Optional[str]
    component_system: Literal["none", "patternfly", "rhds", "json"]


class NextGenUILangGraphAgent:
    """Next Gen UI Agent in LangGraph."""

    def __init__(
        self,
        model: BaseChatModel,
        inference: Optional[InferenceBase] = None,
        config: Optional[AgentConfig] = None,
        output_messages_with_ui_blocks: Optional[bool] = False,
    ):
        """
        Initialize Next Gen UI Agent in LangGraph. Inference is created from model if not provided in config.

        Args:
            * model: The model to use for inference.
            * inference: Optional custom inference implementation.
            * config: Optional UI Agent configuration.
            * output_messages_with_ui_blocks: Whether to output tool messages with whole `UIBlock` serialized in the `content`.
              Default is False which outputs only the result of the rendering step here (the rendered code).
        """
        super().__init__()
        if not inference:
            inference = LangChainModelInference(model)

        config = config if config else AgentConfig()

        self.ngui_agent = NextGenUIAgent(config=config, inference=inference)
        self.output_messages_with_ui_blocks = output_messages_with_ui_blocks

    # Nodes
    async def data_selection(self, state: AgentInputState, config: RunnableConfig):
        backend_data = state.get("backend_data", [])
        user_prompt = state.get("user_prompt", "")

        if user_prompt and len(backend_data) > 0:
            logger.info("User_prompt and backend_data taken from state directly")
            return

        messages = state["messages"]
        # logger.debug(messages)

        messagesReversed = list(reversed(messages))
        for m in messagesReversed:
            # logger.debug(m.content)
            # TODO ERRHANDLING Handle better success/error messages
            if (
                m.type
                == "tool"
                # and (m.status and m.status == "success")
                # and (m.name and not m.name.startswith("ngui"))
            ):
                # TODO: Handle m.content as list and remove type: ignore
                backend_data.append(
                    InputData(id=m.tool_call_id, data=m.content, type=m.name)  # type: ignore
                )
            if m.type == "human" and not user_prompt:
                user_prompt = m.content  # type: ignore
            if user_prompt != "" and len(backend_data) > 0:
                break

        logger.info(
            "User_prompt and backend_data taken HumanMessage and ToolMessages. count=%s",
            len(backend_data),
        )
        return {
            "backend_data": backend_data,
            "user_prompt": user_prompt,
        }

    async def component_selection(self, state: AgentState, config: RunnableConfig):
        user_prompt = state["user_prompt"]
        backend_data = state["backend_data"]
        errors = state.get("errors", [])

        # Run select_component in parallel with exception handling
        results = await asyncio.gather(
            *[self.ngui_agent.select_component(user_prompt, d) for d in backend_data],
            return_exceptions=True,
        )

        # Separate successful components from exceptions
        components = []

        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                error_msg = f"Error selecting component for data from tool_call_id='{backend_data[idx]['id']}': {str(result)}"
                logger.error(error_msg)
                errors.append(error_msg)
            else:
                components.append(result)

        return {"components": components, "errors": errors}

    def data_transformation(self, state: AgentState, config: RunnableConfig):
        components = state["components"]
        backend_data = state["backend_data"]
        errors = state.get("errors", [])

        # Create a mapping of backend_data by id for easy lookup
        backend_data_map = {d["id"]: d for d in backend_data}

        # Transform data for each component with exception handling
        components_data = []

        for component in components:
            try:
                # Find the corresponding input_data for this component - this should never happen, but just to be sure
                if component.id not in backend_data_map:
                    error_msg = f"Error transforming data: no data found for component.id='{component.id}'"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    continue

                component_data = self.ngui_agent.transform_data(
                    backend_data_map[component.id], component
                )
                components_data.append(component_data)

            except Exception as e:
                error_msg = f"Error transforming data from tool_call_id='{component.id}': {str(e)}"
                logger.exception(error_msg)
                errors.append(error_msg)

        return {"components_data": components_data, "errors": errors}

    async def choose_system(
        self, state: AgentState, config: RunnableConfig
    ) -> Command[Literal["design_system_handler", "__end__"]]:
        cfg: GraphConfig = config.get("configurable", {})  # type: ignore

        component_system = cfg.get("component_system")
        if component_system and component_system != "none":
            return Command(goto="design_system_handler")

        # TODO is this really correct, shouldn't json renderer be used by default?
        return Command(goto=END)

    def design_system_handler(self, state: AgentState, config: RunnableConfig):
        logger.debug("\n\n---CALL design_system_handler---")
        cfg = config.get("configurable", {})
        component_system = cfg.get("component_system")
        errors = state.get("errors", [])
        backend_data_map = {d["id"]: d for d in state["backend_data"]}
        components_map = {c.id: c for c in state["components"]}

        results = []
        ui_blocks = []
        tool_calls = []
        messages: list[BaseMessage] = []
        for component_data in state["components_data"]:
            try:
                result = self.ngui_agent.generate_rendering(
                    component_data, component_system
                )
                results.append(result)

                logger.debug(
                    "---CALL %s--- id: %s, component rendition: %s",
                    component_system,
                    result.id,
                    result.content,
                )

                ui_block = UIBlock(
                    id=result.id,
                    rendering=result,
                    configuration=self.ngui_agent.construct_UIBlockConfiguration(
                        backend_data_map[component_data.id],
                        components_map[component_data.id],
                    ),
                )

                tm = ToolMessage(
                    status="success",
                    name=f"ngui_{component_system}",
                    tool_call_id=str(result.id) + uuid.uuid4().hex,
                    content=ui_block.model_dump_json()
                    if self.output_messages_with_ui_blocks
                    else str(result.content),
                )
                tool_calls.append(
                    ToolCall(
                        id=tm.tool_call_id,
                        name=tm.name,  # type: ignore
                        args={},
                    )
                )
                messages.append(tm)
                ui_blocks.append(ui_block)
            except Exception as e:
                error_msg = f"Error generating rendering for data from tool_call_id='{component_data.id}': {str(e)}"
                logger.exception(error_msg)
                errors.append(error_msg)

        # convert errors into messages
        if errors:
            for error in errors:
                tm = ToolMessage(
                    status="error",
                    name=f"ngui_error_{component_system}",
                    tool_call_id=uuid.uuid4().hex,
                    content=error,
                )
                tool_calls.append(
                    ToolCall(
                        id=tm.tool_call_id,
                        name=tm.name,  # type: ignore
                        args={},
                    )
                )
                messages.append(tm)

        # TODO content with details similar as in MCP Server?
        ai = AIMessage(
            content=f"Successfully generated {len(results)} UI components. Failed: {len(errors)}",
            name=f"ngui_{component_system}",
            id=uuid.uuid4().hex,
            tool_calls=tool_calls,
        )
        messages.append(ai)

        return {
            "messages": messages,
            "renditions": results,
            "ui_blocks": ui_blocks,
            "errors": errors,
        }

    @staticmethod
    def is_next_gen_ui_message(message: BaseMessage):
        """Return True if the message is generated by NextGenUILangGraphAgent and reports successful processing,
        otherwise False."""
        if not message.name:
            return False
        return message.name.startswith("ngui_") and not message.name.startswith(
            "ngui_error_"
        )

    @staticmethod
    def is_next_gen_ui_error_message(message: BaseMessage):
        """Return True if the message is generated by NextGenUILangGraphAgent and reports error from the processing,
        otherwise False."""
        if not message.name:
            return False
        return message.name.startswith("ngui_error_")

    def build_graph(self):
        """Build NextGenUI Agent as Langgraph graph."""
        builder = StateGraph(
            state_schema=AgentState,
            config_schema=GraphConfig,
            input=AgentInputState,
            output=AgentOutputState,
        )

        builder.add_node("component_selection", self.component_selection)
        builder.add_node("data_transformation", self.data_transformation)
        builder.add_node("data_selection", self.data_selection)
        builder.add_node("component_system", self.choose_system)
        builder.add_node("design_system_handler", self.design_system_handler)

        builder.add_edge(START, "data_selection")
        builder.add_edge("data_selection", "component_selection")
        builder.add_edge("component_selection", "data_transformation")
        builder.add_edge("data_transformation", "component_system")
        builder.add_edge("design_system_handler", END)

        graph = builder.compile()
        return graph
