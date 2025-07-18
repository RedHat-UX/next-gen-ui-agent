from abc import ABC, abstractmethod
from typing import NotRequired, Optional, TypedDict

from next_gen_ui_agent.model import InferenceBase
from pydantic import BaseModel, ConfigDict, Field


# Intentionaly TypeDict because of passing ABC class InferenceBase
class AgentConfig(TypedDict):
    """Agent Configuration."""

    inference: NotRequired[InferenceBase]
    """Inference to use to call LLM by the agent."""
    component_system: NotRequired[str]
    """Component system to use to render the component."""
    unsupported_components: NotRequired[bool]
    """
    If `False` (default), the agent can generate only fully supported UI components.
    If `True`, the agent can also generate unsupported UI components.
    """
    component_selection_strategy: NotRequired[str]
    """
    Component selection strategy to use.
    Possible values:
    - default - use the default implementation
    - one_llm_call - use the one LLM call implementation from component_selection.py
    - two_llm_calls - use the two LLM calls implementation from component_selection_twostep.py
    """


class InputData(TypedDict):
    """Agent Input Data."""

    id: str
    data: str


class AgentInput(TypedDict):
    """Agent Input."""

    user_prompt: str
    input_data: list[InputData]


class DataField(BaseModel):
    """UI Component field metadata."""

    model_config = ConfigDict(title="RenderContextDataField")

    name: str = Field(description="Field name")
    data_path: str = Field(description="JSON Path to input data")
    """JSON Path to input data"""


class UIComponentMetadata(BaseModel):
    """UI Component Mentadata."""

    id: Optional[str] = None
    title: str
    reasonForTheComponentSelection: Optional[str] = None
    confidenceScore: Optional[str] = None
    component: str
    fields: list[DataField]


class Rendition(BaseModel):
    """Rendition of the component."""

    id: str
    component_system: str
    mime_type: str
    content: str


class ComponentSelectionStrategy(ABC):
    """Abstract base class for LLM-based component selection and configuration strategies."""

    @abstractmethod
    async def select_components(
        self, inference: InferenceBase, input: AgentInput
    ) -> list[UIComponentMetadata]:
        """Select UI components based on input data and user prompt."""
        pass

    @abstractmethod
    async def perform_inference(
        self,
        user_prompt: str,
        inference: InferenceBase,
        input_data: InputData,
    ) -> list[str]:
        """Perform inference to select UI components and configure them. Multiple LLM calls can be performed and inference results can be returned as a list of strings."""
        pass

    @abstractmethod
    def parse_infernce_output(
        self, inference_output: list[str], input_data: InputData
    ) -> UIComponentMetadata:
        """Parse LLM inference outputs from `perform_inference` and return UIComponentMetadata or throw exception if it can't be constructed because of invalid LLM outputs."""
        pass
