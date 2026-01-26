import pytest
from next_gen_ui_agent.component_selection_pertype import (
    components_mapping,
    init_pertype_components_mapping,
    select_component_per_type,
)
from next_gen_ui_agent.types import (
    AgentConfig,
    AgentConfigComponent,
    AgentConfigDataType,
    AgentConfigDynamicComponentConfiguration,
    DataField,
    InputData,
    UIComponentMetadata,
    UIComponentMetadataHandBuildComponent,
)

AGENT_CONFIG = AgentConfig(
    data_types={
        "my.type": AgentConfigDataType(
            components=[AgentConfigComponent(component="one-card-special")]
        ),
        "my.type_dynamic": AgentConfigDataType(
            components=[
                AgentConfigComponent(
                    component="one-card",
                    configuration=AgentConfigDynamicComponentConfiguration(
                        title="One Card Dynamic",
                        fields=[
                            DataField(name="title", data_path="$..title"),
                            DataField(name="description", data_path="$..description"),
                        ],
                    ),
                )
            ]
        ),
    }
)


def test_select_component_per_type_HBC_EXISTING_BY_TYPE() -> None:
    init_pertype_components_mapping(AGENT_CONFIG)
    json_data = {"title": "test"}
    input_data = InputData(id="1", data="{}", type="my.type")
    result = select_component_per_type(input_data, json_data)
    assert isinstance(result, UIComponentMetadataHandBuildComponent)
    assert result is not None
    assert result.component == "hand-build-component"
    assert result.id == "1"
    assert result.title == ""
    assert result.component_type == "one-card-special"
    assert result.json_data == json_data


def test_select_component_per_type_HBC_EXISTING_BY_INPUT_DATA_FIELD() -> None:
    init_pertype_components_mapping(AGENT_CONFIG)
    json_data = {"title": "test"}
    # we put type with existing configuration here to be sure `hand_build_component_type` has precedence over it
    input_data = InputData(
        id="1", data="{}", type="my.type", hand_build_component_type="one-card-special2"
    )
    result = select_component_per_type(input_data, json_data)
    assert isinstance(result, UIComponentMetadataHandBuildComponent)
    assert result.component == "hand-build-component"
    assert result.id == "1"
    assert result.title == ""
    assert result.component_type == "one-card-special2"
    assert (
        result.reasonForTheComponentSelection
        == "requested in InputData.hand_build_component_type"
    )
    assert result.json_data == json_data


def test_select_component_per_type_DYNAMIC_COMPONENT_NAME() -> None:
    init_pertype_components_mapping(AGENT_CONFIG)
    json_data = {"title": "test", "description": "test"}
    input_data = InputData(id="10", data="{}", type="my.type_dynamic")
    result = select_component_per_type(input_data, json_data)
    assert isinstance(result, UIComponentMetadata)
    assert result.component == "one-card"
    assert result.id == "10"
    assert result.title == "One Card Dynamic"
    assert result.fields[0].name == "title"
    assert result.fields[0].data_path == "$..title"
    assert result.fields[1].name == "description"
    assert result.fields[1].data_path == "$..description"
    assert result.json_data == json_data


def test_select_component_per_type_TYPE_NON_IN_CONFIG() -> None:
    init_pertype_components_mapping(AGENT_CONFIG)
    input_data = InputData(id="1", data="{}", type="my.type2")
    result = select_component_per_type(input_data)
    assert result is None


def test_select_component_per_type_NO_TYPE_IN_INPUT_DATA() -> None:
    init_pertype_components_mapping(AGENT_CONFIG)
    input_data = InputData(id="1", data="{}")
    result = select_component_per_type(input_data)
    assert result is None


def test_select_component_per_type_MAPPING_NOT_CONFIGURED() -> None:
    init_pertype_components_mapping(AgentConfig())
    input_data = InputData(id="1", data="{}", type="my.type2")
    result = select_component_per_type(input_data)
    assert result is None


# TODO test init_pertype_components_mapping method with all possible variants


def test_init_pertype_components_mapping_NONE() -> None:
    init_pertype_components_mapping(None)
    assert len(components_mapping.keys()) == 0


