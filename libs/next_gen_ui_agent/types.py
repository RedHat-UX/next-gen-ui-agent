from typing import NotRequired, TypedDict

from next_gen_ui_agent.model import InferenceBase


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


class DataField(TypedDict):
    """UI Component field metadata."""

    name: str
    data_path: str
    data: NotRequired[list[str]]
    """Data matching `data_path` from `input_data`"""


class UIComponentMetadata(TypedDict):
    """UI Component Mentadata."""

    id: str
    title: str
    reasonForTheComponentSelection: str
    confidenceScore: str
    component: str
    fields: list[DataField]
    rendition: NotRequired[str]
