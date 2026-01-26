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

        # Try single-component or HBC selection first (no LLM needed)
        component = select_component_per_type(input_data, json_data)
        if component:
            component.input_data_transformer_name = input_data_transformer_name
            component.input_data_type = input_data.get("type")
            return component

        # LLM-based component selection (unified for both data_type-specific and global)
        data_type = input_data.get("type")
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

        # Single unified call to strategy
        # Strategy will extract data_type from input_data and determine components internally
        component = await self._component_selection_strategy.select_component(
            inference, user_prompt, input_data_for_strategy
        )
        component.input_data_transformer_name = input_data_transformer_name
        component.input_data_type = data_type
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
