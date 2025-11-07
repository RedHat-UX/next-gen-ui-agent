import logging
from typing import Any

from next_gen_ui_agent.component_descriptions import get_ui_components_description
from next_gen_ui_agent.component_selection_chart_instructions import CHART_INSTRUCTIONS
from next_gen_ui_agent.component_selection_prompts import (
    COMPONENT_SELECTION_BASE_INSTRUCTIONS,
    COMPONENT_SELECTION_EXAMPLES,
    FIELD_SELECTION_BASE_INSTRUCTIONS,
    get_component_extension,
    get_component_examples,
)
from next_gen_ui_agent.component_selection_llm_strategy import (
    ComponentSelectionStrategy,
    trim_to_json,
)
from next_gen_ui_agent.model import InferenceBase
from next_gen_ui_agent.types import UIComponentMetadata
from pydantic_core import from_json

logger = logging.getLogger(__name__)


class TwostepLLMCallComponentSelectionStrategy(ComponentSelectionStrategy):
    """Component selection strategy using two LLM inference calls, one for component selection and one for its configuration."""

    def __init__(
        self,
        unsupported_components: bool,
        select_component_only: bool = False,
        input_data_json_wrapping: bool = True,
    ):
        """
        Component selection strategy using two LLM inference calls, one for component selection and one for its configuration.

        Args:
            unsupported_components: if True, generate all UI components, otherwise generate only supported UI components
            select_component_only: if True, only generate the component, it is not necesary to generate it's configuration
            input_data_json_wrapping: if True, wrap the JSON input data into data type field if necessary due to its structure
        """
        super().__init__(logger, input_data_json_wrapping)
        self.unsupported_components = unsupported_components
        self.select_component_only = select_component_only

    def parse_infernce_output(
        self, inference_output: list[str], input_data_id: str
    ) -> UIComponentMetadata:
        """Parse inference output and return UIComponentMetadata or throw exception if inference output is invalid."""

        # Correct common LLM mistakes with component names (e.g., "bar-chart" -> "chart" with chartType)
        from next_gen_ui_agent.component_selection_llm_strategy import (
            correct_chart_component_name,
        )
        
        component_str = correct_chart_component_name(inference_output[0])
        
        # allow values coercing by `strict=False`
        # allow partial json parsing by `allow_partial=True`, validation will fail on missing fields then. See https://docs.pydantic.dev/latest/concepts/json/#partial-json-parsing
        part = from_json(component_str, allow_partial=True)

        # parse fields if they are available
        if len(inference_output) > 1:
            part["fields"] = from_json(inference_output[1], allow_partial=True)
        else:
            part["fields"] = []

        result: UIComponentMetadata = UIComponentMetadata.model_validate(
            part, strict=False
        )
        result.id = input_data_id
        return result

    async def perform_inference(
        self,
        inference: InferenceBase,
        user_prompt: str,
        json_data: Any,
        input_data_id: str,
    ) -> list[str]:
        """Run Component Selection inference."""

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "---CALL component_selection_inference--- id: %s", {input_data_id}
            )

        data_for_llm = str(json_data)

        response_1 = trim_to_json(
            await self.inference_step_1(inference, user_prompt, data_for_llm)
        )

        if self.select_component_only:
            return [response_1]

        response_2 = trim_to_json(
            await self.inference_step_2(
                inference, response_1, user_prompt, data_for_llm
            )
        )

        return [response_1, response_2]

    async def inference_step_1(self, inference, user_prompt, json_data_for_llm: str):
        """Run Component Selection inference."""

        sys_msg_content = COMPONENT_SELECTION_BASE_INSTRUCTIONS
        sys_msg_content += f"\n\nSelect from these UI components: {get_ui_components_description(self.unsupported_components)}\n\n"
        sys_msg_content += CHART_INSTRUCTIONS
        sys_msg_content += "\n" + COMPONENT_SELECTION_EXAMPLES

        prompt = f"""=== User query ===
{user_prompt}
=== Data ===
{json_data_for_llm}
"""

        logger.debug("LLM component selection system message:\n%s", sys_msg_content)
        logger.debug("LLM component selection prompt:\n%s", prompt)

        response = await inference.call_model(sys_msg_content, prompt)
        logger.debug("Component selection LLM response: %s", response)
        return response

    async def inference_step_2(
        self,
        inference,
        component_selection_response,
        user_prompt,
        json_data_for_llm: str,
    ):
        component = from_json(component_selection_response, allow_partial=True)[
            "component"
        ]

        """Run Component Configuration inference."""

        sys_msg_content = FIELD_SELECTION_BASE_INSTRUCTIONS.format(
            component=component,
        )
        sys_msg_content += "\n" + get_component_extension(component)
        sys_msg_content += "\n" + get_component_examples(component)

        prompt = f"""=== User query ===
{user_prompt}

=== Data ===
{json_data_for_llm}
"""

        logger.debug("LLM component configuration system message:\n%s", sys_msg_content)
        logger.debug("LLM component configuration prompt:\n%s", prompt)

        response = await inference.call_model(sys_msg_content, prompt)
        logger.debug("Component configuration LLM response: %s", response)
        return response
