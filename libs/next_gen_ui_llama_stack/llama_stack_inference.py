import logging

from llama_stack_client import AsyncLlamaStackClient, LlamaStackClient
from llama_stack_client.types.shared import SystemMessage, UserMessage
from llama_stack_client.types.shared.chat_completion_response import (
    ChatCompletionResponse,
)
from llama_stack_client.types.shared.sampling_params import (
    SamplingParams,
    StrategyGreedySamplingStrategy,
)
from next_gen_ui_agent.model import InferenceBase

logger = logging.getLogger(__name__)

# greedy sampling always select the most probable next word, it should also be the fastest sampling method
LLM_SAMPLING_STRATEGY = StrategyGreedySamplingStrategy(type="greedy")


def process_response(response, input_messages) -> str:
    """Helper method to process response of the client.inference.chat_completion in both agents - validate response type, log inputs and output, return content string"""

    if isinstance(response, ChatCompletionResponse):
        result = response.completion_message.content

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("UI Agent LLM Inputs: %s", input_messages)
            logger.debug("UI Agent LLM Output: %s", result)

        if isinstance(result, str):
            return result
        return str(result)
    else:
        # Should not happen because of `stream=False`, but just to be sure
        raise NotImplementedError(
            "Set stream=False on client.inference.chat_completion!"
        )


class LlamaStackAgentInference(InferenceBase):
    """Class wrapping llama_stack LlamaStackClient.inference"""

    def __init__(self, client: LlamaStackClient, model: str):
        super().__init__()
        self.model = model
        self.client = client

    async def call_model(self, system_msg: str, prompt: str) -> str:
        input_messages = [
            SystemMessage(role="system", content=system_msg),
            UserMessage(role="user", content=prompt),
        ]

        response = self.client.inference.chat_completion(
            model_id=self.model,
            messages=input_messages,
            stream=False,
            sampling_params=SamplingParams(strategy=LLM_SAMPLING_STRATEGY),
        )  # type: ignore

        return process_response(response, input_messages)


class LlamaStackAsyncAgentInference(InferenceBase):
    """Class wrapping llama_stack AsyncLlamaStackClient.inference"""

    def __init__(self, client: AsyncLlamaStackClient, model: str):
        super().__init__()
        self.model = model
        self.client = client

    async def call_model(self, system_msg: str, prompt: str) -> str:
        input_messages = [
            SystemMessage(role="system", content=system_msg),
            UserMessage(role="user", content=prompt),
        ]

        response = await self.client.inference.chat_completion(
            model_id=self.model,
            messages=input_messages,
            stream=False,
            sampling_params=SamplingParams(strategy=LLM_SAMPLING_STRATEGY),
        )  # type: ignore

        return process_response(response, input_messages)
