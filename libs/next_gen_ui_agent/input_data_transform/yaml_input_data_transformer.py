from typing import Any, Literal

import yaml  # type: ignore[import-untyped]
from next_gen_ui_agent.types import InputData, InputDataTransformerBase


class YamlInputDataTransformer(InputDataTransformerBase):
    """Input Data transformer from Yaml format."""

    TRANSFORMER_NAME = "yaml"

    TRANSFORMER_NAME_LITERAL = Literal["yaml"]

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
            parsed_data = yaml.safe_load(input_data)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format of the Input Data: {e}") from e

        # Check that the root element is either an object (dict) or array (list)
        if not isinstance(parsed_data, (dict, list)):
            raise ValueError(
                "Invalid YAML format of the Input Data: YAML root must be an object or array"
            )

        return parsed_data

    def detect_my_data_structure(self, input_data: InputData) -> bool:
        """
        Detect if input data looks like YAML using heuristics.
        Checks first 1KB for YAML-like patterns without actual parsing.
        """
        data_str = input_data["data"].strip()
        if not data_str:
            return False

        # Check first 1KB for YAML patterns
        sample = data_str[:1024] if len(data_str) > 1024 else data_str

        # YAML heuristics - check for common YAML patterns:
        # - Starts with document marker (---)
        # - Has key: value patterns (colon followed by space or newline)
        # - Has list markers (- followed by space)
        has_yaml_separator = sample.startswith("---")
        has_key_value = ": " in sample or ":\n" in sample
        has_list_marker = "\n- " in sample or sample.startswith("- ")

        # Should NOT look like JSON (starts with { or [)
        looks_like_json = data_str[0] in ("{", "[")

        return (
            has_yaml_separator or has_key_value or has_list_marker
        ) and not looks_like_json
