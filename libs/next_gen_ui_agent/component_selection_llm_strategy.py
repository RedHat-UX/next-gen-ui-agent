import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Optional, TypedDict

from next_gen_ui_agent.array_field_reducer import reduce_arrays
from next_gen_ui_agent.component_metadata import (
    get_component_metadata,
    merge_per_component_prompt_overrides,
)
from next_gen_ui_agent.component_selection_common import (
    build_components_description,
    normalize_allowed_components,
)
from next_gen_ui_agent.inference.inference_base import InferenceBase
from next_gen_ui_agent.json_data_wrapper import wrap_json_data, wrap_string_as_json
from next_gen_ui_agent.types import (
    AgentConfig,
    AgentConfigPromptComponent,
    InputDataInternal,
    UIComponentMetadata,
)


class LLMInteraction(TypedDict):
    """LLM interaction metadata for debugging."""

    step: str
    system_prompt: str
    user_prompt: str
    raw_response: str


class InferenceResult(TypedDict):
    """Result from perform_inference containing outputs and metadata."""

    outputs: list[str]  # The actual LLM responses
    llm_interactions: list[LLMInteraction]  # Metadata for debugging


MAX_STRING_DATA_LENGTH_FOR_LLM = 1000
"""Maximum length of the string data passed to the LLM in characters."""

MAX_ARRAY_SIZE_FOR_LLM = 6
"""Maximum size of the array data passed to the LLM in items. `reduce_arrays` function is used to reduce arrays size. LLM prompts must be tuned to handle the reduced arrays size."""


