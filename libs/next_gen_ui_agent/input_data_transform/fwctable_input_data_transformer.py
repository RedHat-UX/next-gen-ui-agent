import re
from typing import Any, Literal

from next_gen_ui_agent.data_structure_tools import sanitize_field_name, transform_value
from next_gen_ui_agent.types import InputDataTransformerBase

# Regex pattern to find column separators in the header line. Indices are taken from it and used for further lines parsing
COLUMN_SEPARATOR_PATTERN = re.compile(r"\s{2,}")


class FwctableInputDataTransformer(InputDataTransformerBase):
    """Input Data transformer from Fixed Width Column Table format with 2+ whitespace or tab separators on header line."""

    TRANSFORMER_NAME = "fwctable"
    TRANSFORMER_NAME_LITERAL = Literal["fwctable"]

    def __init__(self) -> None:
        """Initialize the FWCTABLE transformer."""

    def transform(self, input_data: str) -> Any:
        """
        Transform the input data into the object tree matching parsed JSON format.

        Column headers are sanitized to be valid JSON field names:
        - Special characters (spaces, @, $, %, etc.) are replaced with underscores
        - Headers starting with numbers or hyphens get "field_" prefix
        - This ensures headers work with jsonpath_ng dot notation

        Args:
            input_data: Input data string to transform (FWCTABLE format with headers).
        Returns:
            Object tree matching parsed JSON format (list of dicts), so `jsonpath_ng` can be used
            to access the data, and Pydantic `model_dump_json()` can be used to convert it to JSON string.
        Raises:
            ValueError: If the input data can't be parsed due to invalid format or if the FWCTABLE is empty.
        """
        try:
            # Split input into lines and filter out empty lines
            lines = [line.rstrip() for line in input_data.splitlines() if line.strip()]

            if not lines:
                return []

            # Parse header row to detect column start positions
            header_line = lines[0]
            column_starts = self._detect_column_boundaries(header_line)

            if not column_starts:
                return []

            # Extract and sanitize header column names
            sanitized_headers = []
            for i, start in enumerate(column_starts):
                # Extract header text from start to next column start or end of line
                if i + 1 < len(column_starts):
                    end = column_starts[i + 1]
                    header_text = header_line[start:end].strip()
                else:
                    header_text = header_line[start:].strip()

                sanitized_header = sanitize_field_name(header_text)
                if sanitized_header:
                    sanitized_headers.append(sanitized_header)
                else:
                    sanitized_headers.append(f"field_{len(sanitized_headers)}")

            # Parse data rows using column start positions
            parsed_data = []
            for line in lines[1:]:
                row_dict = {}
                for i, start in enumerate(column_starts):
                    sanitized_header = sanitized_headers[i]
                    # Extract value from the column start position
                    # For the last column, extend to the end of the line
                    if i == len(column_starts) - 1:
                        value_text = line[start:].strip()
                    else:
                        # For non-last columns, use the next column's start position as end
                        next_start = column_starts[i + 1]
                        value_text = line[start:next_start].strip()

                    row_dict[sanitized_header] = transform_value(value_text)

                parsed_data.append(row_dict)

        except Exception as e:
            raise ValueError(f"Invalid FWCTABLE format of the Input Data: {e}") from e

        return parsed_data

    def _detect_column_boundaries(self, header_line: str) -> list[int]:
        """
        Detect column start positions from the header line by finding patterns matching `COLUMN_SEPARATOR_PATTERN`.

        Args:
            header_line: The header line to analyze

        Returns:
            List of start positions for each column
        """
        column_starts = [0]

        for match in COLUMN_SEPARATOR_PATTERN.finditer(header_line):
            # The start of the next column is where non-whitespace begins after the separator
            next_start = match.end()
            # Skip any leading whitespace to find the actual start of the next column
            while next_start < len(header_line) and header_line[next_start].isspace():
                next_start += 1

            if next_start < len(header_line):
                column_starts.append(next_start)

        return column_starts
