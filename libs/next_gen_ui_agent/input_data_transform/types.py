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
            Object tree matching parsed JSON format.
        """
        raise NotImplementedError("Subclasses must implement this method")
