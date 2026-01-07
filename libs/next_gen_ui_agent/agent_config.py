import argparse
import logging

import yaml  # type: ignore[import-untyped]
from next_gen_ui_agent.argparse_env_default_action import EnvDefault, EnvDefaultExtend
from next_gen_ui_agent.design_system_handler import get_component_system_names
from next_gen_ui_agent.types import AgentConfig


def merge_configs(config_yamls: list[dict]) -> dict:
    """
    Merges multiple configs into one. Last config has the highest precedense on 1st and 2nd object level.
    e.g. `data_types` child nodes are merged.
    """
    config_yaml = dict()
    data_types = dict()
    for next_cy in config_yamls:
        config_yaml.update(next_cy)
        data_types.update(next_cy.get("data_types", {}))
    config_yaml["data_types"] = data_types

    return config_yaml


def parse_config_yaml_to_dict(stream) -> dict:
    """Parse Config Yaml.
    Any compatible input for yaml.safe_load_all can be passed e.g. file stream or string of 1 or multiple YAMLs
    """
    config_yamls = yaml.safe_load_all(stream)
    config = merge_configs(config_yamls)
    return config


def parse_config_yaml(stream) -> AgentConfig:
    """Parse Config Yaml.
    Any compatible input for yaml.safe_load_all can be passed e.g. file stream or string of 1 or multiple YAMLs
    """
    config_yaml = parse_config_yaml_to_dict(stream)
    return AgentConfig(**config_yaml)


def read_config_yaml_file_dict(file_path: str | list[str]) -> dict:
    """Read config yaml file or files into dictionary. Can be used to construct AgentConfig subclasses from this dictionary.
    If you want to read the config into AgentConfig instance, use read_config_yaml_file() instead.
    """
    config_yamls: list[dict] = []
    if type(file_path) is list:
        for f in file_path:
            if f == "":
                continue
            with open(f, "r") as stream:
                config_yamls.append(parse_config_yaml_to_dict(stream))
    elif type(file_path) is str and file_path != "":
        with open(file_path, "r") as stream:
            config_yamls.append(parse_config_yaml_to_dict(stream))

    return merge_configs(config_yamls)


def read_config_yaml_file(file_path: str | list[str]) -> AgentConfig:
    """Read config yaml file or files into one agent config"""

    config_yaml = read_config_yaml_file_dict(file_path)

    return AgentConfig(**config_yaml)


def add_agent_config_comandline_args(
    parser: argparse.ArgumentParser,
) -> None:
    """
    Add commandline arguments for UI agent configuration reading in read_agent_config_from_arguments().

    Args:
        parser: ArgumentParser instance to add arguments to.
    """

    parser.add_argument(
        "--config-path",
        action=EnvDefaultExtend,
        nargs="+",
        type=str,
        help=(
            "Path to configuration YAML file. "
            "You can specify multiple config files by repeating same parameter "
            "or passing comma separated value. Value `-` means no config file is used, or you can simply omit this argument."
        ),
        envvar="NGUI_CONFIG_PATH",
        required=False,
    )
    parser.add_argument(
        "--component-system",
        choices=get_component_system_names(),
        help="Component system to use for rendering (default: yaml config file > `json`)",
        action=EnvDefault,
        envvar="NGUI_COMPONENT_SYSTEM",
        required=False,
    )


def read_agent_config_dict_from_arguments(
    args: argparse.Namespace, logger: logging.Logger
) -> dict:
    """
    Read agent configuration from commandline arguments defined in add_agent_config_comandline_args().

    Args:
        args: Commandline arguments.
        logger: Logger to use for logging.

    Returns:
        Dictionary with configuration, so you can construct `AgentConfig` class or its subclasses for extended configuration, e.g. `AgentConfig(**config_dict)`.
    """
    config = dict()
    if args.config_path and args.config_path != ["-"]:
        logger.info("Loading Next Gen UI Config from paths %s", args.config_path)
        config = read_config_yaml_file_dict(args.config_path)

    if args.component_system:
        config["component_system"] = args.component_system

    return config
