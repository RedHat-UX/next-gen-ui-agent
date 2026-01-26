from abc import ABC
from typing import Any, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field
from typing_extensions import NotRequired, TypedDict

CONFIG_OPTIONS_DATA_TRANSFORMER = Optional[
    str
    | Literal["json"]
    | Literal["yaml"]
    | Literal["csv-comma"]
    | Literal["csv-semicolon"]
    | Literal["csv-tab"]
    | Literal["fwctable"]
]
""" data_transformer config option possibilities used on multiple levels """

CONFIG_OPTIONS_ALL_COMPONETS = Optional[
    set[
        Literal["one-card"]
        | Literal["image"]
        | Literal["video-player"]
        | Literal["table"]
        | Literal["set-of-cards"]
        | Literal["chart-bar"]
        | Literal["chart-line"]
        | Literal["chart-pie"]
        | Literal["chart-donut"]
        | Literal["chart-mirrored-bar"]
    ]
]
"""Valid component names that can be selected by the agent's LLM for data visualization."""


class DataField(BaseModel):
    """UI Component Field Metadata."""

    id: str = Field(
        description="Unique field ID. Can be used in CSS selectors to target the field, eg. to set its style, or during live refresh of the shown data from the backend.",
        default_factory=lambda: uuid4().hex,
    )
    """Unique field ID. Can be used for frontend customizations, eg. using it in CSS class names to target the field and set its style. Or as a field id during live refresh of the shown data from the backend."""

    name: str = Field(description="Field name to be shown in the UI")
    """Field name to be shown in the UI."""

    data_path: str = Field(
        description="JSON Path pointing to the input data structure (after input data transformation and JSON wrapping, if applied). It is used to pickup values to be shown in the UI."
    )
    """JSON Path pointing to the input data structure (after input data transformation and JSON wrapping, if applied). It is used to pickup values to be shown in the UI."""


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

    llm_configure: Optional[bool] = Field(
        default=True,
        description="If True, LLM generates configuration. If False, pre-defined configuration must be provided and will be used. Only applicable to dynamic components, not hand-build components.",
    )
    """
    If True, LLM generates configuration (fields). If False, pre-defined configuration from `configuration` field is used.
    Only applicable to dynamic components. Hand-build components must not use this field.
    """

    prompt: Optional["AgentConfigPromptComponent"] = Field(
        default=None,
        description="Optional prompt customization for this component. Overrides global `prompt.components` configuration for this component in this data_type context. Has the same fields as `prompt.components`. For HBCs in multi-component scenarios, at least 'description' field is required.",
    )
    """Optional prompt customization for this component."""


class AgentConfigDataType(BaseModel):
    """Agent Configuration for the Data Type."""

    data_transformer: CONFIG_OPTIONS_DATA_TRANSFORMER = Field(
        default=None,
        description="Transformer to use to transform the input data of this type. Available transformers: `json`, `yaml`, `csv-comma`, `csv-semicolon`, `csv-tab`. Other transformers can be installed, see docs.",
    )
    """
    Data transformer to use to transform the input data of this type.
    """

    generate_all_fields: Optional[bool] = Field(
        default=None,
        description="If `True`, the agent will generate all possible view Fields for the UI component into its output configuration `UIBlockComponentMetadata.fields_all`, if `False` then all fields aren't generated, if `None` then agent's default setting is used. Supported only for `table` and `set-of-cards` components.",
    )
    """
    If `True`, the agent will generate all possible view Fields for the UI component into its output configuration `UIBlockComponentMetadata.fields_all`.
    If `False` then all fields aren't generated, if `None` then agent's default setting is used.
    Supported only for `table` and `set-of-cards` components.
    """

    components: Optional[list[AgentConfigComponent]] = Field(
        default=None,
        description="List of components to select from for the input data of this type.",
    )
    """
    List of components to select from for the input data of this type.
    """


