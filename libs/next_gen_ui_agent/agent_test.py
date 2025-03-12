import pytest

from . import NextGenUIAgent


def test_say_hello() -> None:
    agent = NextGenUIAgent()
    assert agent.say_hello() == "next_gen_ui_agent"


@pytest.mark.asyncio
async def test_async_say_hello() -> None:
    agent = NextGenUIAgent()
    assert await agent.say_hello_async() == "next_gen_ui_agent_async"
