import logging
from typing import Any, Optional

from next_gen_ui_agent.component_metadata import (
    get_component_metadata,
    merge_per_component_prompt_overrides,
)
from next_gen_ui_agent.component_selection_common import (
    CHART_COMPONENTS,
    build_chart_instructions,
    build_components_description,
    build_twostep_step2configure_example,
    build_twostep_step2configure_rules,
    get_prompt_field,
    has_chart_components,
    has_non_chart_components,
    normalize_allowed_components,
)
from next_gen_ui_agent.component_selection_llm_strategy import (
    ComponentSelectionStrategy,
    InferenceResult,
    LLMInteraction,
    trim_to_json,
    validate_and_correct_chart_type,
)
from next_gen_ui_agent.component_selection_pertype import DYNAMIC_COMPONENT_NAMES
from next_gen_ui_agent.inference.inference_base import InferenceBase
from next_gen_ui_agent.types import (
    AgentConfig,
    AgentConfigComponent,
    UIComponentMetadata,
)
from pydantic_core import from_json

logger = logging.getLogger(__name__)


# Default prompt templates for step 1 (component selection)
DEFAULT_STEP1SELECT_SYSTEM_PROMPT_START = """You are a UI design assistant. Select the best UI component to visualize the Data based on User query.

RULES:
- Generate JSON only
- If user explicitly requests a component type ("table", "chart", "cards"), USE IT if present in the list of AVAILABLE UI COMPONENTS, unless data structure prevents it
- Select one component into "component" field. It MUST BE named in the AVAILABLE UI COMPONENTS!
- Provide "title", "reasonForTheComponentSelection", "confidenceScore" (percentage)

AVAILABLE UI COMPONENTS:"""

DEFAULT_STEP1SELECT_EXAMPLES_NORMALCOMPONENTS = """Response example for multi-item data when table is suitable:
{
    "reasonForTheComponentSelection": "User explicitly requested a table, and data has multiple items with short field values",
    "confidenceScore": "95%",
    "title": "Orders",
    "component": "table"
}

Response example for one-item data when one-card is suitable:
{
    "reasonForTheComponentSelection": "One item available in the data. Multiple fields to show based on the User query",
    "confidenceScore": "95%",
    "title": "Order CA565",
    "component": "one-card"
}

Response example for one-item data and image when image is suitable:
{
    "reasonForTheComponentSelection": "User asked to see the magazine cover",
    "confidenceScore": "75%",
    "title": "Magazine cover",
    "component": "image"
}"""

DEFAULT_STEP1SELECT_EXAMPLES_CHARTS = """Response example for multi-item data when bar chart is suitable:
{
    "title": "Movie Revenue Comparison",
    "reasonForTheComponentSelection": "User wants to compare numeric values as a chart",
    "confidenceScore": "90%",
    "component": "chart-bar"
}

Response example for multi-item data when mirrored-bar chart is suitable (comparing 2 metrics):
{
    "title": "Movie ROI and Budget Comparison",
    "reasonForTheComponentSelection": "User wants to compare two metrics (ROI and budget) across movies, which requires a mirrored-bar chart to handle different scales",
    "confidenceScore": "90%",
    "component": "chart-mirrored-bar"
}"""

# Default prompt template for step 2 (field configuration)
DEFAULT_STEP2CONFIGURE_SYSTEM_PROMPT_START = """You are a UI design assistant. Select the best fields to display Data in the {component} component.

RULES:
- Generate JSON array of objects only
- Each field must also have "reason" and "confidenceScore" (percentage)
- Select relevant Data fields based on User query
- Each field must have "name" and "data_path"
- Do not use formatting or calculations in "data_path"

JSONPATH REQUIREMENTS:
- Analyze actual Data structure carefully
- If fields are nested (e.g., items[*].movie.title), include full path
- Do NOT skip intermediate objects
- Use [*] for array access"""

# User prompt template for step1select
# Available placeholders: {user_prompt}, {json_data_for_llm}
STEP1SELECT_USER_PROMPT_TEMPLATE = """=== User query ===
{user_prompt}
=== Data ===
{json_data_for_llm}
"""