class ComponentSelectionStrategy(ABC):
    """Abstract base class for LLM-based component selection and configuration strategies."""

    logger: logging.Logger
    config: AgentConfig
    """AgentConfig for component selection configuration."""

    _base_metadata: dict[str, AgentConfigPromptComponent]
    """Base component metadata with global overrides applied."""

    input_data_json_wrapping: bool
    """
    If `True`, the agent will wrap the JSON input data into data type field if necessary due to its structure.
    If `False`, the agent will never wrap the JSON input data into data type field.
    """

    def __init__(self, logger: logging.Logger, config: AgentConfig):
        self.logger = logger
        self.config = config
        self._base_metadata = get_component_metadata(config)
        self.input_data_json_wrapping = (
            config.input_data_json_wrapping
            if config.input_data_json_wrapping is not None
            else True
        )

    def get_system_prompt(self, data_type: Optional[str] = None) -> str:
        """
        Get the system prompt for the component selection strategy.

        Args:
            data_type: Optional data type for data-type-specific prompt customization

        Returns:
            System prompt string for the given data_type (or global prompt if None)
        """
        return "NOT IMPLEMENTED"

    def get_debug_prompts(
        self,
        data_type: Optional[str] = None,
        component_for_step2: Optional[str] = None,
    ) -> dict[str, str]:
        """
        Get all system prompts for debugging/inspection.

        This method returns the actual system prompts that would be used at runtime
        for different strategies and configurations. Useful for prompt tuning and
        understanding how the agent behaves with different settings.

        Args:
            data_type: Optional data type for data-type-specific prompt customization
            component_for_step2: For two-step strategy: specific component name to show
                step2 prompt for (e.g., 'table', 'chart-bar'). If None, returns prompts
                for all dynamic components.

        Returns:
            Dictionary with prompt keys and their content. Keys depend on strategy:
            - One-step strategy: {'system_prompt': '...'}
            - Two-step strategy: {'step1_system_prompt': '...', 'step2_system_prompt_<component>': '...'}
        """
        return {}

    async def select_component(
        self,
        inference: InferenceBase,
        user_prompt: str,
        input_data: InputDataInternal,
    ) -> UIComponentMetadata:
        """
        Select UI component based on input data and user prompt.
        Args:
            inference: Inference to use to call LLM by the agent
            user_prompt: User prompt to be processed
            input_data: Input data to be processed (contains optional 'type' field for data_type-specific prompt customization)
        Returns:
            Generated `UIComponentMetadata`
        Raises:
            Exception: If the component selection fails
        """

        input_data_id = input_data["id"]
        data_type = input_data.get("type")
        self.logger.debug(
            "---CALL component_selection_run--- id: %s, data_type: %s",
            input_data_id,
            data_type,
        )

        json_data = input_data.get("json_data")
        input_data_transformer_name: str | None = input_data.get(
            "input_data_transformer_name"
        )

        if not json_data:
            json_data = json.loads(input_data["data"])

        json_wrapping_field_name: str | None = None
        if isinstance(json_data, str):
            # wrap string as JSON - necessary for the output of the `noop` input data transformer to be processed by the LLM
            json_data_for_llm, notused = wrap_string_as_json(
                json_data, input_data.get("type"), MAX_STRING_DATA_LENGTH_FOR_LLM
            )
            json_data, json_wrapping_field_name = wrap_string_as_json(
                json_data, input_data.get("type")
            )

        else:
            # wrap parsed JSON data structure into data type field if allowed and necessary
            if self.input_data_json_wrapping:
                json_data, json_wrapping_field_name = wrap_json_data(
                    json_data, input_data.get("type")
                )
            # we have to reduce arrays size to avoid LLM context window limit
            json_data_for_llm = reduce_arrays(json_data, MAX_ARRAY_SIZE_FOR_LLM)

        inference_result = await self.perform_inference(
            inference,
            user_prompt,
            json_data_for_llm,
            input_data_id,
            data_type,
        )

        try:
            result = self.parse_infernce_output(inference_result, input_data_id)
            result.json_data = json_data
            result.input_data_transformer_name = input_data_transformer_name
            result.json_wrapping_field_name = json_wrapping_field_name
            result.input_data_type = input_data.get("type")

            # Handle llm_configure=False merging for data_type-specific components
            if data_type and not result.fields:
                result = self._merge_with_preconfig_if_needed(data_type, result)

            return result
        except Exception as e:
            self.logger.exception("Cannot decode the json from LLM response")
            raise e

    def get_allowed_components(self, data_type: Optional[str] = None) -> set[str]:
        """Get allowed components for the given data_type.

        This is a convenience method that returns only the allowed components,
        without the metadata.

        Args:
            data_type: Optional data type for data-type-specific component selection

        Returns:
            Set of normalized component names that are allowed for the given data_type regarding used config.
        """
        allowed_components, _ = self._resolve_allowed_components_and_metadata(data_type)
        return allowed_components

    def get_allowed_components_description(
        self, data_type: Optional[str] = None
    ) -> str:
        """Get formatted components description for the given data_type used in the system prompt.

        This is a convenience method that returns only the formatted description string
        of allowed components, without the components set or metadata.

        Args:
            data_type: Optional data type for data-type-specific component selection

        Returns:
            Formatted string describing the allowed components regarding used config.
        """
        _, _, components_description = self._resolve_components_and_description(
            data_type
        )
        return components_description

    def _resolve_components_and_description(
        self, data_type: Optional[str]
    ) -> tuple[set[str], dict[str, AgentConfigPromptComponent], str]:
        """Resolve allowed components, metadata, and component descriptions for data_type.

        This is a convenience method that combines _resolve_allowed_components_and_metadata
        with build_components_description.

        Args:
            data_type: Optional data type for data-type-specific component selection

        Returns:
            Tuple of (allowed_components, metadata, components_description) where:
                - allowed_components: Set of normalized component names
                - metadata: Dictionary mapping component names to their metadata
                - components_description: Formatted string describing the components
        """
        allowed_components, metadata = self._resolve_allowed_components_and_metadata(
            data_type
        )
        components_description = build_components_description(
            allowed_components, metadata
        )
        return allowed_components, metadata, components_description

    def _resolve_allowed_components_and_metadata(
        self, data_type: Optional[str]
    ) -> tuple[set[str], dict[str, AgentConfigPromptComponent]]:
        """Resolve allowed components and metadata based on data_type.

        This method determines which components are allowed and what metadata to use
        based on whether a data_type is specified. It handles:
        - Data-type-specific component selection with per-component prompt overrides
        - Global component selection using selectable_components
        - Fallback to all available components

        Args:
            data_type: Optional data type for data-type-specific component selection

        Returns:
            Tuple of (allowed_components, metadata) where:
                - allowed_components: Set of normalized component names
                - metadata: Dictionary mapping component names to their metadata
        """
        config: AgentConfig = self.config
        base_metadata: dict[str, AgentConfigPromptComponent] = self._base_metadata

        # Determine allowed components and metadata based on data_type
        if data_type and config.data_types and data_type in config.data_types:
            # Extract component names from data_type configuration
            components_list = config.data_types[data_type].components
            if components_list:
                allowed_components_config = {comp.component for comp in components_list}

                # Merge per-component prompt overrides
                metadata = merge_per_component_prompt_overrides(
                    base_metadata, components_list
                )
            else:
                allowed_components_config = set(base_metadata.keys())
                metadata = base_metadata
        else:
            # Global selection - use selectable_components
            allowed_components_config = (
                set(config.selectable_components)
                if config.selectable_components
                else set(base_metadata.keys())
            )
            # Use base metadata for global selection
            metadata = base_metadata

        allowed_components = normalize_allowed_components(
            allowed_components_config, metadata
        )

        return allowed_components, metadata

    def _merge_with_preconfig_if_needed(
        self, data_type: str, result: UIComponentMetadata
    ) -> UIComponentMetadata:
        """Merge LLM selection with pre-configuration if llm_configure=False.

        Args:
            data_type: Data type identifier
            result: Partial result from LLM (component selected, but no fields)

        Returns:
            Complete UIComponentMetadata with fields from pre-configuration
        """
        # Import here to avoid circular dependency
        from next_gen_ui_agent.types import AgentConfig

        # Get config (must be set in subclass __init__)
        if not hasattr(self, "config"):
            return result

        config: AgentConfig = self.config

        # No fields means pre-configuration should be used
        if config.data_types and data_type in config.data_types:
            data_type_config = config.data_types[data_type]
            if data_type_config.components:
                # Find the selected component in the config
                selected_component_name = result.component
                for comp in data_type_config.components:
                    if comp.component == selected_component_name:
                        if comp.llm_configure is False and comp.configuration:
                            # Merge LLM selection metadata with pre-configured fields
                            result = UIComponentMetadata(
                                id=result.id,
                                component=selected_component_name,
                                title=comp.configuration.title,
                                fields=comp.configuration.fields,
                                reasonForTheComponentSelection=result.reasonForTheComponentSelection,
                                confidenceScore=result.confidenceScore,
                                json_data=result.json_data,
                                input_data_transformer_name=result.input_data_transformer_name,
                                json_wrapping_field_name=result.json_wrapping_field_name,
                                input_data_type=result.input_data_type,
                                llm_interactions=result.llm_interactions,
                            )
                        break

        return result

    @abstractmethod
    async def perform_inference(
        self,
        inference: InferenceBase,
        user_prompt: str,
        json_data: Any,
        input_data_id: str,
        data_type: Optional[str] = None,
    ) -> InferenceResult:
        """
        Perform inference to select UI components and configure them.
        Multiple LLM calls can be performed and inference results can be returned along with metadata.

        Args:
            inference: Inference to use to call LLM
            user_prompt: User prompt to be processed
            json_data: JSON data parsed into python objects
            input_data_id: ID of the input data
            data_type: Optional data type identifier for data_type-specific prompt customization

        Args:
            inference: Inference to use to call LLM by the agent
            user_prompt: User prompt to be processed
            json_data: JSON data parsed into python objects to be processed
            input_data_id: ID of the input data
            allowed_components: Optional set of component names to filter selection to
            components_config: Optional mapping of component names to their configs

        Returns:
            InferenceResult with outputs and llm_interactions
        """
        pass

    @abstractmethod
    def parse_infernce_output(
        self, inference_result: InferenceResult, input_data_id: str
    ) -> UIComponentMetadata:
        """
        Parse LLM inference outputs from `perform_inference` and return `UIComponentMetadata`
        or throw exception if it can't be constructed because of invalid LLM outputs.

        Args:
            inference_result: InferenceResult from perform_inference method
            input_data_id: ID of the input data

        Returns:
            `UIComponentMetadata`
        """
        pass


