import logging
import os
from typing import Optional

from next_gen_ui_agent.agent_config import parse_config_yaml
from next_gen_ui_agent.component_selection_llm_onestep import (
    OnestepLLMCallComponentSelectionStrategy,
)
from next_gen_ui_agent.component_selection_llm_twostep import (
    TwostepLLMCallComponentSelectionStrategy,
)
from next_gen_ui_agent.component_selection_pertype import (
    init_pertype_components_mapping,
    select_component_per_type,
)
from next_gen_ui_agent.data_transform.types import ComponentDataBase
from next_gen_ui_agent.data_transformation import enhance_component_by_input_data
from next_gen_ui_agent.design_system_handler import (
    design_system_handler as _design_system_handler,
)
from next_gen_ui_agent.input_data_transform.input_data_transform import (
    init_input_data_transformers,
    perform_input_data_transformation,
)
from next_gen_ui_agent.model import InferenceBase
from next_gen_ui_agent.renderer.base_renderer import PLUGGABLE_RENDERERS_NAMESPACE
from next_gen_ui_agent.renderer.json.json_renderer import JsonStrategyFactory
from next_gen_ui_agent.types import (
    AgentConfig,
    AgentInput,
    ComponentSelectionStrategy,
    InputData,
    InputDataInternal,
    Rendition,
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
        """STEP 1: Select component and generate its configuration metadata."""

        # select per type configured components, for rest run LLM powered component selection, then join results together
        ret: list[UIComponentMetadata] = []
        to_dynamic_selection: list[InputData] = []
        for input_data in input["input_data"]:
            json_data = perform_input_data_transformation(input_data)

            # select component InputData.type or InputData.hand_build_component_type
            component = select_component_per_type(input_data, json_data)
            if component:
                ret.append(component)
            else:
                # Copy input_data and just add a json_data
                id: InputDataInternal = {
                    **input_data,
                    "json_data": json_data,
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

    def data_transformation(
        self, input_data: list[InputData], components: list[UIComponentMetadata]
    ) -> list[ComponentDataBase]:
        """STEP 2: Transform generated metadata into component metadata including data values taken from InputData JSON."""
        return enhance_component_by_input_data(
            input_data=input_data, components=components
        )

    def design_system_handler(
        self,
        components: list[ComponentDataBase],
        component_system: Optional[str] = None,
    ) -> list[Rendition]:
        """STEP 3: Render the component with the chosen component system,
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
