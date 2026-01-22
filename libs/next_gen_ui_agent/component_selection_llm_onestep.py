import logging
from typing import Any

from next_gen_ui_agent.component_metadata import get_component_metadata
from next_gen_ui_agent.component_selection_common import (
    CHART_COMPONENTS,
    ONESTEP_PROMPT_RULES,
    build_chart_instructions,
    build_components_description,
    build_onestep_examples,
    normalize_allowed_components,
    set_active_component_metadata,
)
from next_gen_ui_agent.component_selection_llm_strategy import (
    ComponentSelectionStrategy,
    InferenceResult,
    LLMInteraction,
    trim_to_json,
    validate_and_correct_chart_type,
)
from next_gen_ui_agent.inference.inference_base import InferenceBase
from next_gen_ui_agent.types import (
    CONFIG_OPTIONS_ALL_COMPONETS,
    AgentConfig,
    UIComponentMetadata,
)
from pydantic_core import from_json

logger = logging.getLogger(__name__)


class OnestepLLMCallComponentSelectionStrategy(ComponentSelectionStrategy):
    """Component selection strategy using one LLM inference call for both component selection and configuration."""

    def __init__(
        self,
        config: AgentConfig,
    ):
        """
        Component selection strategy using one LLM inference call for both component selection and configuration.

        Args:
            config: AgentConfig to get selectable components and input data json wrapping configuration from
        """
        super().__init__(logger, config)

        # Get merged metadata with overrides and set it globally
        merged_metadata = get_component_metadata(config)
        set_active_component_metadata(merged_metadata)

        self._system_prompt = self._build_system_prompt(config.selectable_components)

    def get_system_prompt(self) -> str:
        """
        Get the system prompt for the component selection strategy.
        """
        return self._system_prompt

    def _build_system_prompt(
        self, allowed_components_config: CONFIG_OPTIONS_ALL_COMPONETS
    ) -> str:
        """
        Build complete system prompt based on allowed components.

        Args:
            allowed_components_config: Set of allowed component names, or None for all components

        Returns:
            Complete system prompt string
        """

        allowed_components = normalize_allowed_components(allowed_components_config)

        # Get filtered component descriptions
        components_description = build_components_description(allowed_components)

        # Get filtered examples
        response_examples = build_onestep_examples(allowed_components)

        # Detect chart components in allowed set
        allowed_charts = allowed_components & CHART_COMPONENTS

        # Get chart instructions (empty if no charts)
        chart_instructions = build_chart_instructions(allowed_charts)

        # Build the complete system prompt
        system_prompt = f"""You are a UI design assistant. Select the best UI component to visualize the Data based on User query.

{ONESTEP_PROMPT_RULES}

AVAILABLE UI COMPONENTS:
{components_description}

{chart_instructions}"""

        # Add examples if available
        if response_examples:
            system_prompt += f"""

{response_examples}"""

        return system_prompt

    async def perform_inference(
        self,
        inference: InferenceBase,
        user_prompt: str,
        json_data: Any,
        input_data_id: str,
    ) -> InferenceResult:
        """Run Component Selection inference."""

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "---CALL component_selection_inference--- id: %s", {input_data_id}
            )
            # logger.debug(user_prompt)
            # logger.debug(input_data)

        # Use pre-constructed system prompt
        sys_msg_content = self._system_prompt

        prompt = f"""=== User query ===
    {user_prompt}

    === Data ===
    {str(json_data)}
        """

        logger.debug("LLM system message:\n%s", sys_msg_content)
        logger.debug("LLM prompt:\n%s", prompt)

        raw_response = await inference.call_model(sys_msg_content, prompt)
        response = trim_to_json(raw_response)
        logger.debug("Component metadata LLM response: %s", response)

        # Return result with LLM interaction metadata
        return InferenceResult(
            outputs=[response],
            llm_interactions=[
                LLMInteraction(
                    step="component_selection",
                    system_prompt=sys_msg_content,
                    user_prompt=prompt,
                    raw_response=raw_response,
                )
            ],
        )

    def parse_infernce_output(
        self, inference_result: InferenceResult, input_data_id: str
    ) -> UIComponentMetadata:
        """Parse inference output and return UIComponentMetadata or throw exception if inference output is invalid."""

        # allow values coercing by `strict=False`
        # allow partial json parsing by `allow_partial=True`, validation will fail on missing fields then. See https://docs.pydantic.dev/latest/concepts/json/#partial-json-parsing
        result: UIComponentMetadata = UIComponentMetadata.model_validate(
            from_json(inference_result["outputs"][0], allow_partial=True), strict=False
        )
        result.id = input_data_id

        # Attach LLM interactions from result (convert TypedDict instances to plain dicts for Pydantic)
        result.llm_interactions = [
            dict(li) for li in inference_result["llm_interactions"]
        ]

        # Post-processing: Validate chart type matches reasoning
        validate_and_correct_chart_type(result, logger)

        # Log component selection reasoning
        logger.info(
            "[NGUI] Component selection reasoning:\n"
            "  Component: %s\n"
            "  Reason: %s\n"
            "  Confidence: %s",
            result.component,
            result.reasonForTheComponentSelection,
            result.confidenceScore,
        )

        return result
