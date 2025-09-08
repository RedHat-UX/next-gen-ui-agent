from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, Field


class ComponentDataBase(BaseModel):
    """Component Data base with really basic attributes like title and id"""

    component: Any = Field(description="component type")
    id: str = Field(description="id of the backend data this component is for")


class ComponentDataBaseWithTitle(ComponentDataBase):
    """Component Data base with really basic attributes like title and id"""

    title: str = Field(description="title of the component")


class DataFieldBase(BaseModel):
    """Base of the Component Data Field model"""

    name: str = Field(description="Field name")
    data_path: str = Field(description="JSON Path to input data")
    data: Any


DataFieldBasicDataType = Union[str | int | float | bool]
"""Basic Data Value Type - can be either str, int, float or bool"""


DataFieldSimpleValueDataType = list[DataFieldBasicDataType]
"""Simple Value Field Data item type - is always list of DataFieldBasicDataType """


class DataFieldSimpleValue(DataFieldBase):
    """Component Data with fields containing simple value obtained from the input_data."""

    data: DataFieldSimpleValueDataType = Field(
        default=[], description="Data matching `data_path` from `input_data`"
    )
    """Data matching `data_path` from `input_data`"""


class ComponentDataBaseWithSimpleValueFileds(ComponentDataBaseWithTitle):
    """Component Data base extended by fields"""

    fields: list[DataFieldSimpleValue]


DataFieldArrayValueDataType = list[
    Union[DataFieldBasicDataType, list[DataFieldBasicDataType], None]
]
"""Array Value Field Data item - is array of the DataFieldBasicDataType or list of DataFieldBasicDataType"""


class DataFieldArrayValue(DataFieldBase):
    """Component Data with fields containing array of simple values obtained from the input_data."""

    data: DataFieldArrayValueDataType = Field(
        default=[], description="Data matching `data_path` from `input_data`"
    )
    """Data matching `data_path` from `input_data`"""


# TODO do we really want data to be stored in fields, or in a complete separate field?
class ComponentDataBaseWithArrayValueFileds(ComponentDataBaseWithTitle):
    """Component Data base extended by fields"""

    fields: list[DataFieldArrayValue]


class ComponentDataAudio(ComponentDataBaseWithTitle):
    """Component Data for Audio."""

    component: Literal["audio"] = "audio"
    image: str
    audio: str


# url suffixes to detect images
# https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Formats/Image_types
# must be in lower case to get case insensitive matching, and start with dot
IMAGE_URL_SUFFIXES = (
    ".apng",  # APNG
    ".png",  # PNG
    ".avif",
    ".gif",  # GIF
    ".jpg",  # JPEG
    ".jpeg",
    ".jtif",
    ".pjpeg",
    ".pjp",
    ".svg",  # SVG
    ".webp",  # webp
    ".bmp",
    ".tif",  # tiff
    ".tiff",
)

# suffixes of the data_path (name of field in the data) to detect images
# must be in lower case to get case insensitive matching
IMAGE_DATA_PATH_SUFFIXES = (
    "imageurl",
    "image_url",
    "imagelink",
    "image_link",
    "pictureurl",
    "picture_url",
    "picturelink",
    "picture_link",
    "posterurl",
    "poster_url",
    "posterlink",
    "poster_link",
    "thumbnailurl",
    "thumbnail_url",
    "thumbnaillink",
    "thumbnail_link",
)

image_desc = f"""Image URL. It's optional field. If it's not set then image component has been choosen, but no image like path field found.
Image field value either ends by any of these extension: {IMAGE_URL_SUFFIXES},
or the field name ends by either 'url' or 'link' (case insensitive)
"""

# suffixes of the data_path (name of field in the data) to detect videos
# must be in lower case to get case insensitive matching
VIDEO_DATA_PATH_SUFFIXES = (
    "videourl",
    "video_url",
    "videolink",
    "video_link",
)


class ComponentDataImage(ComponentDataBaseWithTitle):
    """Component Data for Image"""

    component: Literal["image"] = "image"
    image: Optional[str] = Field(
        description=image_desc,
        default=None,
    )


class ComponentDataOneCard(ComponentDataBaseWithSimpleValueFileds):
    """Component Data for OneCard."""

    component: Literal["one-card"] = "one-card"
    image: Optional[str] = Field(description="Main Image URL", default=None)


class ComponentDataSetOfCards(ComponentDataBaseWithArrayValueFileds):
    """Component Data for SetOfCard."""

    component: Literal["set-of-cards"] = "set-of-cards"


class ComponentDataTable(ComponentDataBaseWithArrayValueFileds):
    """Component Data for Table."""

    component: Literal["table"] = "table"


class ComponentDataVideo(ComponentDataBaseWithTitle):
    """Component Data for Video."""

    component: Literal["video-player"] = "video-player"
    video: Optional[str] = Field(description="Video URL", default=None)
    video_img: Optional[str] = Field(
        description="URL of the Image for Video", default=None
    )


class ComponentDataHandBuildComponent(ComponentDataBase):
    """Component Data for HandBuildComponent rendered by hand-build code registered in the renderer for given `component_type`."""

    component: str = Field(
        description="type of the component to be used in renderer to select hand-build rendering implementation"
    )
    data: Any = Field(
        description="JSON backend data to be rendered by the hand-build rendering implementation"
    )