# User prompt template for step2configure
# Available placeholders: {user_prompt}, {json_data_for_llm}
STEP2CONFIGURE_USER_PROMPT_TEMPLATE = """=== User query ===
{user_prompt}

=== Data ===
{json_data_for_llm}
"""


class TwostepLLMCallComponentSelectionStrategy(ComponentSelectionStrategy):
    """Component selection strategy using two LLM inference calls, one for component selection and one for its configuration."""

    def __init__(self, config: AgentConfig, select_component_only: bool = False):
        """
        Component selection strategy using two LLM inference calls, one for component selection and one for its configuration.

        Args:
            config: AgentConfig to get selectable components and input data json wrapping configuration from
            select_component_only: if True, only generate the component, it is not necesary to generate it's configuration

        Raises:
            ValueError: If custom twostep_step2configure_system_prompt_start is provided but doesn't contain {component} placeholder
        """
        super().__init__(logger, config)
        self.select_component_only = select_component_only

        # Store full config for data_type lookups
        self.config = config

        # Validate custom step2 prompt if provided
        if (
            config.prompt
            and config.prompt.twostep_step2configure_system_prompt_start
            and "{component}"
            not in config.prompt.twostep_step2configure_system_prompt_start
        ):
            raise ValueError(
                "Custom 'twostep_step2configure_system_prompt_start' must contain {component} placeholder "
                "which will be replaced with the selected component name"
            )

        # Get merged metadata with global overrides
        self._base_metadata = get_component_metadata(config)

        # Cache for step1select system prompts by data_type (for performance)
        self._system_prompt_step1select_cache: dict[str | None, str] = {}

        # Build and cache default step1select system prompt for backward compatibility
        self._step1select_system_prompt = self._get_or_build_step1select_system_prompt(
            data_type=None
        )

    def get_system_prompt(self) -> str:
        """
        Get the system prompt for the component selection strategy.
        """
        return self._step1select_system_prompt

    def _build_step1select_system_prompt(
        self,
        data_type: Optional[str] = None,
    ) -> str:
        """
        Build complete step1select system prompt based on data_type.

        Args:
            data_type: Optional data type for data-type-specific prompt customization

        Returns:
            Complete system prompt string for step1select
        """
        # Determine allowed components and metadata based on data_type
        if data_type and self.config.data_types and data_type in self.config.data_types:
            # Extract component names from data_type configuration
            components_list = self.config.data_types[data_type].components
            if components_list:
                allowed_components_config = {comp.component for comp in components_list}

                # Merge per-component prompt overrides
                metadata = merge_per_component_prompt_overrides(
                    self._base_metadata, components_list
                )
            else:
                allowed_components_config = set(self._base_metadata.keys())
                metadata = self._base_metadata
        else:
            # Global selection - use selectable_components
            allowed_components_config = (
                set(self.config.selectable_components)
                if self.config.selectable_components
                else set(self._base_metadata.keys())
            )
            # Use base metadata for global selection
            metadata = self._base_metadata

        allowed_components = normalize_allowed_components(
            allowed_components_config, metadata
        )

        # Get filtered component descriptions
        components_description = build_components_description(
            allowed_components, metadata
        )

        # Detect chart components in allowed set
        allowed_charts = allowed_components & CHART_COMPONENTS

        # Get chart instructions template from config with precedence: data_type > global > default
        chart_template = get_prompt_field(
            "chart_instructions_template", self.config, data_type, ""
        )
        chart_instructions = build_chart_instructions(
            allowed_charts, metadata, chart_template
        )

        # Get initial prompt with precedence: data_type > global > default
        initial_section = get_prompt_field(
            "twostep_step1select_system_prompt_start",
            self.config,
            data_type,
            DEFAULT_STEP1SELECT_SYSTEM_PROMPT_START,
        )

        # Build the complete system prompt
        system_prompt = f"""{initial_section}
{components_description}

{chart_instructions}"""

        # Get filtered examples
        response_examples = self._build_step1select_examples(
            allowed_components, data_type
        )

        # Add examples if available
        if response_examples:
            system_prompt += f"""

{response_examples}"""

        return system_prompt

    def _build_step1select_examples(
        self, allowed_components: set[str], data_type: Optional[str] = None
    ) -> str:
        """
        Build examples section for two-step step1 (component selection) system prompt.

        Args:
            allowed_components: Set of allowed component names
            data_type: Optional data type for data-type-specific prompt customization

        Returns:
            Formatted string with examples
        """
        # Combine normal components and chart examples
        examples = []

        normalcomponents_examples = self._build_step1select_normalcomponents_examples(
            allowed_components, data_type
        )
        if normalcomponents_examples:
            examples.append(normalcomponents_examples)

        chart_examples = self._build_step1select_chart_examples(
            allowed_components, data_type
        )
        if chart_examples:
            examples.append(chart_examples)

        return "\n\n".join(examples)

    def _build_step1select_normalcomponents_examples(
        self, allowed_components: set[str], data_type: Optional[str] = None
    ) -> str:
        """Build normal component examples for step1."""
        if not has_non_chart_components(allowed_components):
            return ""

        # Get template with precedence: data_type > global > default
        return get_prompt_field(
            "twostep_step1select_examples_normalcomponents",
            self.config,
            data_type,
            DEFAULT_STEP1SELECT_EXAMPLES_NORMALCOMPONENTS,
        )

    def _build_step1select_chart_examples(
        self, allowed_components: set[str], data_type: Optional[str] = None
    ) -> str:
        """Build chart component examples for step1."""
        if not has_chart_components(allowed_components):
            return ""

        # Get template with precedence: data_type > global > default
        return get_prompt_field(
            "twostep_step1select_examples_charts",
            self.config,
            data_type,
            DEFAULT_STEP1SELECT_EXAMPLES_CHARTS,
        )

    def _get_or_build_step1select_system_prompt(self, data_type: str | None) -> str:
        """
        Get or build step1select system prompt with caching.

        Args:
            data_type: Data type identifier (or None for global selection)

        Returns:
            Cached or newly built system prompt string for step1select
        """
        # Use data_type as cache key
        cache_key = data_type

        # Check cache
        if cache_key not in self._system_prompt_step1select_cache:
            # Build and cache (data_type-specific logic is inside _build_step1select_system_prompt)
            self._system_prompt_step1select_cache[cache_key] = (
                self._build_step1select_system_prompt(data_type)
            )

        return self._system_prompt_step1select_cache[cache_key]

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
        data_type: Optional[str] = None,
    ) -> InferenceResult:
        """Run Component Selection inference.

        Args:
            inference: Inference to use to call LLM
            user_prompt: User prompt to be processed
            json_data: JSON data parsed into python objects
            input_data_id: ID of the input data
            data_type: Optional data type identifier for data_type-specific prompt customization
        """

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "---CALL component_selection_inference--- id: %s, data_type: %s",
                input_data_id,
                data_type,
            )

        data_for_llm = str(json_data)

        # Initialize LLM interactions list
        llm_interactions: list[LLMInteraction] = []

        # Determine metadata based on data_type (for step2configure)
        metadata_for_step2configure = self._base_metadata
        components_config: Optional[dict[str, AgentConfigComponent]] = None
        if data_type and self.config.data_types and data_type in self.config.data_types:
            components_list = self.config.data_types[data_type].components
            if components_list:
                components_config = {comp.component: comp for comp in components_list}
                # Merge per-component prompt overrides for step2configure
                metadata_for_step2configure = merge_per_component_prompt_overrides(
                    self._base_metadata, components_list
                )

        raw_response_1 = await self.inference_step1select(
            inference, user_prompt, data_for_llm, llm_interactions, data_type
        )
        response_1 = trim_to_json(raw_response_1)

        if self.select_component_only:
            return InferenceResult(
                outputs=[response_1], llm_interactions=llm_interactions
            )

        # Check if we should skip step2configure
        skip_step2configure = False
        # Parse step1select response to get selected component name
        try:
            step1select_data = from_json(response_1, allow_partial=True)
            selected_component = step1select_data.get("component")
            if selected_component:
                # Skip step2configure for HBCs (hand-build components don't need field selection)
                if selected_component not in DYNAMIC_COMPONENT_NAMES:
                    skip_step2configure = True
                # Skip step2configure for pre-configured dynamic components
                elif (
                    components_config
                    and selected_component in components_config
                    and components_config[selected_component].llm_configure is False
                ):
                    skip_step2configure = True
        except Exception:
            # If parsing fails, continue with step2configure (safe default)
            pass

        if skip_step2configure:
            # Return only step1select result (for HBCs or pre-configured components)
            return InferenceResult(
                outputs=[response_1], llm_interactions=llm_interactions
            )

        raw_response_2 = await self.inference_step2configure(
            inference,
            response_1,
            user_prompt,
            data_for_llm,
            llm_interactions,
            metadata_for_step2configure,
            data_type,
        )
        response_2 = trim_to_json(raw_response_2)

        return InferenceResult(
            outputs=[response_1, response_2], llm_interactions=llm_interactions
        )

    async def inference_step1select(
        self,
        inference,
        user_prompt,
        json_data_for_llm: str,
        llm_interactions: list[LLMInteraction],
        data_type: Optional[str] = None,
    ):
        """Run Component Selection inference (step1select).

        Args:
            inference: Inference to use
            user_prompt: User prompt
            json_data_for_llm: JSON data as string
            llm_interactions: List to append interaction metadata to
            data_type: Optional data type identifier for data_type-specific prompt customization
        """

        # Get or build cached system prompt using data_type
        sys_msg_content = self._get_or_build_step1select_system_prompt(data_type)

        prompt = STEP1SELECT_USER_PROMPT_TEMPLATE.format(
            user_prompt=user_prompt, json_data_for_llm=json_data_for_llm
        )

        logger.debug("LLM component selection system message:\n%s", sys_msg_content)
        logger.debug("LLM component selection prompt:\n%s", prompt)

        response = await inference.call_model(sys_msg_content, prompt)
        logger.debug("Component selection LLM response: %s", response)

        # Store step1select interaction
        llm_interactions.append(
            LLMInteraction(
                step="component_selection",
                system_prompt=sys_msg_content,
                user_prompt=prompt,
                raw_response=response,
            )
        )

        return response

    async def inference_step2configure(
        self,
        inference,
        component_selection_response,
        user_prompt,
        json_data_for_llm: str,
        llm_interactions: list[LLMInteraction],
        metadata: dict,
        data_type: Optional[str] = None,
    ):
        """Run Component Configuration inference (step2configure).

        Args:
            inference: Inference to use to call LLM
            component_selection_response: Response from step1select containing selected component
            user_prompt: User prompt to be processed
            json_data_for_llm: JSON data as string for LLM
            llm_interactions: List to store LLM interactions for debugging
            metadata: Component metadata dictionary to use
            data_type: Optional data type for data-type-specific prompt customization
        """
        component = from_json(component_selection_response, allow_partial=True)[
            "component"
        ]

        # Get initial prompt with precedence: data_type > global > default
        initial_section_template = get_prompt_field(
            "twostep_step2configure_system_prompt_start",
            self.config,
            data_type,
            DEFAULT_STEP2CONFIGURE_SYSTEM_PROMPT_START,
        )

        # Substitute {component} placeholder if present
        initial_section = initial_section_template.format(component=component)

        sys_msg_content = f"""{initial_section}

{build_twostep_step2configure_rules(component, metadata)}

{build_twostep_step2configure_example(component, metadata)}
"""

        prompt = STEP2CONFIGURE_USER_PROMPT_TEMPLATE.format(
            user_prompt=user_prompt, json_data_for_llm=json_data_for_llm
        )

        logger.debug("LLM component configuration system message:\n%s", sys_msg_content)
        logger.debug("LLM component configuration prompt:\n%s", prompt)

        response = await inference.call_model(sys_msg_content, prompt)
        logger.debug("Component configuration LLM response: %s", response)

        # Store step2configure interaction
        llm_interactions.append(
            LLMInteraction(
                step="field_selection",
                system_prompt=sys_msg_content,
                user_prompt=prompt,
                raw_response=response,
            )
        )

        return response
