from .component_selection import component_selection as comp_sel
from .data_transformation import enhance_component_by_input_data
from .design_system_handler import design_system_handler as _design_system_handler
from .model import InferenceBase
from .types import AgentInput, InputData, UIComponentMetadata


class NextGenUIAgent:
    """Next Gen UI Agent."""

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
        return _design_system_handler(components, component_system)
