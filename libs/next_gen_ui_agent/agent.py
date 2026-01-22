import logging
from typing import Optional

from next_gen_ui_agent.agent_config import parse_config_yaml
from next_gen_ui_agent.all_fields_collector import generate_all_fields
from next_gen_ui_agent.component_selection_llm_onestep import (
    OnestepLLMCallComponentSelectionStrategy,
)
from next_gen_ui_agent.component_selection_llm_strategy import (
    ComponentSelectionStrategy,
)
from next_gen_ui_agent.component_selection_llm_twostep import (
    TwostepLLMCallComponentSelectionStrategy,
)
from next_gen_ui_agent.component_selection_pertype import (
    init_pertype_components_mapping,
    select_component_per_type,
)
from next_gen_ui_agent.data_transform.data_transformer_utils import (
    extract_data_key_from_path,
    generate_field_id,
    sanitize_data_path,
)
from next_gen_ui_agent.data_transform.types import ComponentDataBase
from next_gen_ui_agent.data_transformation import generate_component_data
from next_gen_ui_agent.design_system_handler import (
    get_component_system_factory,
    get_component_system_names,
    render_component,
)
from next_gen_ui_agent.inference.inference_base import InferenceBase
from next_gen_ui_agent.input_data_transform.input_data_transform import (
    init_input_data_transformers,
    perform_input_data_transformation,
    perform_input_data_transformation_with_transformer_name,
)
from next_gen_ui_agent.json_data_wrapper import wrap_data
from next_gen_ui_agent.types import (
    AgentConfig,
    AgentConfigDataType,
    InputData,
    InputDataInternal,
    UIBlockComponentMetadata,
    UIBlockConfiguration,
    UIBlockRendering,
    UIComponentMetadata,
)

logger = logging.getLogger(__name__)


