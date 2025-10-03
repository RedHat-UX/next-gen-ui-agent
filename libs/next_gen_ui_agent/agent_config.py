import yaml  # type: ignore[import-untyped]
from next_gen_ui_agent.types import AgentConfig


def parse_config_yaml(stream) -> AgentConfig:
    """Parse Config Yaml.
    Any compatible input for yaml.safe_load can be passed e.g. file stream or string"""
    config_yaml = yaml.safe_load(stream)

    agent_config = AgentConfig(**config_yaml)

    return agent_config


def read_config_yaml_file(file_path: str) -> AgentConfig:
    with open(file_path, "r") as stream:
        return parse_config_yaml(stream)


if __name__ == "__main__":
    config = read_config_yaml_file("libs/next_gen_ui_agent/agent_config_test.yaml")
    print(config)
