from typing import Any

import yaml  # type: ignore[import-untyped]
from next_gen_ui_agent.input_data_transform.types import InputDataTransformerBase


class YamlInputDataTransformer(InputDataTransformerBase):
    """Input Data transformer from Yaml format."""

    def transform(self, input_data: str) -> Any:
        """
        Transform the input data into the object tree matching parsed JSON format.
        Args:
            input_data: Input data string to transform.
        Returns:
            Object tree matching parsed JSON format.
        """
        try:
            return yaml.safe_load(input_data)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format of the Input Data: {e}") from e
