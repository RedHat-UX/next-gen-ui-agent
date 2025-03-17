import logging

from llama_stack_client import LlamaStackClient
from llama_stack_client.types.agents.turn import Step
from next_gen_ui_agent import AgentInput, InputData, NextGenUIAgent
from next_gen_ui_llama_stack.llama_stack_inference import LlamaStackAgentInference


class NextGenUILlamaStackAgent:
    """Next Gen UI Agen as Llama stack agen."""

    def __init__(self, client: LlamaStackClient, model: str):
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

    async def turn_from_steps(self, user_prompt, steps: list[Step]):
        tool_data_list = self._data_selection(steps)
        components = await self._component_selection(user_prompt, tool_data_list)
        components = self.ngui_agent.data_transformation(
            input_data=tool_data_list, components=components
        )
        logging.debug("tool_data_list: %s", tool_data_list)
        logging.debug("components: %s", components)
        # TODO: Create turns and support Streaming of those turns. Same way as llama-stack client
        return components
