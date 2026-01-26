from typing import Any, Optional

from next_gen_ui_agent.data_transform.image import ImageDataTransformer
from next_gen_ui_agent.data_transform.one_card import OneCardDataTransformer
from next_gen_ui_agent.data_transform.set_of_cards import SetOfCardsDataTransformer
from next_gen_ui_agent.data_transform.table import TableDataTransformer
from next_gen_ui_agent.data_transform.video import VideoPlayerDataTransformer
from next_gen_ui_agent.types import (
    AgentConfig,
    AgentConfigComponent,
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


components_mapping: dict[str, list[AgentConfigComponent] | UIComponentMetadata] = {}
""" Global variable with components mapping configuration.
Filled from init_pertype_components_mapping function.
For single-component config: stores UIComponentMetadata (backward compatibility)
For multi-component config: stores list[AgentConfigComponent] """


def init_pertype_components_mapping(config: AgentConfig | None) -> None:
    """Initialize per type components mapping from config.

    Validates component configurations and stores them for later use.
    For single-component configs, stores UIComponentMetadata (backward compatibility).
    For multi-component configs, stores list[AgentConfigComponent] for LLM selection.

    Raises:
        ValueError: If configuration is invalid (e.g., HBC with llm_configure,
                    dynamic component with llm_configure=False but no configuration)
    """

    components_mapping.clear()

    if config and config.data_types:
        for data_type, data_type_config in config.data_types.items():
            if data_type_config.components:
                # Validate each component configuration
                for component in data_type_config.components:
                    is_dynamic = component.component in DYNAMIC_COMPONENT_NAMES

                    if is_dynamic:
                        # Validation for dynamic components
                        if (
                            component.llm_configure is False
                            and not component.configuration
                        ):
                            raise ValueError(
                                f"Component '{component.component}' for data type '{data_type}' "
                                f"has llm_configure=False but no configuration provided"
                            )
                    else:
                        # Validation for HBC components
                        if (
                            component.llm_configure is not None
                            and component.llm_configure is not True
                        ):
                            raise ValueError(
                                f"Component '{component.component}' for data type '{data_type}' "
                                f"is a hand-build component and cannot use llm_configure option"
                            )
                        if component.configuration is not None:
                            raise ValueError(
                                f"Component '{component.component}' for data type '{data_type}' "
                                f"is a hand-build component and cannot have configuration"
                            )

                # Validate HBC descriptions for multi-component configurations
                if len(data_type_config.components) > 1:
                    # Count HBCs in the list
                    hbc_components = [
                        comp
                        for comp in data_type_config.components
                        if comp.component not in DYNAMIC_COMPONENT_NAMES
                    ]
                    # If multiple components with HBCs, validate descriptions
                    if hbc_components:
                        for hbc in hbc_components:
                            if not (hbc.prompt and hbc.prompt.description):
                                raise ValueError(
                                    f"HBC '{hbc.component}' for data type '{data_type}' must have "
                                    f"prompt.description defined when multiple components are configured"
                                )

                # Store components based on count
                if len(data_type_config.components) == 1:
                    # Single component: backward compatibility - store as UIComponentMetadata
                    component = data_type_config.components[0]
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
                        components_mapping[data_type] = (
                            UIComponentMetadataHandBuildComponent(
                                title="",
                                fields=[],
                                component="hand-build-component",
                                component_type=component.component,
                                reasonForTheComponentSelection=f"configured for {data_type} in the configuration",
                            )
                        )
                else:
                    # Multiple components: store list for LLM selection
                    components_mapping[data_type] = data_type_config.components


def select_configured_component(
    input_data: InputData, json_data: Any | None = None
) -> Optional[UIComponentMetadata]:
    """Select component based on InputData type and configured mapping.

    Only returns component for single-component configurations.
    Returns None for multi-component configurations (LLM selection needed).
    """
    if components_mapping and input_data.get("type"):
        type = input_data["type"]
        if type and type in components_mapping:
            config_value = components_mapping[type]
            # Only handle single-component case (UIComponentMetadata)
            if isinstance(config_value, UIComponentMetadata):
                # clone configured metadata and set values depending on the InputData to it
                ret = config_value.model_copy()
                ret.id = input_data["id"]
                ret.json_data = json_data
                return ret
            # For list[AgentConfigComponent], return None (needs LLM selection)
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
        `UIComponentMetadata` for the selected component or null if none is selected.
        Returns None for multi-component configurations (LLM selection needed).
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