class AgentConfigPromptComponent(BaseModel):
    """Component metadata overrides for LLM prompts.

    Allows overriding any field from COMPONENT_METADATA for a specific component.
    Available fields depend on component type:
    - All components: description, twostep_step2_example, twostep_step2_rules
    - Chart components: chart_description, chart_fields_spec, chart_rules, chart_inline_examples
    """

    description: Optional[str] = Field(
        default=None,
        description="Override component description used in LLM prompts",
    )
    """Override component description used in LLM prompts."""

    twostep_step2_example: Optional[str] = Field(
        default=None,
        description="Override example for two-step strategy field selection",
    )
    """Override example for two-step strategy field selection."""

    twostep_step2_rules: Optional[str] = Field(
        default=None,
        description="Override rules for two-step strategy field selection",
    )
    """Override rules for two-step strategy field selection."""

    chart_description: Optional[str] = Field(
        default=None,
        description="Override chart type description (chart components only)",
    )
    """Override chart type description (chart components only)."""

    chart_fields_spec: Optional[str] = Field(
        default=None,
        description="Override chart fields specification (chart components only)",
    )
    """Override chart fields specification (chart components only)."""

    chart_rules: Optional[str] = Field(
        default=None,
        description="Override chart-specific rules (chart components only)",
    )
    """Override chart-specific rules (chart components only)."""

    chart_inline_examples: Optional[str] = Field(
        default=None,
        description="Override inline chart examples (chart components only)",
    )
    """Override inline chart examples (chart components only)."""


class AgentConfigPrompt(BaseModel):
    """Prompt-related configuration for LLM interactions."""

    components: Optional[dict[str, AgentConfigPromptComponent]] = Field(
        default=None,
        description="Component metadata overrides. Keys are component names (e.g., 'table', 'chart-bar'), values are field overrides. Component names must match those in CONFIG_OPTIONS_ALL_COMPONETS.",
    )
    """Component metadata overrides. Keys are component names, values are field overrides."""


