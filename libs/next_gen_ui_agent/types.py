from typing import Any, NotRequired, Optional, TypedDict, Union

from next_gen_ui_agent.model import InferenceBase
from pydantic import BaseModel


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


# TODO: Check data_transformation how types are handled
DataFieldDataType = Union[str | int | Any]
"""Field Data item can be either str or int"""


class DataField(BaseModel):
    """UI Component field metadata."""

    name: str
    data_path: str
    data: list[DataFieldDataType] = []
    """Data matching `data_path` from `input_data`"""


class UIComponentMetadata(BaseModel):
    """UI Component Mentadata."""

    id: Optional[str] = None
    title: str
    reasonForTheComponentSelection: Optional[str] = None
    confidenceScore: Optional[str] = None
    component: str
    fields: list[DataField]
    rendition: Optional[str] = None
