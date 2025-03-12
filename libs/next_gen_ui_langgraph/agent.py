from langgraph.graph import MessagesState, StateGraph
from next_gen_ui_agent import NextGenUIAgent

workflow = StateGraph(MessagesState)

ngui_agent = NextGenUIAgent()


class NextGenUILangGraphAgent:
    """Next Gen UI Agent in LangGraph."""

    def say_hello(self) -> str:
        print("Hallo from LangGraph")

        return "langgraph"


if __name__ == "__main__":
    agent = NextGenUILangGraphAgent()
    agent.say_hello()
