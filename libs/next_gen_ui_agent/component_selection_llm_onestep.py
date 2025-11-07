import logging
from typing import Any

from next_gen_ui_agent.component_descriptions import get_ui_components_description
from next_gen_ui_agent.component_selection_chart_instructions import CHART_INSTRUCTIONS
from next_gen_ui_agent.component_selection_prompts import (
    ONESTEP_BASE_INSTRUCTIONS,
    ONESTEP_RESPONSE_EXAMPLES,
)
from next_gen_ui_agent.component_selection_llm_strategy import (
    ComponentSelectionStrategy,
    trim_to_json,
)
from next_gen_ui_agent.model import InferenceBase
from next_gen_ui_agent.types import UIComponentMetadata
from pydantic_core import from_json

logger = logging.getLogger(__name__)


class OnestepLLMCallComponentSelectionStrategy(ComponentSelectionStrategy):
    """Component selection strategy using one LLM inference call for both component selection and configuration."""

    def __init__(
        self,
        unsupported_components: bool = False,
        input_data_json_wrapping: bool = True,
    ):
        """
        Component selection strategy using one LLM inference call for both component selection and configuration.

        Args:
            unsupported_components: if True, generate all UI components, otherwise generate only supported UI components
            input_data_json_wrapping: if True, wrap the JSON input data into data type field if necessary due to its structure
        """
        super().__init__(logger, input_data_json_wrapping)
        self.unsupported_components = unsupported_components

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
            # logger.debug(user_prompt)
            # logger.debug(input_data)

        sys_msg_content = ONESTEP_BASE_INSTRUCTIONS
        sys_msg_content += f"\n\nSelect from these UI components: {get_ui_components_description(self.unsupported_components)}\n\n"
        sys_msg_content += CHART_INSTRUCTIONS
        sys_msg_content += "\n" + ONESTEP_RESPONSE_EXAMPLES

        prompt = f"""=== User query ===
    {user_prompt}

    === Data ===
    {str(json_data)}
        """

        logger.debug("LLM system message:\n%s", sys_msg_content)
        logger.debug("LLM prompt:\n%s", prompt)

        response = trim_to_json(await inference.call_model(sys_msg_content, prompt))
        logger.debug("Component metadata LLM response: %s", response)

        return [response]

    def parse_infernce_output(
        self, inference_output: list[str], input_data_id: str
    ) -> UIComponentMetadata:
        """Parse inference output and return UIComponentMetadata or throw exception if inference output is invalid."""

        # Correct common LLM mistakes with component names (e.g., "bar-chart" -> "chart" with chartType)
        from next_gen_ui_agent.component_selection_llm_strategy import (
            correct_chart_component_name,
        )
        
        output_str = correct_chart_component_name(inference_output[0])
        
        # allow values coercing by `strict=False`
        # allow partial json parsing by `allow_partial=True`, validation will fail on missing fields then. See https://docs.pydantic.dev/latest/concepts/json/#partial-json-parsing
        try:
            result: UIComponentMetadata = UIComponentMetadata.model_validate(
                from_json(output_str, allow_partial=True), strict=False
            )
            result.id = input_data_id
            return result
        except Exception as e:
            print(f"[ComponentSelection] ERROR parsing LLM output: {e}")
            print("[ComponentSelection] Full output:")
            print(output_str)
            raise
