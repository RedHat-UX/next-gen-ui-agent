from abc import ABC, abstractmethod
from typing import Any, Literal, Optional

from next_gen_ui_agent.model import InferenceBase
from pydantic import BaseModel, Field
from typing_extensions import NotRequired, TypedDict

CONFIG_OPTIONS_DATA_TRANSFORMER = Optional[
    str
    | Literal["json"]
    | Literal["yaml"]
    | Literal["csv-comma"]
    | Literal["csv-semicolon"]
    | Literal["csv-tab"]
]
""" data_transformer config option possibilities used on multiple levels """


class DataField(BaseModel):
    """UI Component Field Metadata."""

    name: str = Field(description="Field name to be shown in the UI")
    """Field name to be shown in the UI."""

    data_path: str = Field(
        description="JSON Path pointing to the input data structure to be used to pickup values to be shown in UI"
    )
    """JSON Path pointing to the input data structure to be used to pickup values to be shown in UI"""


class AgentConfigDynamicComponentConfiguration(BaseModel):
    """Agent Configuration - pre-configuration of the one dynamic component for data type."""

    title: str = Field(
        description="Title of the dynamic component to be shown in the UI"
    )
    """Title of the dynamic component to be shown in the UI."""

    fields: list[DataField] = Field(
        description="Fields of the dynamic component to be shown in the UI",
    )
    """Fields of the dynamic component to be shown in the UI."""


class AgentConfigComponent(BaseModel):
    """Agent Configuration - one component config for data type."""

    component: str = Field(
        description="Component name. Can be name of existing dynamic component supported by the UI Agent, or name for hand-build component."
    )
    """
    Component name. Can be name of existing dynamic component supported by the UI Agent, or name for hand-build component.
    """

    configuration: Optional[AgentConfigDynamicComponentConfiguration] = Field(
        default=None,
        description="Optional pre-configuration of the dynamic component to be used.",
    )
    """Optional pre-configuration of the dynamic component to be used."""


class AgentConfigDataType(BaseModel):
    """Agent Configuration for the Data Type."""

    data_transformer: CONFIG_OPTIONS_DATA_TRANSFORMER = Field(
        default=None,
        description="Transformer to use to transform the input data of this type. Available transformers: `json`, `yaml`, `csv-comma`, `csv-semicolon`, `csv-tab`. Other transformers can be installed, see docs.",
    )
    """
    Data transformer to use to transform the input data of this type.
    """

    components: Optional[list[AgentConfigComponent]] = Field(
        default=None,
        description="List of components to select from for the input data of this type.",
    )
    """
    List of components to select from for the input data of this type.
    """


# Intentionaly TypeDict because of passing ABC class InferenceBase
class AgentConfig(BaseModel):
    """Next Gen UI Agent Configuration."""

    component_system: Optional[str] = Field(
        default=None,
        description="Component system to use to render the UI component. Default is `json`. UI renderers have to be installed to use other systems.",
    )
    """Component system to use to render the UI component."""

    data_transformer: CONFIG_OPTIONS_DATA_TRANSFORMER = Field(
        default="json",
        description="Transformer used to parse the input data (can be overriden on 'data type' level). Default `json`, available transformers: `yaml`, `csv-comma`, `csv-semicolon`, `csv-tab`. Other transformers can be installed, see docs.",
    )
    """
    Data transformer to use to transform the input data of this type.
    """

    unsupported_components: Optional[bool] = Field(
        default=None,
        description="If `False` (default), the agent can generate only fully supported UI components. If `True`, the agent can also generate unsupported UI components.",
    )
    """
    If `False` (default), the agent can generate only fully supported UI components.
    If `True`, the agent can also generate unsupported UI components.
    """

    component_selection_strategy: Optional[
        Literal["one_llm_call", "two_llm_calls"]
    ] = Field(
        default=None,
        description="Strategy for LLM powered component selection and configuration step. Possible values: `one_llm_call` (default) - uses one LLM call, `two_llm_calls` - use two LLM calls - experimental!",
    )
    """
    Component selection strategy to use.
    Possible values:
    - `one_llm_call` (default) - use the one LLM call implementation from component_selection.py
    - `two_llm_calls` - use the two LLM calls implementation from component_selection_twostep.py - experimental!
    """

    data_types: Optional[dict[str, AgentConfigDataType]] = Field(
        default=None,
        description="Mapping from `InputData.type` to UI component - currently only one dynamic component with pre-configuration, or hand-build component (aka HBC) can be defined here. Will be extended in the future.",
    )
    """
    Mapping from `InputData.type` to UI component - currently only one dynamic component with pre-configuration, or hand-build component (aka HBC) can be defined here. Will be extended in the future.
    """

    input_data_json_wrapping: Optional[bool] = Field(
        default=None,
        description="If `True` (default), the agent will wrap the JSON input data into data type field if necessary due to its structure. If `False`, the agent will never wrap the JSON input data into data type field.",
    )
    """
    If `True` (default), the agent will wrap the JSON input data into data type field if necessary due to its structure.
    If `False`, the agent will never wrap the JSON input data into data type field.
    """


