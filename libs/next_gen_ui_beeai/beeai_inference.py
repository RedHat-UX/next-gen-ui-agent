import logging
from typing import Any

from beeai_framework.backend import (
    ChatModel,
    ChatModelOutput,
    ChatModelParameters,
    Message,
    SystemMessage,
    UserMessage,
)
from next_gen_ui_agent.model import InferenceBase

logger = logging.getLogger(__name__)


class BeeAIInference(InferenceBase):
    """Class wrapping BeeAI ChatModel"""

    def __init__(self, model: str):
        super().__init__()
        self.model = ChatModel.from_name(model, ChatModelParameters(temperature=0))

    async def call_model(self, system_msg: str, prompt: str) -> str:
        input_messages: list[Message[Any]] = [
            SystemMessage(content=system_msg),
            UserMessage(content=prompt),
        ]
        output: ChatModelOutput = await self.model.run(input_messages)
        response = output.get_text_content()
        return str(response)
