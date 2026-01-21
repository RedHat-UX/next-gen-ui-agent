from typing import Annotated, Any, Literal, Optional, Union
from uuid import uuid4

from pydantic import BaseModel, Discriminator, Field


class ComponentDataBase(BaseModel):
    """Component Data base with really basic attributes like title and id"""

    component: Any = Field(description="component type")
    id: str = Field(description="id of the backend data this component is for")
    input_data_type: Optional[str] = Field(
        default=None,
        description="Optional type of the input data. Can be used for frontend customization of the component for concrete data type, eg. by using it in CSS class names.",
    )


class ComponentDataBaseWithTitle(ComponentDataBase):
    """Component Data base with really basic attributes like title and id"""

    title: str = Field(description="title of the component")


class DataFieldBase(BaseModel):
    """Base of the Component Data Field model"""

    id: str = Field(description="Field ID", default_factory=lambda: uuid4().hex)
    name: str = Field(description="Field name")
    data_path: str = Field(description="JSON Path to input data")
    data: Any


DataFieldBasicDataType = Union[str | int | float | bool]
"""Basic Data Value Type - can be either str, int, float or bool"""


DataFieldSimpleValueDataType = list[DataFieldBasicDataType]
"""Simple Value Field Data item type - is always list of DataFieldBasicDataType """


class DataFieldSimpleValue(DataFieldBase):
    """
    Component field description with data containing one value obtained from the input_data to be rendered as a dynamic component of the "one object" type.
    The data value can be simple value or arrays of simple values to be rendered as a one field of the UI component.
    """

    data: DataFieldSimpleValueDataType = Field(
        default=[], description="Data matching `data_path` from `input_data`"
    )
    """Data matching `data_path` from `input_data`"""
    formatter: Optional[str] = Field(
        default=None,
        description="Optional identifier for a formatter function to customize cell rendering. The formatter should be registered in the frontend component registry.",
    )
    """Optional identifier for a formatter function to customize cell rendering"""


class ComponentDataBaseWithSimpleValueFileds(ComponentDataBaseWithTitle):
    """Component Data base extended by fields"""

    fields: list[DataFieldSimpleValue]


DataFieldArrayValueDataType = list[
    Union[DataFieldBasicDataType, list[DataFieldBasicDataType], None]
]
"""Array Value Field Data item - is array of the DataFieldBasicDataType or list of DataFieldBasicDataType"""


class DataFieldArrayValue(DataFieldBase):
    """
    Component field description with data containing array of values obtained from the input_data to be rendered as a dynamic component of the "array of objects" type.
    Every item of the data array should be rendered as a table row or a card in the set of cards UI component.
    Individual data values in the array can be simple values or arrays of simple values to be rendered as a one field of the row/card.
    """

    data: DataFieldArrayValueDataType = Field(
        default=[], description="Data matching `data_path` from `input_data`"
    )
    """Data matching `data_path` from `input_data`"""
    formatter: Optional[str] = Field(
        default=None,
        description="Optional identifier for a formatter function to customize cell rendering. The formatter should be registered in the frontend component registry.",
    )
    """Optional identifier for a formatter function to customize cell rendering"""


# TODO do we really want data to be stored in fields, or in a complete separate field?
class ComponentDataBaseWithArrayValueFileds(ComponentDataBaseWithTitle):
    """Component Data base extended by fields"""

    fields: list[DataFieldArrayValue]


class ComponentDataAudio(ComponentDataBaseWithTitle):
    """Component Data for Audio."""

    component: Literal["audio"] = "audio"
    image: str
    audio: str


class ChartDataPoint(BaseModel):
    """A single data point in a chart series"""

    name: Optional[str] = Field(
        default=None, description="Optional name for the data point"
    )
    x: Union[str, int, float] = Field(
        description="X-axis value (label for the data point)"
    )
    y: Union[int, float] = Field(description="Y-axis value (numeric value)")


class ChartSeries(BaseModel):
    """A series of data points for the chart"""

    name: str = Field(description="Name of the series (shown in legend)")
    data: list[ChartDataPoint] = Field(
        description="Array of data points in this series"
    )


class ComponentDataChartBase(ComponentDataBaseWithTitle):
    """Base Component Data for Chart visualization with common properties."""

    data: Optional[list[ChartSeries]] = Field(
        default=None, description="Array of data series for the chart"
    )
    x_axis_label: Optional[str] = Field(
        default=None,
        description="Label for the x-axis (shared by all series). Typically taken from the first field's name.",
    )


class ComponentDataBarChart(ComponentDataChartBase):
    """Component Data for Bar Chart."""

    component: Literal["chart-bar"] = "chart-bar"


class ComponentDataLineChart(ComponentDataChartBase):
    """Component Data for Line Chart."""

    component: Literal["chart-line"] = "chart-line"


class ComponentDataPieChart(ComponentDataChartBase):
    """Component Data for Pie Chart."""

    component: Literal["chart-pie"] = "chart-pie"


class ComponentDataDonutChart(ComponentDataChartBase):
    """Component Data for Donut Chart."""

    component: Literal["chart-donut"] = "chart-donut"


class ComponentDataMirroredBarChart(ComponentDataChartBase):
    """Component Data for Mirrored Bar Chart."""

    component: Literal["chart-mirrored-bar"] = "chart-mirrored-bar"


# Discriminated union of all chart types
ComponentDataChart = Annotated[
    Union[
        ComponentDataBarChart,
        ComponentDataLineChart,
        ComponentDataPieChart,
        ComponentDataDonutChart,
        ComponentDataMirroredBarChart,
    ],
    Discriminator("component"),
]


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
    on_row_click: Optional[str] = Field(
        default=None,
        description="Optional identifier for an onRowClick handler function. The handler should be registered in the frontend component registry. When a row is clicked, the handler will be called with (event, rowData) where rowData contains all column values as key-value pairs.",
    )
    """Optional identifier for an onRowClick handler function"""


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
