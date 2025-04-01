import logging
from typing import AsyncIterator, Iterator

from llama_stack_client import AsyncLlamaStackClient, LlamaStackClient
from llama_stack_client.lib.agents.agent import Agent, AsyncAgent
from llama_stack_client.types.agents.turn import Turn
from llama_stack_client.types.shared import UserMessage
from next_gen_ui_agent.model import InferenceBase

logger = logging.getLogger(__name__)


class LlamaStackAgentInference(InferenceBase):
    """Class wrapping llama_stack_client.lib.agents.agent.Agent."""

    def __init__(self, client: LlamaStackClient, model: str):
        super().__init__()
        self.model = model
        self.client = client

    async def call_model(self, system_msg: str, prompt: str) -> str:
        agent = Agent(
            client=self.client,
            model=self.model,
            instructions=system_msg,
            enable_session_persistence=False,
        )
        # Create a session
        session_id = agent.create_session(session_name="ngui")
        # Non-streaming API
        response = agent.create_turn(
            session_id=session_id,
            messages=[UserMessage(content=prompt, role="user")],
            stream=False,
        )

        if isinstance(response, Turn):
            logger.debug("Inputs: %s", response.input_messages)
            logger.debug("Output: %s", response.output_message.content)
            logger.debug("Steps: %s", response.steps)
            result = response.output_message.content
            if isinstance(result, str):
                return result
            return str(result)
        if isinstance(response, Iterator):
            # Should not happen because of `stream=False`
            raise NotImplementedError("stream=False set on agent.create_turn")


class LlamaStackAsyncAgentInference(InferenceBase):
    """Class wrapping llama_stack_client.lib.agents.agent.AsyncAgent."""

    def __init__(self, client: AsyncLlamaStackClient, model: str):
        super().__init__()
        self.model = model
        self.client = client

    async def call_model(self, system_msg: str, prompt: str) -> str:
        agent = AsyncAgent(
            client=self.client,  # type: ignore
            model=self.model,
            instructions=system_msg,
            enable_session_persistence=False,
        )
        # Create a session
        session_id = await agent.create_session(session_name="ngui")
        # Non-streaming API
        response = await agent.create_turn(
            session_id=session_id,
            messages=[UserMessage(content=prompt, role="user")],
            stream=False,
        )

        if isinstance(response, Turn):
            logger.debug("Inputs: %s", response.input_messages)
            logger.debug("Output: %s", response.output_message.content)
            logger.debug("Steps: %s", response.steps)
            result = response.output_message.content
            if isinstance(result, str):
                return result
            return str(result)
        if isinstance(response, AsyncIterator):
            # Should not happen because of `stream=False`
            raise NotImplementedError("stream=False set on agent.create_turn")
