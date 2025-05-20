import logging
from typing import Optional

from next_gen_ui_agent.component_selection import component_selection as comp_sel
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
    InputData,
    Rendition,
    UIComponentMetadata,
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
        return await comp_sel(inference=inference, input=input)

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
