from enum import Enum
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


# TODO Start using ComponentName enum
class ComponentName(Enum):
    ONE_CARD = "one-card"
    TABLE = "table"
    SET_OF_CARDS = "set-of-cards"


class UIComponentMetadata(TypedDict):
    """UI Component Mentadata."""

    id: str
    title: str
    reasonForTheComponentSelection: str
    confidenceScore: str
    component: str
    """Value of types.ComponentName"""
    fields: list[DataField]
    rendition: NotRequired[str]


class RenderContextBase(TypedDict):
    """Rendering Context."""

    title: str
    fields: list[DataField]
    field_names: list[str]
    data_length: int


class RenderContextOneCard(RenderContextBase):
    """Rendering Context for OneCard."""

    image: NotRequired[str]


class RenderContexSetOfCard(RenderContextBase):
    """Rendering Context for SetOfCard."""

    image_field: DataField
    subtitle_field: DataField


class RenderContextImage(RenderContextBase):
    """Rendering Context for Image."""

    image: str


class RenderContextVideo(RenderContextBase):
    """Rendering Context for Video."""

    video: str
    video_img: str


class RenderContextAudio(RenderContextBase):
    """Rendering Context for Audio."""

    image: str
    audio: str