def trim_to_json(text: str) -> str:
    """
    Remove all characters from the string before `</think>` tag if present.
    Then remove all characters until the first occurrence of '{' or '[' character. String is not modified if these character are not found.
    Everything after the last '}' or ']' character is stripped also.

    Args:
        text: The input string to process

    Returns:
        The string starting from the first '{' or '[' character and ending at the last '}' or ']' character,
        or the original string if neither character is found
    """

    # check if text contains </think> tag
    if "</think>" in text:
        text = text.split("</think>")[1]

    # Find the start of JSON (first { or [)
    start_index = -1
    for i, char in enumerate(text):
        if char in "{[":
            start_index = i
            break

    if start_index == -1:
        return text

    # Find the end of JSON (last } or ])
    end_index = -1
    for i in range(len(text) - 1, start_index - 1, -1):
        if text[i] in "]}":
            end_index = i + 1
            break

    if end_index == -1:
        return text[start_index:]

    return text[start_index:end_index]


def validate_and_correct_chart_type(
    result: UIComponentMetadata, logger: logging.Logger
) -> None:
    """
    Validate that the chart component type in the result matches what's mentioned in the reasoning.
    If there's a mismatch, auto-correct the component and log a warning.

    Args:
        result: The UIComponentMetadata to validate and potentially correct
        logger: Logger instance for warnings
    """
    if not result.component.startswith("chart-"):
        return

    reasoning_lower = (result.reasonForTheComponentSelection or "").lower()

    # Map of chart type keywords to expected component values
    # Order matters: check more specific types first (e.g., "mirrored-bar" before "bar")
    chart_type_checks = [
        ("chart-mirrored-bar", ["mirrored-bar", "mirrored bar"]),
        ("chart-donut", ["donut"]),
        ("chart-pie", ["pie"]),
        ("chart-line", ["line"]),
        ("chart-bar", ["bar"]),
    ]

    # Check for explicit chart type mentions in reasoning
    detected_type = None
    for expected_component, keywords in chart_type_checks:
        if any(keyword in reasoning_lower for keyword in keywords):
            detected_type = expected_component
            break

    # If we detected a type in reasoning and it doesn't match the actual component, correct it
    if detected_type and detected_type != result.component:
        logger.warning(
            "[NGUI] LLM returned component='%s' but reasoning mentions '%s'. Auto-correcting.",
            result.component,
            detected_type,
        )
        result.component = detected_type
