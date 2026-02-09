import logging
from typing import Any, Optional

from next_gen_ui_agent.component_selection_common import (
    CHART_COMPONENTS,
    build_chart_instructions,
    get_prompt_field,
    has_chart_components,
    has_non_chart_components,
)
from next_gen_ui_agent.component_selection_llm_strategy import (
    ComponentSelectionStrategy,
    InferenceResult,
    LLMInteraction,
    trim_to_json,
    validate_and_correct_chart_type,
)
from next_gen_ui_agent.inference.inference_base import InferenceBase
from next_gen_ui_agent.types import AgentConfig, UIComponentMetadata
from pydantic_core import from_json

logger = logging.getLogger(__name__)


# Default prompt templates
DEFAULT_SYSTEM_PROMPT_START = """You are a UI design assistant. Select the best UI component to visualize the Data based on User query.

RULES:
- Generate JSON only
- If user explicitly requests a component type ("table", "chart", "cards"), USE IT if present in the list of AVAILABLE UI COMPONENTS, unless data structure prevents it
- Select one component into "component" field. It MUST BE named in the AVAILABLE UI COMPONENTS!
- Provide "title", "reasonForTheComponentSelection", "confidenceScore" (percentage)
- Select relevant Data fields based on User query
- Each field must have "name" and "data_path"
- Do not use formatting or calculations in "data_path"

JSONPATH REQUIREMENTS:
- Analyze actual Data structure carefully
- If fields are nested (e.g., items[*].movie.title), include full path
- Do NOT skip intermediate objects
- Use [*] for array access

AVAILABLE UI COMPONENTS:"""

DEFAULT_EXAMPLES_NORMALCOMPONENTS = """Response example for multi-item data when table is suitable:
{
    "title": "Orders",
    "reasonForTheComponentSelection": "User explicitly requested a table, and data has multiple items with short field values",
    "confidenceScore": "95%",
    "component": "table",
    "fields" : [
        {"name":"Name","data_path":"orders[*].name"},
        {"name":"Creation Date","data_path":"orders[*].creationDate"}
    ]
}

Response example for one-item data when one-card is suitable:
{
    "title": "Order CA565",
    "reasonForTheComponentSelection": "One item available in the data",
    "confidenceScore": "75%",
    "component": "one-card",
    "fields" : [
        {"name":"Name","data_path":"order.name"},
        {"name":"Creation Date","data_path":"order.creationDate"}
    ]
}"""

DEFAULT_EXAMPLES_CHARTS = """Response example for multi-item data when bar chart is suitable:
{
    "title": "Movie Revenue Comparison",
    "reasonForTheComponentSelection": "User wants to compare numeric values as a chart",
    "confidenceScore": "90%",
    "component": "chart-bar",
    "fields" : [
        {"name":"Movie","data_path":"movies[*].title"},
        {"name":"Revenue","data_path":"movies[*].revenue"}
    ]
}

Response example for multi-item data when mirrored-bar chart is suitable (comparing 2 metrics, note nested structure):
{
    "title": "Movie ROI and Budget Comparison",
    "reasonForTheComponentSelection": "User wants to compare two metrics (ROI and budget) across movies, which requires a mirrored-bar chart to handle different scales",
    "confidenceScore": "90%",
    "component": "chart-mirrored-bar",
    "fields" : [
        {"name":"Movie","data_path":"get_all_movies[*].movie.title"},
        {"name":"ROI","data_path":"get_all_movies[*].movie.roi"},
        {"name":"Budget","data_path":"get_all_movies[*].movie.budget"}
    ]
}"""

