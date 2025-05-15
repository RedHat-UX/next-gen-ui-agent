from typing import Any, Literal, Optional

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


class ComponentDataBase(BaseModel):
    """Component Data base with really basic attributes like title and id"""

    component: Any
    id: str
    title: str


class ComponentDataBaseWithFileds(ComponentDataBase):
    """Component Data base extended by fields"""

    fields: list[DataField]


class ComponentDataAudio(ComponentDataBase):
    """Component Data for Audio."""

    component: Literal["audio"] = "audio"
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


class ComponentDataImage(ComponentDataBase):
    """Component Data for Image"""

    component: Literal["image"] = "image"
    image: Optional[str] = Field(
        description=image_desc,
        default=None,
    )


class ComponentDataOneCard(ComponentDataBaseWithFileds):
    """Component Data for OneCard."""

    component: Literal["one-card"] = "one-card"
    image: Optional[str] = Field(description="Image URL", default=None)
    """Image URL"""


class ComponentDataSetOfCard(ComponentDataBaseWithFileds):
    """Component Data for SetOfCard."""

    component: Literal["set-of-cards"] = "set-of-cards"
    image_field: DataField
    subtitle_field: DataField


class ComponentDataVideo(ComponentDataBase):
    """Component Data for Video."""

    component: Literal["video-player"] = "video-player"
    video: str
    video_img: str
