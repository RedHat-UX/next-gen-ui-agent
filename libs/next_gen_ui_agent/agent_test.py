import pytest

from . import NextGenUIAgent


@pytest.mark.asyncio
async def test_async_say_hello() -> None:
    NextGenUIAgent()
    # assert await agent.say_hello_async() == "next_gen_ui_agent_async"
