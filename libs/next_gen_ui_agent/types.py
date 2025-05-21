from typing import NotRequired, Optional, TypedDict

from next_gen_ui_agent.model import InferenceBase
from pydantic import BaseModel, ConfigDict, Field


# Intentionaly TypeDict because of passing ABC class InferenceBase
class AgentConfig(TypedDict):
    """Agent Configuration."""

    inference: NotRequired[InferenceBase]
    component_system: NotRequired[str]


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