# User prompt template for inference
# Available placeholders: {user_prompt}, {json_data}
USER_PROMPT_TEMPLATE = """=== User query ===
    {user_prompt}

    === Data ===
    {json_data}
        """


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

        # Cache for system prompts by data_type (for performance)
        self._system_prompt_cache: dict[str | None, str] = {}

        # Build and cache default system prompt for backward compatibility
        self._system_prompt = self._get_or_build_system_prompt(data_type=None)

    def get_system_prompt(self, data_type: Optional[str] = None) -> str:
        """
        Get the system prompt for the component selection strategy.

        Args:
            data_type: Optional data type for data-type-specific prompt customization

        Returns:
            System prompt string for the given data_type (or global prompt if None)
        """
        return self._get_or_build_system_prompt(data_type)

    def get_debug_prompts(
        self,
        data_type: Optional[str] = None,
        component_for_step2: Optional[str] = None,
    ) -> dict[str, str]:
        """
        Get all system prompts for debugging/inspection.

        For one-step strategy, returns a single system prompt that handles both
        component selection and configuration.

        Args:
            data_type: Optional data type for data-type-specific prompt customization
            component_for_step2: Not used in one-step strategy (included for interface compatibility)

        Returns:
            Dictionary with single key 'system_prompt' containing the complete prompt
        """
        return {"system_prompt": self._get_or_build_system_prompt(data_type)}

    def _build_system_prompt(
        self,
        data_type: Optional[str] = None,
    ) -> str:
        """
        Build complete system prompt based on data_type.

        Args:
            data_type: Optional data type for data-type-specific prompt customization

        Returns:
            Complete system prompt string
        """
        # Determine allowed components, metadata, and descriptions based on data_type
        (
            allowed_components,
            metadata,
            components_description,
        ) = self._resolve_components_and_description(data_type)

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
            "system_prompt_start", self.config, data_type, DEFAULT_SYSTEM_PROMPT_START
        )

        # Build the complete system prompt with initial section + generated parts
        system_prompt = f"""{initial_section}
{components_description}

{chart_instructions}"""

        # Get filtered examples
        response_examples = self._build_examples(allowed_components, data_type)

        # Add examples if available
        if response_examples:
            system_prompt += f"""

{response_examples}"""

        return system_prompt

    def _build_examples(
        self, allowed_components: set[str], data_type: Optional[str] = None
    ) -> str:
        """
        Build examples section for one-step strategy system prompt.

        Args:
            allowed_components: Set of allowed component names
            data_type: Optional data type for data-type-specific prompt customization

        Returns:
            Formatted string with examples
        """
        # Combine normal components and chart examples
        examples = []

        normalcomponents_examples = self._build_normalcomponents_examples(
            allowed_components, data_type
        )
        if normalcomponents_examples:
            examples.append(normalcomponents_examples)

        chart_examples = self._build_chart_examples(allowed_components, data_type)
        if chart_examples:
            examples.append(chart_examples)

        return "\n\n".join(examples)

    def _build_normalcomponents_examples(
        self, allowed_components: set[str], data_type: Optional[str] = None
    ) -> str:
        """Build normal component examples (table, cards, image)."""
        if not has_non_chart_components(allowed_components):
            return ""

        # Get template with precedence: data_type > global > default
        return get_prompt_field(
            "examples_normalcomponents",
            self.config,
            data_type,
            DEFAULT_EXAMPLES_NORMALCOMPONENTS,
        )

    def _build_chart_examples(
        self, allowed_components: set[str], data_type: Optional[str] = None
    ) -> str:
        """Build chart component examples."""
        if not has_chart_components(allowed_components):
            return ""

        # Get template with precedence: data_type > global > default
        return get_prompt_field(
            "examples_charts", self.config, data_type, DEFAULT_EXAMPLES_CHARTS
        )

    def _get_or_build_system_prompt(self, data_type: str | None) -> str:
        """
        Get or build system prompt with caching.

        Args:
            data_type: Data type identifier (or None for global selection)

        Returns:
            Cached or newly built system prompt string
        """
        # Use data_type as cache key
        cache_key = data_type

        # Check cache
        if cache_key not in self._system_prompt_cache:
            # Build and cache (data_type-specific logic is inside _build_system_prompt)
            self._system_prompt_cache[cache_key] = self._build_system_prompt(data_type)

        return self._system_prompt_cache[cache_key]

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
            # logger.debug(user_prompt)
            # logger.debug(input_data)

        # Get or build cached system prompt using data_type
        sys_msg_content = self._get_or_build_system_prompt(data_type)

        prompt = USER_PROMPT_TEMPLATE.format(
            user_prompt=user_prompt, json_data=str(json_data)
        )

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
