import logging
from typing import AsyncIterator, Optional

from llama_stack_client import LlamaStackClient
from llama_stack_client.types.agents.turn import Step
from next_gen_ui_agent import AgentInput, InputData, NextGenUIAgent
from next_gen_ui_agent.model import InferenceBase
from next_gen_ui_llama_stack.llama_stack_inference import LlamaStackAgentInference
from next_gen_ui_llama_stack.types import ResponseEvent


class NextGenUILlamaStackAgent:
    """Next Gen UI Agen as Llama stack agen."""

    def __init__(
        self,
        client: LlamaStackClient,
        model: str,
        inference: Optional[InferenceBase] = None,
    ):
        if inference:
            self.inference = inference
        else:
            self.inference = LlamaStackAgentInference(client, model)

        self.client = client
        self.ngui_agent = NextGenUIAgent()

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
        components = await self.ngui_agent.component_selection(
            inference=self.inference,
            input=input,
        )
        return components

    async def create_turn(
        self, user_prompt, steps: list[Step]
    ) -> AsyncIterator[ResponseEvent]:
        logging.debug("create_turn. user_prompt: %s", user_prompt)
        tool_data_list = self._data_selection(steps)
        components = await self._component_selection(user_prompt, tool_data_list)
        yield ResponseEvent(event_type="component_metadata", payload=components)

        components = self.ngui_agent.data_transformation(
            input_data=tool_data_list, components=components
        )
        yield ResponseEvent(event_type="output_json", payload=components)
