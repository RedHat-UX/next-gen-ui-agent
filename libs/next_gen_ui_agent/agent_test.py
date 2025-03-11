# import pytest

from . import NextGenUIAgent


def test_say_hello() -> None:
    agent = NextGenUIAgent()
    assert agent.say_hello() == "next_gen_ui_agent"
