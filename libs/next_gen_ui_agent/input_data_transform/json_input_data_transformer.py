import json
from typing import Any

from next_gen_ui_agent.input_data_transform.types import InputDataTransformerBase


class JsonInputDataTransformer(InputDataTransformerBase):
    """Input Data transformer from JSON format."""

    def transform(self, input_data: str) -> Any:
        """
        Transform the input data into the object tree matching parsed JSON format.
        Args:
            input_data: Input data string to transform.
        Returns:
            Object tree matching parsed JSON format.
        """
        try:
            return json.loads(input_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format of the Input Data: {e}") from e