def test_init_pertype_components_mapping_EMPTY() -> None:
    init_pertype_components_mapping(AgentConfig())
    assert len(components_mapping.keys()) == 0


def test_init_pertype_components_mapping_DATA_TYPES_NONE() -> None:
    init_pertype_components_mapping(AgentConfig(data_types=None))
    assert len(components_mapping.keys()) == 0


def test_init_pertype_components_mapping_DATA_TYPES_EMPTY() -> None:
    init_pertype_components_mapping(AgentConfig(data_types={}))
    assert len(components_mapping.keys()) == 0


def test_init_pertype_components_mapping_DATA_TYPES_NON_EMPTY_BUT_NO_COMPONENTS() -> (
    None
):
    init_pertype_components_mapping(
        AgentConfig(data_types={"my.type": AgentConfigDataType(components=[])})
    )
    assert len(components_mapping.keys()) == 0


def test_init_pertype_components_mapping_HBC() -> None:
    init_pertype_components_mapping(
        AgentConfig(
            data_types={
                "my.type": AgentConfigDataType(
                    components=[AgentConfigComponent(component="one-card-special")]
                ),
                "my.type2": AgentConfigDataType(
                    components=[AgentConfigComponent(component="one-card-special2")]
                ),
            }
        )
    )
    assert len(components_mapping.keys()) == 2
    assert isinstance(
        components_mapping["my.type"], UIComponentMetadataHandBuildComponent
    )
    assert components_mapping["my.type"].component == "hand-build-component"
    assert components_mapping["my.type"].component_type == "one-card-special"
    assert (
        components_mapping["my.type"].reasonForTheComponentSelection
        == "configured for my.type in the configuration"
    )
    assert components_mapping["my.type"].json_data is None
    assert components_mapping["my.type"].id is None
    assert components_mapping["my.type"].title == ""
    assert components_mapping["my.type"].fields == []


def test_init_pertype_components_mapping_DYNAMIC_COMPONENT() -> None:
    init_pertype_components_mapping(
        AgentConfig(
            data_types={
                "my.type": AgentConfigDataType(
                    components=[
                        AgentConfigComponent(
                            component="one-card",
                            configuration=AgentConfigDynamicComponentConfiguration(
                                title="One Card Dynamic",
                                fields=[
                                    DataField(name="title", data_path="$..title"),
                                    DataField(
                                        name="description", data_path="$..description"
                                    ),
                                ],
                            ),
                        )
                    ]
                )
            }
        )
    )
    assert len(components_mapping.keys()) == 1
    assert isinstance(components_mapping["my.type"], UIComponentMetadata)
    assert components_mapping["my.type"].component == "one-card"
    assert components_mapping["my.type"].title == "One Card Dynamic"
    assert components_mapping["my.type"].fields[0].name == "title"
    assert components_mapping["my.type"].fields[0].data_path == "$..title"
    assert components_mapping["my.type"].fields[1].name == "description"
    assert components_mapping["my.type"].fields[1].data_path == "$..description"

    assert (
        components_mapping["my.type"].reasonForTheComponentSelection
        == "configured for my.type in the configuration"
    )
    assert components_mapping["my.type"].json_data is None
    assert components_mapping["my.type"].id is None


def test_init_pertype_components_mapping_DYNAMIC_COMPONENT_WITHOUT_CONFIGURATION_ERROR() -> (
    None
):
    with pytest.raises(ValueError):
        init_pertype_components_mapping(
            AgentConfig(
                data_types={
                    "my.type": AgentConfigDataType(
                        components=[AgentConfigComponent(component="one-card")]
                    )
                }
            )
        )


def test_init_pertype_components_mapping_MULTIPLE_COMPONENTS_PER_TYPE() -> None:
    """Test that multiple components per type are now allowed and stored correctly."""
    init_pertype_components_mapping(
        AgentConfig(
            data_types={
                "my.type": AgentConfigDataType(
                    components=[
                        AgentConfigComponent(
                            component="table",
                            configuration=AgentConfigDynamicComponentConfiguration(
                                title="Table View",
                                fields=[DataField(name="Name", data_path="$..name")],
                            ),
                        ),
                        AgentConfigComponent(
                            component="set-of-cards",
                            configuration=AgentConfigDynamicComponentConfiguration(
                                title="Cards View",
                                fields=[DataField(name="Name", data_path="$..name")],
                            ),
                        ),
                    ]
                )
            }
        )
    )
    # Should store list of components
    assert "my.type" in components_mapping
    assert isinstance(components_mapping["my.type"], list)
    assert len(components_mapping["my.type"]) == 2


