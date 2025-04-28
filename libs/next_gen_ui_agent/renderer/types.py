from typing import Optional

from next_gen_ui_agent.types import DataField
from pydantic import BaseModel


class RenderContextBase(BaseModel):
    """Rendering Context."""

    title: str
    fields: list[DataField]
    field_names: list[str]
    data_length: int


class RenderContextAudio(RenderContextBase):
    """Rendering Context for Audio."""

    image: str
    audio: str


class RenderContextImage(RenderContextBase):
    """Rendering Context for Image."""

    image: str


class RenderContextOneCard(RenderContextBase):
    """Rendering Context for OneCard."""

    image: Optional[str] = None


class RenderContexSetOfCard(RenderContextBase):
    """Rendering Context for SetOfCard."""

    image_field: DataField
    subtitle_field: DataField


class RenderContextVideo(RenderContextBase):
    """Rendering Context for Video."""

    video: str
    video_img: str
