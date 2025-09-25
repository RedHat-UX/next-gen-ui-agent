from typing import Optional

import yaml  # type: ignore[import-untyped]
from next_gen_ui_agent.types import AgentConfig
from pydantic import BaseModel


class AgentConfigFile(BaseModel):
    """Agent configuration from the file.
    Pydantic class to get validation feature fields has to be same as AgentConfig TypedDict
    """

    component_system: Optional[str] = None
    """Component system to use to render the component."""

    unsupported_components: Optional[bool] = None
    """
    If `False` (default), the agent can generate only fully supported UI components.
    If `True`, the agent can also generate unsupported UI components.
    """

    component_selection_strategy: Optional[str] = "default"
    """
    Component selection strategy to use.
    Possible values:
    - default - use the default implementation
    - one_llm_call - use the one LLM call implementation from component_selection.py
    - two_llm_calls - use the two LLM calls implementation from component_selection_twostep.py
    """

    hand_build_components_mapping: Optional[dict[str, str]] = None
    """
    Mapping from `InputData.type` to hand-build `component_type` (aka HBC).
    LLM powered component selection and configuration is skipped for HBC, data are propagated "as is", and only
    rendering is performed by hand-build code registered in the renderer for given `component_type`.
    """

    # data_types: Optional[dict[str, UIComponentMetadata]] = None
    # """Data type configuration"""


def parse_config_yaml(stream) -> AgentConfig:
    """Parse Config Yaml.
    Any compatible input for yaml.safe_load can be passed e.g. file stream or string"""
    config_yaml = yaml.safe_load(stream)

    agent_config = AgentConfigFile(**config_yaml)

    ac: AgentConfig = {
        "component_system": agent_config.component_system,
        "hand_build_components_mapping": agent_config.hand_build_components_mapping,
        # "data_types": agent_config.data_types,  # contains pydantic objects!
    }
    return ac


def read_config_yaml_file(file_path: str) -> AgentConfig:
    with open(file_path, "r") as stream:
        return parse_config_yaml(stream)


if __name__ == "__main__":
    config = read_config_yaml_file("libs/next_gen_ui_agent/agent_config_test.yaml")
    print(config)
