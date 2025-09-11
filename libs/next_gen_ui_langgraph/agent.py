import logging
import uuid
from typing import Literal, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langchain_core.runnables.config import RunnableConfig
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.types import Command
from next_gen_ui_agent import AgentInput, InputData, NextGenUIAgent, UIComponentMetadata
from next_gen_ui_agent.data_transform.types import ComponentDataBase
from next_gen_ui_agent.model import LangChainModelInference
from next_gen_ui_agent.types import AgentConfig, Rendition
from typing_extensions import TypedDict

logger = logging.getLogger(__name__)


# Graph State Schema
class AgentState(MessagesState):
    backend_data: list[InputData]
    user_prompt: str
    components: list[UIComponentMetadata]
    components_data: list[ComponentDataBase]
    renditions: list[Rendition]


class AgentInputState(MessagesState):
    backend_data: list[InputData]
    user_prompt: str


class AgentOutputState(MessagesState):
    components: list[UIComponentMetadata]
    components_data: list[ComponentDataBase]
    renditions: list[Rendition]


# Graph Config Schema
class GraphConfig(TypedDict):
    model: Optional[str]
    model_api_base_url: Optional[str]
    model_api_token: Optional[str]
    component_system: Literal["none", "patternfly", "rhds", "json"]


class NextGenUILangGraphAgent:
    """Next Gen UI Agent in LangGraph."""

    def __init__(self, model: BaseChatModel, config: Optional[AgentConfig] = None):
        """Initialize Next Gen UI Agent in LangGraph. Inference is created from model if not provided in config."""
        super().__init__()
        config = config if config else AgentConfig()
        if "inference" not in config:
            inference = LangChainModelInference(model)
            config["inference"] = inference

        self.ngui_agent = NextGenUIAgent(config=config)

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
                backend_data.append({"id": m.tool_call_id, "data": m.content, "type": m.name})  # type: ignore
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
        input_data = [
            InputData(id=d["id"], data=d["data"], type=d.get("type"))
            for d in state["backend_data"]
        ]
        input = AgentInput(user_prompt=user_prompt, input_data=input_data)
        components = await self.ngui_agent.component_selection(input=input)
        return {"components": components}

    def data_transformation(self, state: AgentState, config: RunnableConfig):
        components = state["components"]
        input_data = [
            InputData(id=d["id"], data=d["data"], type=d.get("type"))
            for d in state["backend_data"]
        ]

        data = self.ngui_agent.data_transformation(
            input_data=input_data, components=components
        )
        return {"components_data": data}

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

        results = self.ngui_agent.design_system_handler(
            state["components_data"], component_system
        )

        messages: list[BaseMessage] = []
        for result in results:
            logger.debug(
                "---CALL %s--- id: %s, component rendition: %s",
                component_system,
                result.id,
                result.content,
            )

            tm = ToolMessage(
                name=f"ngui_{component_system}",
                tool_call_id=str(result.id) + uuid.uuid4().hex,
                content=str(result.content),
            )
            ai = AIMessage(
                content="", name=f"ngui_{component_system}", id=uuid.uuid4().hex
            )
            ai.tool_calls.append(
                {"id": tm.tool_call_id, "name": f"ngui_{component_system}", "args": {}}
            )
            messages.append(ai)
            messages.append(tm)
        return {"messages": messages, "renditions": results}

    @staticmethod
    def is_next_gen_ui_message(message: BaseMessage):
        """Return True if the message is generated by NextGenUILangGraphAgent,
        otherwise False."""
        if not message.name:
            return False
        return message.name.startswith("ngui_")

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