# Intentionaly TypeDict because of passing ABC class InferenceBase
class AgentConfig(BaseModel):
    """Next Gen UI Agent Configuration."""

    component_system: Optional[str] = Field(
        default="json",
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

    selectable_components: CONFIG_OPTIONS_ALL_COMPONETS = Field(
        default=None,
        description="List of components that can be selected by the agent's LLM for data visualization. If not set, all components are selectable.",
    )
    """
    List of components that can be selected by the agent's LLM for data visualization. If not set, all components are selectable.
    """

    component_selection_strategy: Optional[Literal["one_llm_call", "two_llm_calls"]] = (
        Field(
            default="one_llm_call",
            description="Strategy for LLM powered component selection and configuration step. Possible values: `one_llm_call` (default) - uses one LLM call, `two_llm_calls` - use two LLM calls - experimental!",
        )
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
        default=True,
        description="If `True` (default), the agent will wrap the JSON input data into data type field if necessary due to its structure. If `False`, the agent will never wrap the JSON input data into data type field.",
    )
    """
    If `True` (default), the agent will wrap the JSON input data into data type field if necessary due to its structure.
    If `False`, the agent will never wrap the JSON input data into data type field.
    """

    generate_all_fields: bool = Field(
        default=False,
        description="If `True`, the agent will generate all possible view Fields for the UI component into its output configuration `UIBlockComponentMetadata.fields_all`, if `False` then all fields aren't generated. Can be overriden for individual `data_types`. Supported only for `table` and `set-of-cards` components.",
    )
    """
    If `True`, the agent will generate all possible view Fields for the UI component into its output configuration `UIBlockComponentMetadata.fields_all`.
    If `False` then all fields aren't generated. Can be overriden for individual `data_types`.
    Supported only for `table` and `set-of-cards` components.
    """

    prompt: Optional[AgentConfigPrompt] = Field(
        default=None,
        description="Prompt-related configuration for LLM interactions. Allows customizing component descriptions, rules, and examples used in agent prompts.",
    )
    """Prompt-related configuration for LLM interactions. Allows customizing component descriptions, rules, and examples used in agent prompts."""


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
    Optional type identification of the input data. Used for processing (see `AgentConfig.data_types`) and frontend visualization customizations.
    Name of Tool used to load data from backend is typically put into this field.
    """
    hand_build_component_type: NotRequired[str | None]
    """
    Optional `component_type` of the "hand-build component" to be used for UI rendering.
    """


class InputDataInternal(InputData):
    """Input Data used in internal call of component selection. Contain additional fields necessary for internal processing."""

    json_data: NotRequired[Any | None]
    """
    Object structure obtained from the `InputData` by the `input data transformation`.
    """
    input_data_transformer_name: NotRequired[Any | None]
    """
    Name of the input data transformer used to transform the input data string into object structure in the `json_data` field.
    """


class AgentInput(TypedDict):
    """Agent Input."""

    user_prompt: str
    """User prompt to be processed."""
    input_data: list[InputData]
    """Input data to be processed - one or more can be provided."""


class UIComponentMetadataBase(BaseModel):
    """UI Component Metadata - part shared between UIBlockConfiguration and UIComponentMetadata."""

    id: Optional[str] = Field(
        default=None, description="ID of the `InputData` this instance is for."
    )
    """ID of the `InputData` this instance is for."""
    title: str = Field(description="Title of the component.")
    """Title of the component."""
    component: str = Field(description="Component type.")
    """Component type."""
    fields: list[DataField] = Field(
        description="Fields of the component to be shown in the UI.",
    )
    """Fields of the component to be shown in the UI."""


class UIComponentMetadata(UIComponentMetadataBase):
    """UI Component Metadata - output of the component selection and configuration step."""

    reasonForTheComponentSelection: Optional[str] = None
    """Reason for the component selection generated by LLM."""
    confidenceScore: Optional[str] = None
    """Confidence score of the component selection generated by LLM."""

    json_data: Optional[Any] = None
    """
    Object structure from the `InputData` that was used to generate the component configuration.
    May be altered against original `InputData` by `input data transformation` and/or `JSON Wrapping`!
    """
    input_data_transformer_name: Optional[str] = None
    """
    Name of the input data transformer used to transform the input data.
    """
    json_wrapping_field_name: Optional[str] = None
    """
    Name of the field used for `JSON Wrapping` if it was performed, `None` if `JSON Wrapping` was not performed.
    """

    input_data_type: Optional[str] = None
    """
    Optional type of the input data. Can be used for frontend customization of the component for concrete data type, eg. by using it in CSS class names.
    """

    # Debug information for LLM interactions
    llm_interactions: Optional[list[dict[str, Any]]] = None
    """
    List of LLM interactions for debugging. Each interaction contains:
    - step: 'component_selection' or 'field_selection'
    - system_prompt: System message sent to LLM
    - user_prompt: User prompt sent to LLM
    - raw_response: Raw response from LLM before parsing
    """


class UIComponentMetadataHandBuildComponent(UIComponentMetadata):
    """UI Component Mentadata for hand-build component."""

    component_type: str
    """Type of the hand-build component."""


class UIBlockComponentMetadata(UIComponentMetadataBase):
    """UI Component Metadata for UIBlockConfiguration."""

    fields_all: Optional[list[DataField]] = Field(
        default=None,
        description="All fields available for the component - generated only for `table` and `set-of-cards` components if enabled in agent's configuration. Can be used to provide user with the ability to manually select fields to be shown in the UI.",
    )
    """All fields available for the component - generated only for `table` and `set-of-cards` components if enabled in agent's configuration.
       Can be used to provide user with the ability to manually select fields to be shown in the UI."""


class UIBlockRendering(BaseModel):
    """UI Block Rendering - output of the UI rendering step."""

    id: str = Field(description="ID of the `InputData` this instance is for.")
    """ID of the `InputData` this instance is for."""
    component_system: str = Field(
        description="Component system used to render the UI block."
    )
    """Component system used to render the UI block."""
    mime_type: str = Field(description="MIME type of the UI block content.")
    """MIME type of the UI block content."""
    content: str = Field(description="Content of the UI block serialized into string.")
    """Content of the UI block serialized into string."""


class UIBlockConfiguration(BaseModel):
    """UI Block configuration"""

    data_type: Optional[str] = Field(default=None, description="Input data type.")
    "Input data type"
    input_data_transformer_name: Optional[str] = Field(
        default=None,
        description="Name of the input data transformer used to transform the input data.",
    )
    "Name of the input data transformer used to transform the input data."
    json_wrapping_field_name: Optional[str] = Field(
        default=None,
        description="Name of the field used for the input data `JSON Wrapping` if it was performed, `None` if `JSON Wrapping` was not performed.",
    )
    "Name of the field used for the input data `JSON Wrapping` if it was performed, `None` if `JSON Wrapping` was not performed."
    component_metadata: Optional[UIBlockComponentMetadata] = Field(
        default=None, description="Metadata of the generated UI component."
    )
    "Metadata of the generated UI component"


class UIBlock(BaseModel):
    """UI Block model with all details"""

    id: str
    """ID of the `InputData` this instance is for."""
    rendering: Optional[UIBlockRendering] = None
    "Rendering of UI block"
    configuration: Optional[UIBlockConfiguration] = None
    "Configuration of the block"


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
