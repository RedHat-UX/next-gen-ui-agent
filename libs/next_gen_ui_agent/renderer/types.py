from typing import Optional

from next_gen_ui_agent.types import DataField
from pydantic import BaseModel, Field
from pydantic._internal._core_utils import CoreSchemaOrField, is_core_schema
from pydantic.json_schema import GenerateJsonSchema


class CustomGenerateJsonSchema(GenerateJsonSchema):
    """Custom JSON Schema Generator. Omits title field for cleaner types generation"""

    def field_title_should_be_set(self, schema: CoreSchemaOrField) -> bool:
        return_value = super().field_title_should_be_set(schema)
        if return_value and is_core_schema(schema):
            return False
        return return_value


class RenderContextBaseTitle(BaseModel):
    """Rendering Context base title only"""

    title: str


class RenderContextBase(RenderContextBaseTitle):
    """Rendering Context base with title and fields"""

    fields: list[DataField]
    field_names: list[str]
    data_length: int = Field(description="Maximal count of items in any data field")
    """Maximal count of items in any data field"""


class RenderContextAudio(RenderContextBaseTitle):
    """Rendering Context for Audio."""

    image: str
    audio: str


# https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Formats/Image_types
IMAGE_SUFFIXES = (
    "apng",  # APNG
    "png",  # PNG
    "avif",
    "gif",  # GIF
    "jpg",  # JPEG
    "jpeg",
    "jtif",
    "pjpeg",
    "pjp",
    "svg",  # SVG
    "webp",  # webp
    "bmp",
    "tif",  # tiff
    "tiff",
)

image_desc = f"""Image URL. It's optional field. If it's not set then image component has been choosen, but no image like path field found.
Image field value either ends by any of these extension: {IMAGE_SUFFIXES},
or the field name ends by either 'url' or 'link' (case insensitive)
"""


class RenderContextImage(RenderContextBaseTitle):
    """Rendering Context for Image"""

    image: Optional[str] = Field(
        description=image_desc,
        default=None,
    )


class RenderContextOneCard(RenderContextBase):
    """Rendering Context for OneCard."""

    image: Optional[str] = Field(description="Image URL", default=None)
    """Image URL"""


class RenderContexSetOfCard(RenderContextBase):
    """Rendering Context for SetOfCard."""

    image_field: DataField
    subtitle_field: DataField


class RenderContextVideo(RenderContextBaseTitle):
    """Rendering Context for Video."""

    video: str
    video_img: str
