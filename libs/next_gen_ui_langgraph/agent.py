from langgraph.graph import StateGraph, START, END
from langchain_core.runnables.config import RunnableConfig
from langchain_core.language_models import BaseChatModel
from next_gen_ui_agent import NextGenUIAgent, AgentInput, InputData
from next_gen_ui_agent.model import LangChainModelInference
from .graph_config import AgentState, AgentConfig, AgentInputState, AgentOutputState
import httpx
import os

ngui_agent = NextGenUIAgent()


class NextGenUILangGraphAgent:
    """Next Gen UI Agent in LangGraph."""

    def __init__(self, model: BaseChatModel):
        super().__init__()
        self.inference = LangChainModelInference(model)

    ### Nodes
    async def data_selection(
        self, state: AgentInputState, config: RunnableConfig
    ) -> AgentState:
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
                m.type == "tool"
                and m.status == "success"
                and not m.name.startswith("genie")
            ):
                backend_data.append({"id": m.tool_call_id, "data": m.content})
            if m.type == "human" and not user_prompt:
                user_prompt = m.content
            if user_prompt != "" and len(backend_data) > 0:
                break

        print(
            f"User_prompt and backend_data taken HumanMessage and ToolMessages. count={len(backend_data)}"
        )
        return {
            "backend_data": backend_data,
            "user_prompt": user_prompt,
        }

    async def component_selection(
        self, state: AgentState, config: RunnableConfig
    ) -> AgentState:
        print("\n\n---CALL component_selection---")

        user_prompt = state["user_prompt"]
        input_data = [InputData(id=d["id"], data=d["data"]) for d in state["backend_data"]]
        input = AgentInput(user_prompt=user_prompt, input_data=input_data)
        components = await ngui_agent.component_selection(
            inference=self.inference,
            input=input,
        )
        return {"components": components}

    def build_graph(self):
        ### Graph
        builder = StateGraph(
            state_schema=AgentState,
            config_schema=AgentConfig,
            input=AgentInputState,
            output=AgentOutputState,
        )

        builder.add_node("component_selection", self.component_selection)
        builder.add_node("data_selection", self.data_selection)
        # builder.add_node("component_system", choose_system)
        # builder.add_node("design_system_handler", design_system_handler)

        builder.add_edge(START, "data_selection")
        builder.add_edge("data_selection", "component_selection")
        builder.add_edge("component_selection", END)
        # builder.add_edge("component_selection", "component_system")
        # builder.add_edge("design_system_handler", END)

        graph = builder.compile()
        return graph
