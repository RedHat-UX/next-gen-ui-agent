from typing import Any, Optional

from next_gen_ui_agent.data_transform.image import ImageDataTransformer
from next_gen_ui_agent.data_transform.one_card import OneCardDataTransformer
from next_gen_ui_agent.data_transform.set_of_cards import SetOfCardsDataTransformer
from next_gen_ui_agent.data_transform.table import TableDataTransformer
from next_gen_ui_agent.data_transform.video import VideoPlayerDataTransformer
from next_gen_ui_agent.types import (
    AgentConfig,
    InputData,
    UIComponentMetadata,
    UIComponentMetadataHandBuildComponent,
)

DYNAMIC_COMPONENT_NAMES = [
    OneCardDataTransformer.COMPONENT_NAME,
    ImageDataTransformer.COMPONENT_NAME,
    VideoPlayerDataTransformer.COMPONENT_NAME,
    TableDataTransformer.COMPONENT_NAME,
    SetOfCardsDataTransformer.COMPONENT_NAME,
]
""" List of dynamic component names. """


components_mapping: dict[str, UIComponentMetadata] = {}
""" Global variable with components mapping configuration.
Filled from init_pertype_components_mapping function """


def init_pertype_components_mapping(config: AgentConfig | None) -> None:
    """Initialize per type components mapping from config"""

    components_mapping.clear()

    if config and config.data_types:
        for data_type, data_type_config in config.data_types.items():
            if data_type_config.components:
                if len(data_type_config.components) > 1:
                    raise ValueError(
                        f"Only one component can be configured for data type {data_type}"
                    )
                # keep loop here for later use
                for component in data_type_config.components:
                    if component.component in DYNAMIC_COMPONENT_NAMES:
                        if not component.configuration:
                            raise ValueError(
                                f"Pre-defined configuration is required for dynamic component {component.component} for data type {data_type}"
                            )
                        components_mapping[data_type] = UIComponentMetadata(
                            component=component.component,
                            title=component.configuration.title,
                            fields=component.configuration.fields,
                            reasonForTheComponentSelection=f"configured for {data_type} in the configuration",
                        )
                    else:
                        components_mapping[
                            data_type
                        ] = UIComponentMetadataHandBuildComponent(
                            title="",
                            fields=[],
                            component="hand-build-component",
                            component_type=component.component,
                            reasonForTheComponentSelection=f"configured for {data_type} in the configuration",
                        )


def select_configured_component(
    input_data: InputData, json_data: Any | None = None
) -> Optional[UIComponentMetadata]:
    """Select component based on InputData type and configured mapping."""
    if components_mapping and input_data.get("type"):
        type = input_data["type"]
        if type and type in components_mapping:
            # clone configured metadata and set values epending on the InputData to it
            ret = components_mapping[type].model_copy()
            ret.id = input_data["id"]
            ret.json_data = json_data
            return ret
    return None


def construct_hbc_metadata(
    component_type: str, input_data: InputData, json_data: Any | None = None
) -> Optional[UIComponentMetadataHandBuildComponent]:
    """Construct hand-build component metadata for component_type and input data."""
    return UIComponentMetadataHandBuildComponent.model_validate(
        {
            "id": input_data["id"],
            "title": "",
            "component": "hand-build-component",
            "reasonForTheComponentSelection": "requested in InputData.hand_build_component_type",
            "component_type": component_type,
            "fields": [],
            "json_data": json_data,
        }
    )


def select_component_per_type(
    input_data: InputData, json_data: Any | None = None
) -> Optional[UIComponentMetadata]:
    """Select component per `InputData.type` based on AgentConfiguration parsed by `init_pertype_components_mapping` or `InputData.hand_build_component_type`

    Args:
        input_data: `InputData` to select component for
        json_data: JSON data to be used to construct component metadata

    Returns:
        `UIComponentMetadata` for the selected component or null if none is selected
    """

    component: Optional[UIComponentMetadata] = None

    # Process HBC directly requested in InputData first
    hbc_type = (
        input_data.get("hand_build_component_type")
        if "hand_build_component_type" in input_data
        else None
    )
    if hbc_type:
        component = construct_hbc_metadata(hbc_type, input_data, json_data)
    else:
        # try to find component from configured mapping
        component = select_configured_component(input_data, json_data)

    return component
