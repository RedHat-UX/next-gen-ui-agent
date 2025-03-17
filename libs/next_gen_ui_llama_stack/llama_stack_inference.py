import logging
from typing import Iterator

from llama_stack_client import LlamaStackClient
from llama_stack_client.lib.agents.agent import Agent
from llama_stack_client.types.agents.turn import Turn
from llama_stack_client.types.shared import UserMessage
from next_gen_ui_agent.model import InferenceBase


class LlamaStackAgentInference(InferenceBase):
    """Class wrapping Langchain langchain_core.language_models.BaseChatModel
    class."""

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
            logging.debug("Inputs: %s", response.input_messages)
            logging.debug("Output: %s", response.output_message.content)
            logging.debug("Steps: %s", response.steps)
            result = response.output_message.content
            if isinstance(result, str):
                return result
            return str(result)
        if isinstance(response, Iterator):
            # Should not happen because of `stream=False`
            raise NotImplementedError("stream=False set on agent.create_turn")