def test_llm_configure_false_without_config_error() -> None:
    """Test that llm_configure=False without configuration raises ValueError."""
    with pytest.raises(
        ValueError, match="has llm_configure=False but no configuration provided"
    ):
        init_pertype_components_mapping(
            AgentConfig(
                data_types={
                    "my.type": AgentConfigDataType(
                        components=[
                            AgentConfigComponent(
                                component="table",
                                llm_configure=False,
                                # Missing configuration!
                            )
                        ]
                    )
                }
            )
        )


def test_llm_configure_true_without_config_ok() -> None:
    """Test that llm_configure=True (default) without configuration is OK for multi-component."""
    # This should not raise error for multi-component config
    init_pertype_components_mapping(
        AgentConfig(
            data_types={
                "my.type": AgentConfigDataType(
                    components=[
                        AgentConfigComponent(
                            component="table",
                            llm_configure=True,
                            # No configuration - LLM will generate
                        ),
                        AgentConfigComponent(
                            component="set-of-cards",
                            llm_configure=True,
                            # No configuration - LLM will generate
                        ),
                    ]
                )
            }
        )
    )
    assert "my.type" in components_mapping
    assert isinstance(components_mapping["my.type"], list)


def test_hbc_with_llm_configure_error() -> None:
    """Test that HBC with llm_configure flag raises ValueError."""
    with pytest.raises(
        ValueError,
        match="is a hand-build component and cannot use llm_configure option",
    ):
        init_pertype_components_mapping(
            AgentConfig(
                data_types={
                    "my.type": AgentConfigDataType(
                        components=[
                            AgentConfigComponent(
                                component="my-custom-hbc",
                                llm_configure=False,  # ERROR: HBC can't use this
                            )
                        ]
                    )
                }
            )
        )


def test_hbc_with_configuration_error() -> None:
    """Test that HBC with configuration raises ValueError."""
    with pytest.raises(
        ValueError, match="is a hand-build component and cannot have configuration"
    ):
        init_pertype_components_mapping(
            AgentConfig(
                data_types={
                    "my.type": AgentConfigDataType(
                        components=[
                            AgentConfigComponent(
                                component="my-custom-hbc",
                                configuration=AgentConfigDynamicComponentConfiguration(
                                    title="Test",
                                    fields=[
                                        DataField(name="Name", data_path="$..name")
                                    ],
                                ),  # ERROR: HBC can't have configuration
                            )
                        ]
                    )
                }
            )
        )


def test_hbc_without_llm_configure_ok() -> None:
    """Test that HBC works correctly without llm_configure or configuration."""
    init_pertype_components_mapping(
        AgentConfig(
            data_types={
                "my.type": AgentConfigDataType(
                    components=[
                        AgentConfigComponent(
                            component="my-custom-hbc",
                            # No llm_configure, no configuration - correct for HBC
                        )
                    ]
                )
            }
        )
    )
    assert "my.type" in components_mapping
    assert isinstance(
        components_mapping["my.type"], UIComponentMetadataHandBuildComponent
    )


def test_hbc_must_be_only_component() -> None:
    """Test that HBC cannot be mixed with other components (temporary restriction)."""
    with pytest.raises(
        ValueError,
        match="Hand-build components must be the only component configured for a data type",
    ):
        init_pertype_components_mapping(
            AgentConfig(
                data_types={
                    "my.type": AgentConfigDataType(
                        components=[
                            AgentConfigComponent(
                                component="my-custom-hbc",
                            ),
                            AgentConfigComponent(
                                component="table",
                                configuration=AgentConfigDynamicComponentConfiguration(
                                    title="Table View",
                                    fields=[
                                        DataField(name="Name", data_path="$..name")
                                    ],
                                ),
                            ),
                        ]
                    )
                }
            )
        )
