import os

import pytest
from next_gen_ui_agent.agent_config import parse_config_yaml, read_config_yaml_file


def test_config_yaml_str() -> None:
    config = parse_config_yaml("component_system: json")
    assert config["component_system"] == "json"
    assert config.get("input_data_json_wrapping") is None


@pytest.fixture()
def test_dir(request):
    return os.path.dirname(request.module.__file__)


def test_config_yaml_file(test_dir) -> None:
    config = read_config_yaml_file(os.path.join(test_dir, "agent_config_test.yaml"))
    assert config["component_system"] == "json"
    assert config.get("component_selection_strategy") is None
    assert config.get("input_data_json_wrapping") is False
    assert config["hand_build_components_mapping"] is not None
    assert config["hand_build_components_mapping"]["my.type"] == "one-card-special"

    # assert config["data_types"] is not None
    # dt = config["data_types"]["namespaces_list"]
    # assert dt.title == "Namespaces"
    # assert dt.component == "table"
    # assert dt.fields[0].name == "Name"
    # assert dt.fields[0].data_path == ".*.metadata.name"
