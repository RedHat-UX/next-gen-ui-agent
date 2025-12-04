import argparse
import logging
import os
from unittest.mock import patch

import pytest
from next_gen_ui_agent.agent_config import (
    add_agent_config_comandline_args,
    parse_config_yaml,
    read_agent_config_dict_from_arguments,
    read_config_yaml_file,
)
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


class TestAddAgentConfigCommandlineArgs:
    """Tests for add_agent_config_comandline_args function."""

    def test_adds_config_path_argument(self) -> None:
        """Test that --config-path argument is added correctly."""
        parser = argparse.ArgumentParser()
        add_agent_config_comandline_args(parser)

        # Verify the argument exists
        assert "--config-path" in parser.format_help()

    def test_adds_component_system_argument(self) -> None:
        """Test that --component-system argument is added correctly."""
        parser = argparse.ArgumentParser()
        add_agent_config_comandline_args(parser)

        # Verify the argument exists
        assert "--component-system" in parser.format_help()

    def test_config_path_uses_env_var_when_not_provided(self) -> None:
        """Test that NGUI_CONFIG_PATH env var is used when --config-path is not provided."""
        env_value = "/path/to/env/config.yaml"
        with patch.dict(os.environ, {"NGUI_CONFIG_PATH": env_value}):
            parser = argparse.ArgumentParser()
            add_agent_config_comandline_args(parser)
            args = parser.parse_args([])
            assert args.config_path == [env_value]

    def test_config_path_arg_overrides_env_var(self) -> None:
        """Test that --config-path argument takes precedence over NGUI_CONFIG_PATH env var."""
        env_value = "/path/to/env/config.yaml"
        arg_value = "/path/to/arg/config.yaml"
        with patch.dict(os.environ, {"NGUI_CONFIG_PATH": env_value}):
            parser = argparse.ArgumentParser()
            add_agent_config_comandline_args(parser)
            args = parser.parse_args(["--config-path", arg_value])
            assert args.config_path == [arg_value]

    def test_component_system_uses_env_var_when_not_provided(self) -> None:
        """Test that NGUI_COMPONENT_SYSTEM env var is used when --component-system is not provided."""
        env_value = "rhds"
        with patch.dict(os.environ, {"NGUI_COMPONENT_SYSTEM": env_value}):
            parser = argparse.ArgumentParser()
            add_agent_config_comandline_args(parser)
            args = parser.parse_args([])
            assert args.component_system == env_value

    def test_component_system_arg_overrides_env_var(self) -> None:
        """Test that --component-system argument takes precedence over NGUI_COMPONENT_SYSTEM env var."""
        env_value = "rhds"
        arg_value = "json"
        with patch.dict(os.environ, {"NGUI_COMPONENT_SYSTEM": env_value}):
            parser = argparse.ArgumentParser()
            add_agent_config_comandline_args(parser)
            args = parser.parse_args(["--component-system", arg_value])
            assert args.component_system == arg_value

    def test_component_agent_config_default_when_neither_provided(self) -> None:
        """Test that component_system defaults to None when neither arg nor env var is provided, so agent config or default is used."""
        with patch.dict(os.environ, {}, clear=True):
            parser = argparse.ArgumentParser()
            add_agent_config_comandline_args(parser)
            args = parser.parse_args([])
            assert args.component_system is None

    def test_both_args_override_both_env_vars(self) -> None:
        """Test that both arguments take precedence over both environment variables."""
        env_vars = {
            "NGUI_CONFIG_PATH": "/env/config.yaml",
            "NGUI_COMPONENT_SYSTEM": "rhds",
        }
        with patch.dict(os.environ, env_vars):
            parser = argparse.ArgumentParser()
            add_agent_config_comandline_args(parser)
            args = parser.parse_args(
                [
                    "--config-path",
                    "/arg/config.yaml",
                    "--component-system",
                    "json",
                ]
            )
            assert args.config_path == ["/arg/config.yaml"]
            assert args.component_system == "json"

    def test_multiple_config_paths_in_arg(self) -> None:
        """Test that multiple config paths can be provided."""
        parser = argparse.ArgumentParser()
        add_agent_config_comandline_args(parser)
        args = parser.parse_args(
            ["--config-path", "/path1.yaml", "--config-path", "/path2.yaml"]
        )
        assert args.config_path == ["/path1.yaml", "/path2.yaml"]

    def test_multiple_config_paths_in_env_var(self) -> None:
        """Test that multiple config paths can be provided in env var."""
        env_value = " /path1.yaml, /path2.yaml "
        with patch.dict(os.environ, {"NGUI_CONFIG_PATH": env_value}):
            parser = argparse.ArgumentParser()
            add_agent_config_comandline_args(parser)
            args = parser.parse_args([])
            assert args.config_path == ["/path1.yaml", "/path2.yaml"]


