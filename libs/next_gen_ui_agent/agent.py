import logging
logger = logging.getLogger(__name__)

from next_gen_ui_agent.base_renderer import (
    PLUGGABLE_RENDERERS_NAMESPACE,
    JsonStrategyFactory,
)
from stevedore import ExtensionManager

from .component_selection import component_selection as comp_sel
from .data_transformation import enhance_component_by_input_data
from .design_system_handler import design_system_handler as _design_system_handler
from .model import InferenceBase
from .types import AgentInput, InputData, UIComponentMetadata


class NextGenUIAgent:
    """Next Gen UI Agent."""

    def __init__(self):
        self._extension_manager = ExtensionManager(
            namespace=PLUGGABLE_RENDERERS_NAMESPACE, invoke_on_load=True
        )

    async def component_selection(
        self,
        inference: InferenceBase,
        input: AgentInput,
    ) -> list[UIComponentMetadata]:
        """Generate component metadata."""
        return await comp_sel(inference=inference, input=input)

    def data_transformation(
        self, input_data: list[InputData], components: list[UIComponentMetadata]
    ) -> list[UIComponentMetadata]:
        """Transform components to Agent Data Output."""
        enhance_component_by_input_data(input_data=input_data, components=components)
        return components

    def design_system_handler(
        self, components: list[UIComponentMetadata], component_system: str
    ) -> list[UIComponentMetadata]:
        """Handle rendering of the component with the chosen component
        system."""

        factory = None
        if not component_system:
            factory = JsonStrategyFactory()
        elif component_system not in self._extension_manager.names():
            logger.exception(
                "Chosen component system %s has not been configured with NextGenUI. The default JSON output will be used instead", component_system
            )
            factory = JsonStrategyFactory()
        else:
            factory = self._extension_manager[component_system].obj

        return _design_system_handler(components, factory or JsonStrategyFactory())
