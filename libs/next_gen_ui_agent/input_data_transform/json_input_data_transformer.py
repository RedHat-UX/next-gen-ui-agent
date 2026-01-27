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
        has_commas = "," in sample
        # Single-pass check: scan sample once instead of up to 4 times
        has_structural_chars = any(c in "{}[]" for c in sample)
        has_objects_inside = "{" in sample

        # For objects (starts with {), require colons and quotes
        if first_char == "{":
            return has_quotes and has_colons and has_structural_chars
        else:  # first_char == '['
            # Arrays can contain: objects, strings, numbers, booleans, null, nested arrays
            # If array contains objects (has '{'), apply stricter checks
            if has_objects_inside:
                return has_quotes and has_colons and has_structural_chars

            # For arrays without objects (primitives, strings, or nested arrays):
            # - Empty arrays: just []
            # - Single element: might not have commas
            # - Multiple elements: should have commas
            # - Look for JSON keywords (true, false, null) or quotes (strings) or commas
            # - Check for nested brackets (nested arrays like [[1], [2]])
            has_json_keywords = any(
                keyword in sample for keyword in ("true", "false", "null")
            )
            # Count brackets to detect nested arrays - if more than 2 brackets, likely nested
            bracket_count = sample.count("[") + sample.count("]")
            has_nested_arrays = bracket_count > 2

            return has_structural_chars and (
                has_quotes or has_commas or has_json_keywords or has_nested_arrays
            )