class TestReadAgentConfigDictFromArguments:
    """Tests for read_agent_config_dict_from_arguments function."""

    @pytest.fixture()
    def logger(self) -> logging.Logger:
        """Create a logger for testing."""
        return logging.getLogger("test")

    def test_reads_config_from_file(self, test_dir, logger) -> None:
        """Test that config is read from file path."""
        config_path = os.path.join(test_dir, "agent_config_test.yaml")
        args = argparse.Namespace(config_path=[config_path], component_system=None)
        config = read_agent_config_dict_from_arguments(args, logger)
        assert config["component_system"] == "json"
        assert "data_types" in config

    def test_reads_component_system_from_arg(self, logger) -> None:
        """Test that component_system is read from argument."""
        args = argparse.Namespace(config_path=None, component_system="rhds")
        config = read_agent_config_dict_from_arguments(args, logger)
        assert config["component_system"] == "rhds"

    def test_component_system_arg_overrides_config_file(self, test_dir, logger) -> None:
        """Test that component_system argument overrides value from config file."""
        config_path = os.path.join(test_dir, "agent_config_test.yaml")
        args = argparse.Namespace(config_path=[config_path], component_system="rhds")
        config = read_agent_config_dict_from_arguments(args, logger)
        # Config file has "json", but arg should override it
        assert config["component_system"] == "rhds"

    def test_config_path_arg_overrides_env_var(self, test_dir, logger) -> None:
        """Test that config_path argument takes precedence over env var."""
        env_config_path = "/nonexistent/env/config.yaml"
        arg_config_path = os.path.join(test_dir, "agent_config_test.yaml")
        with patch.dict(os.environ, {"NGUI_CONFIG_PATH": env_config_path}):
            parser = argparse.ArgumentParser()
            add_agent_config_comandline_args(parser)
            args = parser.parse_args(["--config-path", arg_config_path])
            config = read_agent_config_dict_from_arguments(args, logger)
            # Should read from arg path, not env path
            assert config["component_system"] == "json"
            assert "data_types" in config

    def test_component_system_arg_overrides_env_var(self, logger) -> None:
        """Test that component_system argument takes precedence over env var."""
        env_value = "rhds"
        arg_value = "json"
        with patch.dict(os.environ, {"NGUI_COMPONENT_SYSTEM": env_value}):
            parser = argparse.ArgumentParser()
            add_agent_config_comandline_args(parser)
            args = parser.parse_args(["--component-system", arg_value])
            config = read_agent_config_dict_from_arguments(args, logger)
            assert config["component_system"] == arg_value

    def test_both_args_override_both_env_vars(self, test_dir, logger) -> None:
        """Test that both arguments take precedence over both environment variables."""
        env_vars = {
            "NGUI_CONFIG_PATH": "/nonexistent/env/config.yaml",
            "NGUI_COMPONENT_SYSTEM": "rhds",
        }
        arg_config_path = os.path.join(test_dir, "agent_config_test.yaml")
        with patch.dict(os.environ, env_vars):
            parser = argparse.ArgumentParser()
            add_agent_config_comandline_args(parser)
            args = parser.parse_args(
                [
                    "--config-path",
                    arg_config_path,
                    "--component-system",
                    "json",
                ]
            )
            config = read_agent_config_dict_from_arguments(args, logger)
            # Should use arg values, not env values
            assert config["component_system"] == "json"
            assert "data_types" in config

    def test_env_vars_used_when_no_args_provided(self, test_dir, logger) -> None:
        """Test that environment variables are used when no arguments are provided."""
        env_config_path = os.path.join(test_dir, "agent_config_test.yaml")
        env_vars = {
            "NGUI_CONFIG_PATH": env_config_path,
            "NGUI_COMPONENT_SYSTEM": "rhds",
        }
        with patch.dict(os.environ, env_vars):
            parser = argparse.ArgumentParser()
            add_agent_config_comandline_args(parser)
            args = parser.parse_args([])
            config = read_agent_config_dict_from_arguments(args, logger)
            # Should use env values
            assert config["component_system"] == "rhds"
            assert "data_types" in config

    def test_empty_config_when_no_config_path(self, logger) -> None:
        """Test that empty config is returned when no config_path is provided."""
        args = argparse.Namespace(config_path=None, component_system=None)
        config = read_agent_config_dict_from_arguments(args, logger)
        assert config == {}

    def test_config_path_dash_ignored(self, logger) -> None:
        """Test that config_path of ['-'] is ignored."""
        args = argparse.Namespace(config_path=["-"], component_system="json")
        config = read_agent_config_dict_from_arguments(args, logger)
        assert config["component_system"] == "json"
        assert "data_types" not in config

    def test_multiple_config_files_merged(self, test_dir, logger) -> None:
        """Test that multiple config files are merged correctly."""
        config_path = os.path.join(test_dir, "agent_config_test.yaml")
        args = argparse.Namespace(
            config_path=[config_path, config_path], component_system=None
        )
        config = read_agent_config_dict_from_arguments(args, logger)
        assert config["component_system"] == "json"
        assert "data_types" in config
