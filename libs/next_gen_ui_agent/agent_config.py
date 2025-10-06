import yaml  # type: ignore[import-untyped]
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


def read_config_yaml_file(file_path: str | list[str]) -> AgentConfig:
    """Read config yaml file or files into one agent config"""
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

    config_yaml = merge_configs(config_yamls)
    return AgentConfig(**config_yaml)
