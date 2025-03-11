# import pytest

from . import NextGenUILangGraphAgent


def test_say_hello() -> None:
    agent = NextGenUILangGraphAgent()
    assert agent.say_hello() == "langgraph"
