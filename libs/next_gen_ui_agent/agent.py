from .component_selection import component_selection as comp_sel
from .data_transformation import enhance_component_by_input_data
from .datamodel import AgentInput, InputData, UIComponentMetadata
from .model import InferenceBase


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