class InputData(TypedDict):
    """Agent Input Data."""

    id: str
    """
    ID of the input data so we can reference them during the agent processing.
    Must be unique for each `InputData` in one UI Agent call (in one `AgentInput`).
    """
    data: str
    """JSON data to be processed."""
    type: NotRequired[str | None]
    """
    Optional type identification of the input data. Used for "hand-build component" selection
    based on Agent's configuration. See `AgentConfig.hand_build_components_mapping`.
    """
    hand_build_component_type: NotRequired[str | None]
    """
    Optional `component_type` of the "hand-build component" to be used for UI rendering.
    """


class InputDataInternal(InputData):
    """Input Data used in internal call of component selection. Contain parsed JSON data."""

    json_data: NotRequired[Any | None]


class AgentInput(TypedDict):
    """Agent Input."""

    user_prompt: str
    """User prompt to be processed."""
    input_data: list[InputData]
    """Input data to be processed - one or more can be provided."""


class UIComponentMetadata(BaseModel):
    """UI Component Metadata - output of the component selection and configuration step."""

    id: Optional[str] = None
    """ID of the data this instance is for."""
    title: str
    """Title of the component."""
    reasonForTheComponentSelection: Optional[str] = None
    """Reason for the component selection generated by LLM."""
    confidenceScore: Optional[str] = None
    """Confidence score of the component selection generated by LLM."""
    component: str
    """Component type."""
    fields: list[DataField]
    """Fields of the component."""

    json_data: Optional[Any] = None
    """
    Object structure from the `InputData` that was used to generate the component configuration.
    May be altered against original `InputData` by json wrapping!
    """


class UIComponentMetadataHandBuildComponent(UIComponentMetadata):
    """UI Component Mentadata for hand-build component."""

    component_type: str
    """Type of the hand-build component."""


class Rendition(BaseModel):
    """Rendition of the component - output of the UI rendering step."""

    id: str
    component_system: str
    mime_type: str
    content: str


class ComponentSelectionStrategy(ABC):
    """Abstract base class for LLM-based component selection and configuration strategies."""

    input_data_json_wrapping: bool
    """
    If `True`, the agent will wrap the JSON input data into data type field if necessary due to its structure.
    If `False`, the agent will never wrap the JSON input data into data type field.
    """

    def __init__(self, input_data_json_wrapping: bool):
        self.input_data_json_wrapping = input_data_json_wrapping

    @abstractmethod
    async def select_components(
        self, inference: InferenceBase, input: AgentInput
    ) -> list[UIComponentMetadata]:
        """
        Select UI components based on input data and user prompt.
        Args:
            inference: Inference to use to call LLM by the agent
            input: Agent input
            json_data: optional JSON data parsed into python objects to be processed
        Returns:
            List of `UIComponentMetadata`
        """
        pass

    @abstractmethod
    async def perform_inference(
        self,
        inference: InferenceBase,
        user_prompt: str,
        json_data: Any,
        input_data_id: str,
    ) -> list[str]:
        """
        Perform inference to select UI components and configure them.
        Multiple LLM calls can be performed and inference results can be returned as a list of strings.

        Args:
            inference: Inference to use to call LLM by the agent
            user_prompt: User prompt to be processed
            json_data: JSON data parsed into python objects to be processed
            input_data_id: ID of the input data

        Returns:
            List of strings with LLM inference outputs
        """
        pass

    @abstractmethod
    def parse_infernce_output(
        self, inference_output: list[str], input_data_id: str
    ) -> UIComponentMetadata:
        """
        Parse LLM inference outputs from `perform_inference` and return `UIComponentMetadata`
        or throw exception if it can't be constructed because of invalid LLM outputs.

        Args:
            inference_output: List of strings with LLM inference outputs
            input_data_id: ID of the input data

        Returns:
            `UIComponentMetadata`
        """
        pass


class InputDataTransformerBase(ABC):
    """Base of the Input Data transformer"""

    def transform_input_data(self, input_data: InputData) -> Any:
        """
        Transform the input data into the object tree matching parsed JSON format.

        Default implementation calls #transform(string) method with content.

        Args:
            input_data: InputData to transform
        Returns:
            Object tree matching parsed JSON using `json.loads()`, so `jsonpath_ng` can be used
            to access the data, and Pydantic `model_dump_json()` can be used to convert it to JSON string.
            Root of the structure must be either object (`dict`) or array (`list`).
        Raises:
            ValueError: If the input data can't be parsed due to invalid format.
        """
        return self.transform(input_data["data"])

    def transform(self, input_data: str) -> Any:
        """
        Transform the input data into the object tree matching parsed JSON format.
        Args:
            input_data: Input data string to transform
        Returns:
            Object tree matching parsed JSON using `json.loads()`, so `jsonpath_ng` can be used
            to access the data, and Pydantic `model_dump_json()` can be used to convert it to JSON string.
            Root of the structure must be either object (`dict`) or array (`list`).
        Raises:
            ValueError: If the input data can't be parsed due to invalid format.
        """
        raise NotImplementedError("Subclasses must implement this method")
