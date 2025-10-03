from abc import ABC
from typing import Any


class InputDataTransformerBase(ABC):
    """Input Data transformer Base."""

    def transform(self, input_data: str) -> Any:
        """
        Transform the input data into the object tree matching parsed JSON format.
        Args:
            input_data: Input data string to transform.
        Returns:
            Object tree matching parsed JSON using `json.loads()`, so `jsonpath_ng` can be used
            to access the data, and Pydantic `model_dump_json()` can be used to convert it to JSON string.
        Raises:
            ValueError: If the input data can't be parsed due to invalid format.
        """
        raise NotImplementedError("Subclasses must implement this method")
