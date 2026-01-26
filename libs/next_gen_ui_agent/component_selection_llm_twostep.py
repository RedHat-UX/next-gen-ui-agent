import logging
from typing import Any, Optional, cast

from next_gen_ui_agent.component_metadata import get_component_metadata
from next_gen_ui_agent.component_selection_common import (
    CHART_COMPONENTS,
    TWOSTEP_STEP1_PROMPT_RULES,
    TWOSTEP_STEP2_PROMPT_RULES,
    build_chart_instructions,
    build_components_description,
    build_twostep_step1_examples,
    build_twostep_step2_example,
    build_twostep_step2_rules,
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
    AgentConfigComponent,
    UIComponentMetadata,
)
from pydantic_core import from_json

logger = logging.getLogger(__name__)


class TwostepLLMCallComponentSelectionStrategy(ComponentSelectionStrategy):
    """Component selection strategy using two LLM inference calls, one for component selection and one for its configuration."""

    def __init__(self, config: AgentConfig, select_component_only: bool = False):
        """
        Component selection strategy using two LLM inference calls, one for component selection and one for its configuration.

        Args:
            config: AgentConfig to get selectable components and input data json wrapping configuration from
            select_component_only: if True, only generate the component, it is not necesary to generate it's configuration
        """
        super().__init__(logger, config)
        self.select_component_only = select_component_only

        # Get merged metadata with overrides and set it globally
        merged_metadata = get_component_metadata(config)
        set_active_component_metadata(merged_metadata)

        # Cache for step 1 system prompts by component set (for performance)
        self._system_prompt_step1_cache: dict[frozenset[str], str] = {}

        # Build and cache default step 1 system prompt for backward compatibility
        self._config_selectable_components = config.selectable_components
        self._step1_system_prompt = self._get_or_build_step1_system_prompt(
            config.selectable_components
        )

    def get_system_prompt(self) -> str:
        """
        Get the system prompt for the component selection strategy.
        """
        return self._step1_system_prompt

    def _build_step1_system_prompt(
        self, allowed_components_config: CONFIG_OPTIONS_ALL_COMPONETS
    ) -> str:
        """
        Build complete step 1 system prompt based on allowed components.

        Args:
            allowed_components_config: Set of allowed component names, or None for all components

        Returns:
            Complete system prompt string for step 1
        """
        allowed_components = normalize_allowed_components(allowed_components_config)

        # Get filtered component descriptions
        components_description = build_components_description(allowed_components)

        # Get filtered examples
        response_examples = build_twostep_step1_examples(allowed_components)

        # Detect chart components in allowed set
        allowed_charts = allowed_components & CHART_COMPONENTS

        # Get chart instructions (empty if no charts)
        chart_instructions = build_chart_instructions(allowed_charts)

        # Build the complete system prompt
        system_prompt = f"""You are a UI design assistant. Select the best UI component to visualize the Data based on User query.

{TWOSTEP_STEP1_PROMPT_RULES}

AVAILABLE UI COMPONENTS:
{components_description}

{chart_instructions}"""

        # Add examples if available
        if response_examples:
            system_prompt += f"""

{response_examples}"""

        return system_prompt

    def _get_or_build_step1_system_prompt(
        self, allowed_components_config: CONFIG_OPTIONS_ALL_COMPONETS
    ) -> str:
        """
        Get or build step 1 system prompt with caching.

        Args:
            allowed_components_config: Set of allowed component names, or None for all components

        Returns:
            Cached or newly built system prompt string for step 1
        """
        # Normalize components
        allowed_components = normalize_allowed_components(allowed_components_config)

        # Use frozenset as cache key
        cache_key = frozenset(allowed_components)

        # Check cache
        if cache_key not in self._system_prompt_step1_cache:
            # Build and cache
            self._system_prompt_step1_cache[cache_key] = (
                self._build_step1_system_prompt(allowed_components_config)
            )

        return self._system_prompt_step1_cache[cache_key]

    def parse_infernce_output(
        self, inference_result: InferenceResult, input_data_id: str
    ) -> UIComponentMetadata:
        """Parse inference output and return UIComponentMetadata or throw exception if inference output is invalid."""

        # allow values coercing by `strict=False`
        # allow partial json parsing by `allow_partial=True`, validation will fail on missing fields then. See https://docs.pydantic.dev/latest/concepts/json/#partial-json-parsing
        part = from_json(inference_result["outputs"][0], allow_partial=True)

        # parse fields if they are available
        if len(inference_result["outputs"]) > 1:
            part["fields"] = from_json(
                inference_result["outputs"][1], allow_partial=True
            )
        else:
            part["fields"] = []

        result: UIComponentMetadata = UIComponentMetadata.model_validate(
            part, strict=False
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

    async def perform_inference(
        self,
        inference: InferenceBase,
        user_prompt: str,
        json_data: Any,
        input_data_id: str,
        allowed_components: Optional[set[str]] = None,
        components_config: Optional[dict[str, AgentConfigComponent]] = None,
    ) -> InferenceResult:
        """Run Component Selection inference.

        Args:
            inference: Inference to use to call LLM
            user_prompt: User prompt to be processed
            json_data: JSON data parsed into python objects
            input_data_id: ID of the input data
            allowed_components: Optional set of component names to filter selection to
            components_config: Optional mapping of component names to their configs
                               (used to check llm_configure flag and skip step 2 if needed)
        """

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "---CALL component_selection_inference--- id: %s", {input_data_id}
            )

        data_for_llm = str(json_data)

        # Initialize LLM interactions list
        llm_interactions: list[LLMInteraction] = []

        raw_response_1 = await self.inference_step_1(
            inference, user_prompt, data_for_llm, llm_interactions, allowed_components
        )
        response_1 = trim_to_json(raw_response_1)

        if self.select_component_only:
            return InferenceResult(
                outputs=[response_1], llm_interactions=llm_interactions
            )

        # Check if we should skip step 2 (for llm_configure=False components)
        skip_step_2 = False
        if components_config:
            # Parse step 1 response to get selected component name
            try:
                step1_data = from_json(response_1, allow_partial=True)
                selected_component = step1_data.get("component")
                if selected_component and selected_component in components_config:
                    component_config = components_config[selected_component]
                    if component_config.llm_configure is False:
                        # Skip step 2 for pre-configured components
                        skip_step_2 = True
            except Exception:
                # If parsing fails, continue with step 2 (safe default)
                pass

        if skip_step_2:
            # Return only step 1 result (caller will merge with pre-config)
            return InferenceResult(
                outputs=[response_1], llm_interactions=llm_interactions
            )

        raw_response_2 = await self.inference_step_2(
            inference, response_1, user_prompt, data_for_llm, llm_interactions
        )
        response_2 = trim_to_json(raw_response_2)

        return InferenceResult(
            outputs=[response_1, response_2], llm_interactions=llm_interactions
        )

    async def inference_step_1(
        self,
        inference,
        user_prompt,
        json_data_for_llm: str,
        llm_interactions: list[LLMInteraction],
        allowed_components: Optional[set[str]] = None,
    ):
        """Run Component Selection inference (step 1).

        Args:
            inference: Inference to use
            user_prompt: User prompt
            json_data_for_llm: JSON data as string
            llm_interactions: List to append interaction metadata to
            allowed_components: Optional set of component names to filter to
        """

        # Get or build cached system prompt
        components_to_use = cast(
            CONFIG_OPTIONS_ALL_COMPONETS,
            (
                allowed_components
                if allowed_components is not None
                else self._config_selectable_components
            ),
        )
        sys_msg_content = self._get_or_build_step1_system_prompt(components_to_use)

        prompt = f"""=== User query ===
{user_prompt}
=== Data ===
{json_data_for_llm}
"""

        logger.debug("LLM component selection system message:\n%s", sys_msg_content)
        logger.debug("LLM component selection prompt:\n%s", prompt)

        response = await inference.call_model(sys_msg_content, prompt)
        logger.debug("Component selection LLM response: %s", response)

        # Store step 1 interaction
        llm_interactions.append(
            LLMInteraction(
                step="component_selection",
                system_prompt=sys_msg_content,
                user_prompt=prompt,
                raw_response=response,
            )
        )

        return response

    async def inference_step_2(
        self,
        inference,
        component_selection_response,
        user_prompt,
        json_data_for_llm: str,
        llm_interactions: list[LLMInteraction],
    ):
        component = from_json(component_selection_response, allow_partial=True)[
            "component"
        ]

        """Run Component Configuration inference."""

        sys_msg_content = f"""You are a UI design assistant. Select the best fields to display Data in the {component} component.

{TWOSTEP_STEP2_PROMPT_RULES}

{build_twostep_step2_rules(component)}

{build_twostep_step2_example(component)}
"""

        prompt = f"""=== User query ===
{user_prompt}

=== Data ===
{json_data_for_llm}
"""

        logger.debug("LLM component configuration system message:\n%s", sys_msg_content)
        logger.debug("LLM component configuration prompt:\n%s", prompt)

        response = await inference.call_model(sys_msg_content, prompt)
        logger.debug("Component configuration LLM response: %s", response)

        # Store step 2 interaction
        llm_interactions.append(
            LLMInteraction(
                step="field_selection",
                system_prompt=sys_msg_content,
                user_prompt=prompt,
                raw_response=response,
            )
        )

        return response
