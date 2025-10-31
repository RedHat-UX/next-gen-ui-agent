import logging
import os
from typing import Optional

from next_gen_ui_agent.agent_config import parse_config_yaml
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
from next_gen_ui_agent.data_transform.data_transformer_utils import sanitize_data_path
from next_gen_ui_agent.data_transform.types import ComponentDataBase
from next_gen_ui_agent.data_transformation import enhance_component_by_input_data
from next_gen_ui_agent.design_system_handler import (
    design_system_handler as _design_system_handler,
)
from next_gen_ui_agent.input_data_transform.input_data_transform import (
    init_input_data_transformers,
    perform_input_data_transformation,
    perform_input_data_transformation_with_transformer_name,
)
from next_gen_ui_agent.json_data_wrapper import wrap_data
from next_gen_ui_agent.model import InferenceBase
from next_gen_ui_agent.renderer.base_renderer import PLUGGABLE_RENDERERS_NAMESPACE
from next_gen_ui_agent.renderer.json.json_renderer import JsonStrategyFactory
from next_gen_ui_agent.types import (
    AgentConfig,
    AgentInput,
    InputData,
    InputDataInternal,
    UIBlockConfiguration,
    UIBlockRendering,
    UIComponentMetadata,
)
from stevedore import ExtensionManager

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
        self._extension_manager = ExtensionManager(
            namespace=PLUGGABLE_RENDERERS_NAMESPACE, invoke_on_load=True
        )
        if isinstance(config, str):
            self.config = parse_config_yaml(config)
        else:
            self.config = config

        self.inference = inference

        init_pertype_components_mapping(self.config)
        init_input_data_transformers(self.config)
        self._component_selection_strategy = self._create_component_selection_strategy()

    def _create_component_selection_strategy(self) -> ComponentSelectionStrategy:
        """Create component selection strategy based on config."""
        strategy_name = (
            self.config.component_selection_strategy
            if self.config.component_selection_strategy
            else "default"
        )

        # select which kind of components should be geneated
        unsupported_components = False
        if self.config.unsupported_components is None:
            unsupported_components = (
                os.getenv("NEXT_GEN_UI_AGENT_USE_ALL_COMPONENTS", "false").lower()
                == "true"
            )
        elif self.config.unsupported_components is True:
            unsupported_components = True

        input_data_json_wrapping = self.config.input_data_json_wrapping
        if input_data_json_wrapping is None:
            input_data_json_wrapping = True

        if strategy_name == "default" or strategy_name == "one_llm_call":
            return OnestepLLMCallComponentSelectionStrategy(
                unsupported_components,
                input_data_json_wrapping=input_data_json_wrapping,
            )
        elif strategy_name == "two_llm_calls":
            return TwostepLLMCallComponentSelectionStrategy(
                unsupported_components,
                input_data_json_wrapping=input_data_json_wrapping,
            )
        else:
            raise ValueError(
                f"Unknown component_selection_strategy in config: {strategy_name}"
            )

    def __setattr__(self, name, value):
        if name == "_extension_manager":
            super().__setattr__(name, value)
            self.renderers = ["json"] + self._extension_manager.names()
            logger.info("Registered renderers: %s", self.renderers)
        else:
            super().__setattr__(name, value)

    async def component_selection(
        self, input: AgentInput, inference: Optional[InferenceBase] = None
    ) -> list[UIComponentMetadata]:
        """STEP 2: Select component and generate its configuration metadata."""

        # select per type configured components, for rest run LLM powered component selection, then join results together
        ret: list[UIComponentMetadata] = []
        to_dynamic_selection: list[InputData] = []
        for input_data in input["input_data"]:
            json_data, input_data_transformer_name = perform_input_data_transformation(
                input_data
            )

            # select component InputData.type or InputData.hand_build_component_type
            component = select_component_per_type(input_data, json_data)
            if component:
                component.input_data_transformer_name = input_data_transformer_name
                ret.append(component)
            else:
                # Copy input_data and just add a json_data
                id: InputDataInternal = {
                    **input_data,
                    "json_data": json_data,
                    "input_data_transformer_name": input_data_transformer_name,
                }
                to_dynamic_selection.append(id)

        if to_dynamic_selection:
            inference = inference if inference else self.inference
            if not inference:
                raise ValueError(
                    "config field 'inference' is not defined neither in input parameter nor agent's config"
                )

            input_to_dynamic_selection = AgentInput(
                user_prompt=input["user_prompt"], input_data=to_dynamic_selection
            )
            from_dynamic_selection = (
                await self._component_selection_strategy.select_components(
                    inference, input_to_dynamic_selection
                )
            )
            ret.extend(from_dynamic_selection)

        return ret

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

    def data_transformation(
        self, input_data: list[InputData], components: list[UIComponentMetadata]
    ) -> list[ComponentDataBase]:
        """STEP 3: Transform generated component configuration metadata into component data. Mainly pick up showed data values from `input_data`."""
        return enhance_component_by_input_data(
            input_data=input_data, components=components
        )

    def design_system_handler(
        self,
        components: list[ComponentDataBase],
        component_system: Optional[str] = None,
    ) -> list[UIBlockRendering]:
        """STEP 4: Render the component with the chosen component system,
        either via AgentConfig or parameter provided to this method."""

        component_system = (
            component_system if component_system else self.config.component_system
        )
        if not component_system:
            raise Exception("Component system not defined")

        factory = JsonStrategyFactory()
        if component_system == "json":
            pass
        elif component_system not in self._extension_manager.names():
            raise ValueError(
                f"configured component system '{component_system}' is not present in extension_manager. "
                + "Make sure you install appropriate dependency"
            )
        else:
            factory = self._extension_manager[component_system].obj

        return _design_system_handler(components, factory)

    def construct_UIBlockConfiguration(
        self, input_data: InputData, component_metadata: UIComponentMetadata
    ) -> UIBlockConfiguration:
        """
        Construct `UIBlockConfiguration` for component_metadata and input_data,
        so #refresh_component() can be used later to refresh the component configuration for new input_data.

        It should be returned from AI framework/protocol binding so *Controlling Assistant* can send it back later when it needs to refresh component for the new data.
        """

        # put sanitized data paths to the UIBlockConfiguration
        if component_metadata.fields:
            for field in component_metadata.fields:
                field.data_path = sanitize_data_path(field.data_path)  # type: ignore

        return UIBlockConfiguration(
            component_metadata=component_metadata,
            data_type=input_data.get("type"),
            input_data_transformer_name=component_metadata.input_data_transformer_name,
            json_wrapping_field_name=component_metadata.json_wrapping_field_name,
        )
