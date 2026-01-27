import csv
from io import StringIO
from typing import Any, Literal

from next_gen_ui_agent.data_structure_tools import sanitize_field_name, transform_value
from next_gen_ui_agent.types import InputData, InputDataTransformerBase


class CsvInputDataTransformer(InputDataTransformerBase):
    """Input Data transformer from CSV format with configurable delimiter."""

    def __init__(self, delimiter: str = ",") -> None:
        """
        Initialize the CSV transformer with a specific delimiter.
        Args:
            delimiter: The delimiter to use for parsing CSV (default: comma).
        """
        self.delimiter = delimiter

    def transform(self, input_data: str) -> Any:
        """
        Transform the input data into the object tree matching parsed JSON format.

        Column headers are sanitized to be valid JSON field names:
        - Special characters (spaces, @, $, %, etc.) are replaced with underscores
        - Headers starting with numbers or hyphens get "field_" prefix
        - This ensures headers work with jsonpath_ng dot notation

        Args:
            input_data: Input data string to transform (CSV format with headers).
        Returns:
            Object tree matching parsed JSON format (list of dicts), so `jsonpath_ng` can be used
            to access the data, and Pydantic `model_dump_json()` can be used to convert it to JSON string.
        Raises:
            ValueError: If the input data can't be parsed due to invalid format or if the CSV is empty.
        """
        try:
            # Parse CSV using DictReader which treats first row as headers
            csv_reader = csv.DictReader(StringIO(input_data), delimiter=self.delimiter)
            parsed_data = []
            for row in csv_reader:
                # Sanitize field names and transform values
                sanitized_row = {}
                for key, value in row.items():
                    sanitized_key = sanitize_field_name(key)
                    if sanitized_key:  # Only include if sanitization didn't return None
                        sanitized_row[sanitized_key] = transform_value(value)
                parsed_data.append(sanitized_row)
        except csv.Error as e:
            raise ValueError(f"Invalid CSV format of the Input Data: {e}") from e

        return parsed_data

    def detect_my_data_structure(self, input_data: InputData) -> bool:
        """
        Detect if input data looks like CSV using heuristics.
        Checks first 1KB for delimiter patterns without parsing.
        """
        data_str = input_data["data"].strip()
        if not data_str:
            return False

        # Should NOT look like JSON or YAML. Just basic checks to avoid false positives.
        first_char = data_str[0]
        if first_char in ("{", "["):  # JSON
            return False
        if data_str.startswith("---"):  # YAML document marker
            return False

        # Get first 1KB to check structure (should cover first few lines)
        sample = data_str[:1024]
        lines = [line for line in sample.splitlines() if line.strip()]

        if len(lines) < 2:
            return False

        # CSV heuristics: check for consistent delimiter usage
        first_line_delimiters = lines[0].count(self.delimiter)
        second_line_delimiters = lines[1].count(self.delimiter)

        # Must have at least one delimiter
        if first_line_delimiters == 0:
            return False

        # Delimiters should be consistent across rows (allow ±1 for optional trailing fields)
        if abs(first_line_delimiters - second_line_delimiters) > 1:
            return False

        return True


class CsvCommaInputDataTransformer(CsvInputDataTransformer):
    """Input Data transformer from CSV format with comma delimiter."""

    TRANSFORMER_NAME = "csv-comma"

    TRANSFORMER_NAME_LITERAL = Literal["csv-comma"]

    def __init__(self) -> None:
        """Initialize the CSV transformer with comma delimiter."""
        super().__init__(delimiter=",")


class CsvSemicolonInputDataTransformer(CsvInputDataTransformer):
    """Input Data transformer from CSV format with semicolon delimiter."""

    TRANSFORMER_NAME = "csv-semicolon"

    TRANSFORMER_NAME_LITERAL = Literal["csv-semicolon"]

    def __init__(self) -> None:
        """Initialize the CSV transformer with semicolon delimiter."""
        super().__init__(delimiter=";")


class CsvTabInputDataTransformer(CsvInputDataTransformer):
    """Input Data transformer from CSV format with tab delimiter."""

    TRANSFORMER_NAME = "csv-tab"

    TRANSFORMER_NAME_LITERAL = Literal["csv-tab"]

    def __init__(self) -> None:
        """Initialize the CSV transformer with tab delimiter."""
        super().__init__(delimiter="\t")
