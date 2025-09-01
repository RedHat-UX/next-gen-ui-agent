import logging
import os
from typing import Optional

from next_gen_ui_agent.component_selection import (
    OnestepLLMCallComponentSelectionStrategy,
)
from next_gen_ui_agent.component_selection_twostep import (
    TwostepLLMCallComponentSelectionStrategy,
)
from next_gen_ui_agent.data_transform.types import ComponentDataBase
from next_gen_ui_agent.data_transformation import enhance_component_by_input_data
from next_gen_ui_agent.design_system_handler import (
    design_system_handler as _design_system_handler,
)
from next_gen_ui_agent.model import InferenceBase
from next_gen_ui_agent.renderer.base_renderer import PLUGGABLE_RENDERERS_NAMESPACE
from next_gen_ui_agent.renderer.json.json_renderer import JsonStrategyFactory
from next_gen_ui_agent.types import (
    AgentConfig,
    AgentInput,
    ComponentSelectionStrategy,
    InputData,
    Rendition,
    UIComponentMetadata,
    UIComponentMetadataHandBuildComponent,
)
from stevedore import ExtensionManager

logger = logging.getLogger(__name__)


class NextGenUIAgent:
    """Next Gen UI Agent."""

    def __init__(self, config: AgentConfig = AgentConfig()):
        self._extension_manager = ExtensionManager(
            namespace=PLUGGABLE_RENDERERS_NAMESPACE, invoke_on_load=True
        )
        self.config = config
        self._hand_build_components_mapping = self.config.get(
            "hand_build_components_mapping"
        )
        self._component_selection_strategy = self._create_component_selection_strategy()

    def _create_component_selection_strategy(self) -> ComponentSelectionStrategy:
        """Create component selection strategy based on config."""
        strategy_name = self.config.get("component_selection_strategy", "default")

        # select which kind of components should be geneated
        if "unsupported_components" not in self.config.keys():
            unsupported_components = (
                os.getenv("NEXT_GEN_UI_AGENT_USE_ALL_COMPONENTS", "false").lower()
                == "true"
            )
        else:
            unsupported_components = self.config.get("unsupported_components", False)

        if strategy_name == "default" or strategy_name == "one_llm_call":
            return OnestepLLMCallComponentSelectionStrategy(unsupported_components)
        elif strategy_name == "two_llm_calls":
            return TwostepLLMCallComponentSelectionStrategy(unsupported_components)
        else:
            raise ValueError(f"Unknown component_selection_strategy: {strategy_name}")

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
        """Generate component metadata."""
        inference = inference if inference else self.config.get("inference")
        if not inference:
            raise ValueError(
                "config field 'inference' is not defined neither in input parameter nor agent's config"
            )

        # select hand build components for items where defined, for rest run LLM powered component selection, then join results together
        ret: list[UIComponentMetadata] = []
        to_dynamic_selection: list[InputData] = []
        for input_data in input["input_data"]:
            hbc = self._select_hand_build_component(input_data)
            if hbc:
                ret.append(hbc)
            else:
                to_dynamic_selection.append(input_data)

        if to_dynamic_selection:
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
        """Transform components to Agent Data Output."""
        return enhance_component_by_input_data(
            input_data=input_data, components=components
        )

    def design_system_handler(
        self,
        components: list[ComponentDataBase],
        component_system: Optional[str] = None,
    ) -> list[Rendition]:
        """Handle rendering of the component with the chosen component system
        either via config or parameter."""

        component_system = (
            component_system
            if component_system
            else self.config.get("component_system")
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

    def _select_hand_build_component(
        self, input_data: InputData
    ) -> Optional[UIComponentMetadataHandBuildComponent]:
        """Select hand-build component based on input data type."""
        if "type" in input_data:
            type = input_data["type"]
            if (
                self._hand_build_components_mapping
                and type
                and type in self._hand_build_components_mapping
            ):
                return UIComponentMetadataHandBuildComponent.model_validate(
                    {
                        "id": input_data["id"],
                        "title": "",
                        "component": "hand-build-component",
                        "component_type": self._hand_build_components_mapping[type],
                        "fields": [],
                    }
                )
        return None
