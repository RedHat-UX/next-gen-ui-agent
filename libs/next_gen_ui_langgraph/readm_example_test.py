import pytest


def test_code() -> None:
    # Just import the example but not execute it
    from next_gen_ui_langgraph.readme_example import llm, run  # noqa: F401


@pytest.mark.skip(reason="Mock LLM to run whole example")
def test_run() -> None:
    from next_gen_ui_langgraph.readme_example import run

    # Example: https://github.com/langchain-ai/langchain/blob/master/libs/partners/openai/tests/unit_tests/chat_models/test_base.py#L523
    run()