class NextGenUIAgent:
    """Next Gen UI Agent."""

    def __init__(
        self,
        inference: InferenceBase | None = None,
        config: AgentConfig | str = AgentConfig(),
    ):
        """
        Initialize NextGenUIAgent.

        * `config` - agent config either `AgentConfig` or string with YAML configuraiton.
        """
        if isinstance(config, str):
            self.config = parse_config_yaml(config)
        else:
            self.config = config

        self.inference = inference

        renderers = get_component_system_names()
        logger.info("Registered renderers: %s", renderers)
        if self.config.component_system and self.config.component_system != "json":
            if self.config.component_system not in renderers:
                raise ValueError(
                    f"Configured component system '{self.config.component_system}' is not found. "
                    + "Make sure you install appropriate dependency."
                )

        init_pertype_components_mapping(self.config)
        init_input_data_transformers(self.config)
        self._component_selection_strategy = self._create_component_selection_strategy()

    def _create_component_selection_strategy(self) -> ComponentSelectionStrategy:
        """Create component selection strategy based on config."""

        if self.config.component_selection_strategy == "two_llm_calls":
            return TwostepLLMCallComponentSelectionStrategy(config=self.config)
        else:
            return OnestepLLMCallComponentSelectionStrategy(config=self.config)

    async def select_component(
        self,
        user_prompt: str,
        input_data: InputData,
        inference: Optional[InferenceBase] = None,
    ) -> UIComponentMetadata:
        """STEP 2: Select component and generate its configuration metadata."""

        # select per type configured components, for rest run LLM powered component selection, then join results together
        json_data, input_data_transformer_name = perform_input_data_transformation(
            input_data
        )

        # select component InputData.type or InputData.hand_build_component_type
        component = select_component_per_type(input_data, json_data)
        if component:
            component.input_data_transformer_name = input_data_transformer_name
            component.input_data_type = input_data.get("type")
        else:
            inference = inference if inference else self.inference
            if not inference:
                raise ValueError(
                    "Inference is not defined neither as an input parameter nor as an agent's config"
                )

            input_data_for_strategy: InputDataInternal = {
                **input_data,
                "json_data": json_data,
                "input_data_transformer_name": input_data_transformer_name,
            }
            component = await self._component_selection_strategy.select_component(
                inference, user_prompt, input_data_for_strategy
            )

        # Apply formatters and handlers from config if available
        component = self._apply_config_formatters(component, input_data.get("type"))
        component = self._apply_config_handlers(component, input_data.get("type"))
        return component

    def _get_data_type_config(
        self, data_type: Optional[str]
    ) -> Optional[AgentConfigDataType]:
        """Get data type configuration if available."""
        if not data_type or not self.config.data_types:
            return None
        return self.config.data_types.get(data_type)

    def _match_formatter_pattern(
        self, data_key: str, formatter_overrides: dict[str, str]
    ) -> Optional[str]:
        """
        Match data_key against wildcard patterns in formatter_overrides.

        Supports patterns:
        - "*url*" matches any key containing "url" (e.g., "url", "api_url", "monitoring_dashboard_url")
        - "url*" matches keys starting with "url" (e.g., "url", "url_path")
        - "*url" matches keys ending with "url" (e.g., "url", "api_url")

        Returns the formatter ID if a pattern matches, None otherwise.
        Pattern matching is case-insensitive.
        """
        data_key_lower = data_key.lower()

        for pattern, formatter_id in formatter_overrides.items():
            # Skip non-pattern keys (already checked in exact/case-insensitive match)
            if "*" not in pattern:
                continue

            pattern_lower = pattern.lower()

            # Convert wildcard pattern to regex-like matching
            if pattern_lower.startswith("*") and pattern_lower.endswith("*"):
                # Pattern: "*url*" - contains match
                substring = pattern_lower.strip("*")
                if substring in data_key_lower:
                    return formatter_id
            elif pattern_lower.startswith("*"):
                # Pattern: "*url" - ends with match
                suffix = pattern_lower[1:]  # Remove leading *
                if data_key_lower.endswith(suffix):
                    return formatter_id
            elif pattern_lower.endswith("*"):
                # Pattern: "url*" - starts with match
                prefix = pattern_lower[:-1]  # Remove trailing *
                if data_key_lower.startswith(prefix):
                    return formatter_id

        return None

    def _apply_config_formatters(
        self, component: UIComponentMetadata, data_type: Optional[str]
    ) -> UIComponentMetadata:
        """
        Apply formatters from AgentConfig.data_types.formatter_overrides if configured.
        If no explicit override exists, automatically extracts formatter ID from the field's
        data_path (e.g., "$.pods[*].cpu_usage" -> "cpu_usage").
        """
        if not component.fields or not data_type:
            return component

        data_type_config = self._get_data_type_config(data_type)
        formatter_overrides = (
            data_type_config.formatter_overrides if data_type_config else None
        )

        for field in component.fields:
            # Skip if field already has a formatter
            if field.formatter and field.formatter not in ("null", ""):
                continue

            # Extract data key from data_path
            data_key = extract_data_key_from_path(field.data_path)
            if not data_key:
                continue

            # Try explicit override (exact match, then case-insensitive, then pattern match)
            formatter = None
            if formatter_overrides:
                # 1. Try exact match
                formatter = formatter_overrides.get(data_key)
                if not formatter:
                    # 2. Try case-insensitive match
                    formatter = next(
                        (
                            v
                            for k, v in formatter_overrides.items()
                            if "*" not in k and k.lower() == data_key.lower()
                        ),
                        None,
                    )
                if not formatter:
                    # 3. Try pattern match (wildcard patterns like "*url*", "url*", "*url")
                    formatter = self._match_formatter_pattern(
                        data_key, formatter_overrides
                    )

            # Fallback to auto-detect (use data key as formatter)
            if not formatter:
                formatter = data_key

            field.formatter = formatter

        return component

    def _apply_config_handlers(
        self, component: UIComponentMetadata, data_type: Optional[str]
    ) -> UIComponentMetadata:
        """
        Apply handlers (e.g., on_row_click) from AgentConfig.data_types if configured.
        """
        if not data_type:
            return component

        data_type_config = self._get_data_type_config(data_type)
        if not data_type_config or not data_type_config.on_row_click:
            return component

        # Apply on_row_click if component is a table and doesn't already have one
        if component.component == "table" and (
            not component.on_row_click or component.on_row_click == ""
        ):
            component.on_row_click = data_type_config.on_row_click

        return component

    async def refresh_component(
        self, input_data: InputData, block_configuration: UIBlockConfiguration
    ) -> UIComponentMetadata:
        """STEP 2a: Refresh component configuration metadata for new `input_data` using previous `block_configuration`."""

        if not block_configuration.input_data_transformer_name:
            raise KeyError(
                "Input data transformer name missing in the block configuration"
            )

        if not block_configuration.component_metadata:
            raise KeyError("Component metadata missing in the block configuration")

        json_data = perform_input_data_transformation_with_transformer_name(
            input_data, block_configuration.input_data_transformer_name
        )

        json_data = wrap_data(json_data, block_configuration.json_wrapping_field_name)

        return UIComponentMetadata(
            **block_configuration.component_metadata.model_dump(),
            json_data=json_data,
            input_data_transformer_name=block_configuration.input_data_transformer_name,
            json_wrapping_field_name=block_configuration.json_wrapping_field_name,
            input_data_type=input_data.get("type"),
        )

    def transform_data(
        self, input_data: InputData, component: UIComponentMetadata
    ) -> ComponentDataBase:
        """STEP 3: Transform generated component configuration metadata into component data. Mainly pick up showed data values from `input_data`."""
        return generate_component_data(input_data, component)

    def generate_rendering(
        self, component: ComponentDataBase, component_system: Optional[str] = None
    ) -> UIBlockRendering:
        """STEP 4: Render the component with the chosen component system,
        either via AgentConfig or parameter provided to this method."""
        component_system = (
            component_system if component_system else self.config.component_system
        )
        if not component_system:
            raise Exception("Component system not defined")

        return render_component(
            component, get_component_system_factory(component_system)
        )

    def construct_UIBlockConfiguration(
        self, input_data: InputData, component_metadata: UIComponentMetadata
    ) -> UIBlockConfiguration:
        """
        Construct `UIBlockConfiguration` for component_metadata and input_data,
        so #refresh_component() can be used later to refresh the component configuration for new input_data.

        It should be returned from AI framework/protocol binding so *Controlling Assistant* can send it back later when it needs to refresh component for the new data.
        """

        block_component_metadata = UIBlockComponentMetadata(
            **component_metadata.model_dump(),
        )

        # put sanitized data paths to the UIBlockConfiguration
        if block_component_metadata.fields:
            for field in block_component_metadata.fields:
                field.data_path = sanitize_data_path(field.data_path)  # type: ignore
                field.id = generate_field_id(field.data_path)

        data_type = input_data.get("type")
        generate_for_data_type = (
            data_type
            and self.config.data_types
            and self.config.data_types.get(data_type)
            and self.config.data_types.get(data_type).generate_all_fields  # type: ignore
        )
        if (
            self.config.generate_all_fields and generate_for_data_type is not False
        ) or generate_for_data_type is True:
            block_component_metadata.fields_all = generate_all_fields(
                component_metadata
            )

        return UIBlockConfiguration(
            component_metadata=block_component_metadata,
            data_type=input_data.get("type"),
            input_data_transformer_name=component_metadata.input_data_transformer_name,
            json_wrapping_field_name=component_metadata.json_wrapping_field_name,
        )

    def component_info(self, uiblock_config: UIBlockConfiguration | None) -> str:
        if not uiblock_config:
            return ""
        c_info = []
        if uiblock_config.data_type:
            c_info.append(f"data_type: '{uiblock_config.data_type}'")
        if uiblock_config.component_metadata:
            c_info.append(f"title: '{uiblock_config.component_metadata.title}'")
            c_info.append(
                f"component_type: {uiblock_config.component_metadata.component}"
            )
        return ", ".join(c_info)
