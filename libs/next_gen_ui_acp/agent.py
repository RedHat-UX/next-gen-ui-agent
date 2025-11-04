import asyncio
import logging
import uuid
from typing import AsyncIterator

from acp_sdk.models import Artifact, Message, TrajectoryMetadata
from next_gen_ui_agent.agent import NextGenUIAgent
from next_gen_ui_agent.model import InferenceBase
from next_gen_ui_agent.types import AgentConfig, InputData, UIBlock

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

    def _data_selection(self, messages: list[Message]):
        """Get data from all tool messages."""
        input_data: list[InputData] = []
        user_prompt = ""

        messagesReversed = list(reversed(messages))
        for m in messagesReversed:
            part = m.parts[0]
            if isinstance(part, Artifact) or (
                part.metadata and part.metadata.kind == "trajectory"
            ):
                id = str(uuid.uuid4())
                type = (
                    part.metadata.tool_name
                    if part.metadata and part.metadata.kind == "trajectory"
                    else None
                )
                input_data.append({"id": id, "data": str(part.content), "type": type})

            if m.role == "user":
                user_prompt = str(part.content)

            if user_prompt != "" and len(input_data) > 0:
                break

        return (user_prompt, input_data)

    async def _process_single_data(
        self, user_prompt: str, input_data: InputData
    ) -> Message:
        """Process a single input data and return a Message."""
        try:
            component = await self.ngui_agent.select_component(user_prompt, input_data)
            component_data = self.ngui_agent.transform_data(input_data, component)
            rendering = self.ngui_agent.generate_rendering(
                component_data, self.component_system
            )
            ui_block = UIBlock(
                id=rendering.id,
                rendering=rendering,
                configuration=self.ngui_agent.construct_UIBlockConfiguration(
                    input_data, component
                ),
            )
            return Message(
                role="agent",
                parts=[
                    Artifact(
                        content=ui_block.model_dump_json(),
                        content_type="application/json",
                        name="ui_block",
                        metadata=TrajectoryMetadata(tool_name="next_gen_ui_agent"),
                    )
                ],
            )
        except Exception as e:
            logger.exception("Error processing input data: %s", input_data)
            return Message(
                role="agent",
                parts=[
                    Artifact(
                        content=f"Error processing input data into UI component: {str(e)}",
                        content_type="text/plain",
                        name="error",
                        metadata=TrajectoryMetadata(tool_name="next_gen_ui_agent"),
                    )
                ],
            )

    async def run(self, input: list[Message]) -> AsyncIterator[Message]:
        """Process tool data in parallel and yield each output message independently."""
        (user_prompt, tool_data_list) = self._data_selection(input)

        # Create tasks for all input data processing in parallel
        tasks = [
            asyncio.create_task(self._process_single_data(user_prompt, input_data))
            for input_data in tool_data_list
        ]

        # Yield messages as they complete
        for coro in asyncio.as_completed(tasks):
            message = await coro
            yield message
