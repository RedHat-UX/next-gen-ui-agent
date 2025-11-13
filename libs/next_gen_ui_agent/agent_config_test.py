import os

import pytest
from next_gen_ui_agent.agent_config import parse_config_yaml, read_config_yaml_file
from pydantic import ValidationError


def test_config_yaml_str() -> None:
    config = parse_config_yaml("component_system: json")
    assert config.component_system == "json"
    assert config.input_data_json_wrapping is None


def test_config_yamls_str() -> None:
    config = parse_config_yaml(
        """
---
component_system: json
---
component_system: json2
"""
    )
    assert config.component_system == "json2"
    assert config.input_data_json_wrapping is None


def test_parse_config_yaml_str_INVALID() -> None:
    with pytest.raises(ValidationError):
        parse_config_yaml("unsupported_components: ooo")


@pytest.fixture()
def test_dir(request):
    return os.path.dirname(request.module.__file__)


def test_config_yaml_file(test_dir) -> None:
    config = read_config_yaml_file(os.path.join(test_dir, "agent_config_test.yaml"))
    assert config.component_system == "json"
    assert config.component_selection_strategy is None
    assert config.input_data_json_wrapping is False

    assert config.data_types is not None
    dt = config.data_types["my:type"]
    assert dt.data_transformer is None
    assert dt.components is not None
    assert dt.components[0].component == "one-card-special"
    dt = config.data_types["other:type"]
    assert dt.data_transformer is None
    assert dt.components is not None
    assert dt.components[0].component == "one-card"
    assert dt.components[0].configuration is not None
    assert dt.components[0].configuration.title == "Other Type Card"
    assert dt.components[0].configuration.fields is not None
    assert len(dt.components[0].configuration.fields) == 2
    assert dt.components[0].configuration.fields[0].name == "name"
    assert dt.components[0].configuration.fields[0].data_path == "$.name"
    assert dt.components[0].configuration.fields[1].name == "age"
    assert dt.components[0].configuration.fields[1].data_path == "$.age"
    dt = config.data_types["my:type2"]
    assert dt.data_transformer is None
    assert dt.components is not None
    assert dt.components[0].component == "one-card-special2"
    dt = config.data_types["other:type2"]
    assert dt.data_transformer is None
    assert dt.components is not None
    assert dt.components[0].component == "table-special2"


def test_config_yaml_file_empty_path() -> None:
    config = read_config_yaml_file("")
    assert config.component_selection_strategy is None
    assert config.component_system == "json"


def test_config_yaml_files(test_dir) -> None:
    file_path = os.path.join(test_dir, "agent_config_test.yaml")
    config = read_config_yaml_file([file_path, file_path])
    assert config.component_system == "json"
    assert config.component_selection_strategy is None
    assert config.input_data_json_wrapping is False

    assert config.data_types is not None
    dt = config.data_types["my:type"]
    assert dt.data_transformer is None
    assert dt.components is not None
    assert dt.components[0].component == "one-card-special"

    dt = config.data_types["other:type"]
    assert dt.data_transformer is None
    assert dt.components is not None
    assert dt.components[0].component == "one-card"

    dt = config.data_types["my:type2"]
    assert dt.data_transformer is None
    assert dt.components is not None
    assert dt.components[0].component == "one-card-special2"
    dt = config.data_types["other:type2"]
    assert dt.data_transformer is None
    assert dt.components is not None
    assert dt.components[0].component == "table-special2"


def test_config_yaml_file_override(test_dir) -> None:
    config = read_config_yaml_file(os.path.join(test_dir, "agent_config_test.yaml"))
    assert config.data_types is not None
    dt = config.data_types["other:type_to_override"]
    assert dt.components is not None
    assert dt.components[0].component == "value2"
