import logging
from typing import AsyncIterator, Optional

from llama_stack_client import AsyncLlamaStackClient, LlamaStackClient
from llama_stack_client.types.agents.turn import Step
from next_gen_ui_agent import AgentInput, InputData, NextGenUIAgent
from next_gen_ui_agent.model import InferenceBase
from next_gen_ui_agent.types import AgentConfig
from next_gen_ui_llama_stack.llama_stack_inference import (
    LlamaStackAgentInference,
    LlamaStackAsyncAgentInference,
)
from next_gen_ui_llama_stack.types import ResponseEvent

logger = logging.getLogger(__name__)


class NextGenUILlamaStackAgent:
    """Next Gen UI Agen as Llama stack agen."""

    def __init__(
        self,
        client: LlamaStackClient | AsyncLlamaStackClient,
        model: str,
        inference: Optional[InferenceBase] = None,
    ):
        if not inference:
            if isinstance(client, LlamaStackClient):
                inference = LlamaStackAgentInference(client, model)
            else:
                inference = LlamaStackAsyncAgentInference(client, model)

        self.client = client
        self.ngui_agent = NextGenUIAgent(AgentConfig(inference=inference))

    def _data_selection(self, steps: list[Step]) -> list[InputData]:
        """Get data from all tool messages."""
        data = []
        for s in steps:
            if not s.step_type == "tool_execution":
                continue
            for r in s.tool_responses:
                d = InputData(id=r.call_id, data=str(r.content))
                data.append(d)

        return data

    async def _component_selection(self, user_prompt, input_data: list[InputData]):
        input = AgentInput(user_prompt=user_prompt, input_data=input_data)
        components = await self.ngui_agent.component_selection(input=input)
        return components

    async def create_turn(
        self, user_prompt, steps: list[Step], component_system: Optional[str] = None
    ) -> AsyncIterator[ResponseEvent]:
        logger.debug("create_turn. user_prompt: %s", user_prompt)
        tool_data_list = self._data_selection(steps)
        components = await self._component_selection(user_prompt, tool_data_list)
        yield ResponseEvent(event_type="component_metadata", payload=components)

        components_data = self.ngui_agent.data_transformation(
            input_data=tool_data_list, components=components
        )
        renditions = self.ngui_agent.design_system_handler(
            components=components_data, component_system=component_system
        )
        yield ResponseEvent(event_type="rendering", payload=renditions)
