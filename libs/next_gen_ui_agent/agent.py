from .component_selection import component_selection as comp_sel
from .datamodel import AgentInput, UIComponentMetadata
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
