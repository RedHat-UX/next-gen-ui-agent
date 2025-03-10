from next_gen_ui_agent.agent import NextGenUIAgent

from langgraph.graph import StateGraph, MessagesState, START, END

workflow = StateGraph(MessagesState)

class NextGenUILangGraphAgent:
    """Next Gen UI Agent in LangGraph"""

    def say_hello(self) -> str:
        print("Hallo from LangGraph")

        agent = NextGenUIAgent()
        agent.say_hello()

        return "langgraph"


if __name__ == "__main__":
    agent = NextGenUILangGraphAgent()
    agent.say_hello()
