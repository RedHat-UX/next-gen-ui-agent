import json
from typing import Any, Literal

from next_gen_ui_agent.types import InputData, InputDataTransformerBase


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

    def detect_my_data_structure(self, input_data: InputData) -> bool:
        """
        Detect if input data looks like JSON using heuristics.
        Checks first 1KB for JSON-like patterns without actual parsing.
        """
        data_str = input_data["data"].strip()
        if not data_str:
            return False

        # Check first and last characters for JSON structure
        first_char = data_str[0]
        # For large data, check a reasonable sample for closing character
        sample = data_str[:1024] if len(data_str) > 1024 else data_str

        # JSON must start with { or [
        if first_char not in ("{", "["):
            return False

        # Basic heuristics: look for JSON-like patterns
        # Check for common JSON patterns: quotes, colons (for objects), commas, braces/brackets
        has_quotes = '"' in sample
        has_colons = ":" in sample
        # Single-pass check: scan sample once instead of up to 4 times
        has_structural_chars = any(c in "{}[]" for c in sample)

        # For objects (starts with {), require colons
        # For arrays (starts with [), just require quotes and structural chars
        if first_char == "{":
            return has_quotes and has_colons and has_structural_chars
        else:  # first_char == '['
            return has_structural_chars and (has_quotes or has_colons)
