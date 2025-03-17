from typing import Literal, Optional, TypedDict

from langchain_core.language_models import BaseChatModel
from langchain_core.runnables.config import RunnableConfig
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.types import Command
from next_gen_ui_agent import AgentInput, InputData, NextGenUIAgent
from next_gen_ui_agent.model import LangChainModelInference

ngui_agent = NextGenUIAgent()


class DataPath(TypedDict):
    name: str
    data_path: str
    data: list[str]


class BackendData(TypedDict):
    id: str
    data: str


class UIComponent(TypedDict):
    id: str
    title: str
    component: str
    fields: list[DataPath]


# Graph State Schema
class AgentState(MessagesState):
    backend_data: list[BackendData]
    user_prompt: str
    components: list[UIComponent]


class AgentInputState(MessagesState):
    backend_data: list[BackendData]
    user_prompt: str


class AgentOutputState(MessagesState):
    components: list[UIComponent]


# Graph Config Schema
class AgentConfig(TypedDict):
    model: Optional[str]
    model_api_base_url: Optional[str]
    model_api_token: Optional[str]
    component_system: Literal["none", "patternfly", "rhds"]


class NextGenUILangGraphAgent:
    """Next Gen UI Agent in LangGraph."""

    def __init__(self, model: BaseChatModel):
        super().__init__()
        self.inference = LangChainModelInference(model)

    # Nodes
    async def data_selection(self, state: AgentInputState, config: RunnableConfig):
        print("\n\n---CALL data_selection---")
        backend_data = state.get("backend_data", [])
        user_prompt = state.get("user_prompt", "")

        if user_prompt and len(backend_data) > 0:
            print("User_prompt and backend_data taken from state directly")
            return

        messages = state["messages"]
        # print(messages)

        messagesReversed = list(reversed(messages))
        for m in messagesReversed:
            # print(m.content)
            # TODO: Handle better success/error messages
            if (
                m.type
                == "tool"
                # and (m.status and m.status == "success")
                # and (m.name and not m.name.startswith("genie"))
            ):
                # TODO: Handle m.content as list and remove type: ignore
                backend_data.append({"id": m.tool_call_id, "data": m.content})  # type: ignore
            if m.type == "human" and not user_prompt:
                user_prompt = m.content  # type: ignore
            if user_prompt != "" and len(backend_data) > 0:
                break

        print(
            f"User_prompt and backend_data taken HumanMessage and ToolMessages. count={len(backend_data)}"
        )
        return {
            "backend_data": backend_data,
            "user_prompt": user_prompt,
        }

    async def component_selection(self, state: AgentState, config: RunnableConfig):
        print("\n\n---CALL component_selection---")

        user_prompt = state["user_prompt"]
        input_data = [
            InputData(id=d["id"], data=d["data"]) for d in state["backend_data"]
        ]
        input = AgentInput(user_prompt=user_prompt, input_data=input_data)
        components = await ngui_agent.component_selection(
            inference=self.inference,
            input=input,
        )
        # TODO: TypeDict or Data Class ???
        return {"components": components}

    async def choose_system(
        self, state: AgentState, config: RunnableConfig
    ) -> Command[Literal["design_system_handler", "__end__"]]:
        print("\n\n---CALL component_generation---")
        cfg: AgentConfig = config.get("configurable", {})  # type: ignore

        # TODO: Resolve TypeDict vs Data class first. Then you can call the data_transformation
        # input_data = [
        #     InputData(id=d["id"], data=d["data"]) for d in state["backend_data"]
        # ]
        # components = state["components"]
        # ngui_agent.data_transformation(input_data=input_data, components=components)

        component_system = cfg.get("component_system", "rhds")
        if component_system and component_system != "none":
            return Command(goto="design_system_handler")

        return Command(goto=END)

    def design_system_handler(self, state: AgentState, config: RunnableConfig):
        print("\n\n---CALL design_system_handler---")
        # TODO design_system_handler

    def build_graph(self):
        """Build NextGenUI Agent as Langgraph graph."""
        builder = StateGraph(
            state_schema=AgentState,
            config_schema=AgentConfig,
            input=AgentInputState,
            output=AgentOutputState,
        )

        builder.add_node("component_selection", self.component_selection)
        builder.add_node("data_selection", self.data_selection)
        builder.add_node("component_system", self.choose_system)
        builder.add_node("design_system_handler", self.design_system_handler)

        builder.add_edge(START, "data_selection")
        builder.add_edge("data_selection", "component_selection")
        builder.add_edge("component_selection", "component_system")
        builder.add_edge("design_system_handler", END)

        graph = builder.compile()
        return graph
