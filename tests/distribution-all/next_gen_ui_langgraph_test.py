from next_gen_ui_langgraph import NextGenUILangGraphAgent
from langchain_core.language_models import FakeMessagesListChatModel


def test_next_gen_ui_langgraph() -> None:
    response = "{}"
    msg = {"type": "assistant", "content": response}
    llm = FakeMessagesListChatModel(responses=[msg])

    agent = NextGenUILangGraphAgent(model=llm)

    agent.build_graph()
