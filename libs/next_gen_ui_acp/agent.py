import logging

from acp_sdk.models import Artifact, Message
from next_gen_ui_agent.agent import NextGenUIAgent
from next_gen_ui_agent.model import InferenceBase
from next_gen_ui_agent.types import AgentConfig, AgentInput, InputData

logger = logging.getLogger(__name__)


class NextGenUIACPAgent:
    """Next Gen UI Agen as ACP agent."""

    def __init__(
        self,
        inference: InferenceBase,
        component_system: str,
    ):
        self.ngui_agent = NextGenUIAgent(config=AgentConfig(), inference=inference)
        self.component_system = component_system

    def data_selection(self, messages: list[Message]):
        """Get data from all tool messages."""
        input_data: list[InputData] = []
        user_prompt = ""

        messagesReversed = list(reversed(messages))
        for m in messagesReversed:
            part = m.parts[0]
            role = part.role  # type: ignore
            if role == "tool" or isinstance(part, Artifact):
                id = part.id  # type: ignore
                input_data.append({"id": id, "data": str(part.content)})
            if role == "user":
                user_prompt = str(part.content)

            if user_prompt != "" and len(input_data) > 0:
                break

        return (user_prompt, input_data)

    async def component_selection(self, user_prompt, input_data: list[InputData]):
        input = AgentInput(user_prompt=user_prompt, input_data=input_data)
        components = await self.ngui_agent.component_selection(input=input)
        return components

    async def run(self, input: list[Message]) -> list[Artifact]:
        (user_prompt, tool_data_list) = self.data_selection(input)
        components = await self.component_selection(user_prompt, tool_data_list)
        components_data = self.ngui_agent.data_transformation(
            input_data=tool_data_list, components=components
        )
        renditions = self.ngui_agent.design_system_handler(
            components=components_data, component_system=self.component_system
        )
        parts = [
            Artifact(
                content=rendition.content,
                name="rendering",
                role="tool",
                id=rendition.id,
            )  # type: ignore
            for rendition in renditions
        ]
        return parts
