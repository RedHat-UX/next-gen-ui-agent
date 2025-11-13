import json
from typing import Any, Literal

from next_gen_ui_agent.types import InputDataTransformerBase


class JsonInputDataTransformer(InputDataTransformerBase):
    """Input Data transformer from JSON format."""

    TRANSFORMER_NAME = "json"

    TRANSFORMER_NAME_LITERAL = Literal["json"]

    def transform(self, input_data: str) -> Any:
        """
        Transform the input data into the object tree matching parsed JSON format.
        Args:
            input_data: Input data string to transform.
        Returns:
            Object tree matching parsed JSON format, so `jsonpath_ng` can be used
            to access the data, and Pydantic `model_dump_json()` can be used to convert it to JSON string.
        Raises:
            ValueError: If the input data can't be parsed due to invalid format or if root is not object or array.
        """
        try:
            parsed_data = json.loads(input_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format of the Input Data: {e}") from e

        # Check that the root element is either an object (dict) or array (list)
        if not isinstance(parsed_data, (dict, list)):
            raise ValueError(
                "Invalid JSON format of the Input Data: JSON root must be an object or array"
            )

        return parsed_data
