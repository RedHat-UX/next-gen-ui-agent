import json
import time
from typing import cast

from jsonpath_ng import parse  # type: ignore
from next_gen_ui_agent.input_data_transform.fwctable_input_data_transformer import (
    FwctableInputDataTransformer,
)
from next_gen_ui_agent.types import InputData
from pydantic import BaseModel


class TestFwctableInputDataTransformer:
    """Test cases for FWCTABLE input data transformer."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.transformer = FwctableInputDataTransformer()

    def test_transformer_name(self) -> None:
        """Test that transformer has correct name."""
        assert self.transformer.TRANSFORMER_NAME == "fwctable"

    def test_transform_basic_fwctable(self) -> None:
        """Test transforming basic FWCTABLE data with type conversion."""
        input_data = """name    age  city
John012 30   New York
Jane    25   Boston"""

        result = self.transformer.transform(input_data)

        expected = [
            {"name": "John012", "age": 30, "city": "New York"},  # age is int
            {"name": "Jane", "age": 25, "city": "Boston"},
        ]

        assert isinstance(result, list)
        assert len(result) == 2
        assert result == expected
        # Verify type conversion
        assert isinstance(result[0]["age"], int)
        assert isinstance(result[1]["age"], int)

    def test_transform_spaces_in_header(self) -> None:
        """Test transforming basic FWCTABLE data with type conversion."""
        input_data = """n me    a e  ci y
John012 30   New York
Jane    25   Boston"""

        result = self.transformer.transform(input_data)

        expected = [
            {"n_me": "John012", "a_e": 30, "ci_y": "New York"},  # age is int
            {"n_me": "Jane", "a_e": 25, "ci_y": "Boston"},
        ]
        assert result == expected

    def test_transform_single_row(self) -> None:
        """Test transforming FWCTABLE with single data row."""
        input_data = """name    age  city
John    30   New York"""

        result = self.transformer.transform(input_data)

        expected = [{"name": "John", "age": 30, "city": "New York"}]  # age is int
        assert result == expected

    def test_transform_with_various_whitespace(self) -> None:
        """Test transforming FWCTABLE with various amounts of whitespace separators."""
        input_data = """name  age    city
John  30     New York
Jane  25     Boston"""

        result = self.transformer.transform(input_data)

        expected = [
            {"name": "John", "age": 30, "city": "New York"},  # age is int
            {"name": "Jane", "age": 25, "city": "Boston"},
        ]
        assert result == expected

    def test_transform_with_tabs_and_spaces(self) -> None:
        """Test transforming FWCTABLE with mixed tabs and spaces as separators."""
        input_data = """name\t\tage    city
John\t\t30     New York
Jane\t\t25     Boston"""

        result = self.transformer.transform(input_data)

        expected = [
            {"name": "John", "age": 30, "city": "New York"},  # age is int
            {"name": "Jane", "age": 25, "city": "Boston"},
        ]
        assert result == expected

    def test_transform_with_empty_fields(self) -> None:
        """Test transforming FWCTABLE with empty fields."""
        input_data = """name    age  city
John          New York
        25    Boston"""

        result = self.transformer.transform(input_data)

        expected = [
            {"name": "John", "age": None, "city": "New York"},
            {"name": None, "age": 25, "city": "Boston"},  # age is int
        ]
        assert result == expected

    def test_transform_with_special_characters(self) -> None:
        """Test transforming FWCTABLE with special characters in values."""
        input_data = """name        email              note
John Doe    john@example.com   Hello, world!
Jane Smith  jane@test.org      Test & verify"""

        result = self.transformer.transform(input_data)

        assert result[0]["name"] == "John Doe"
        assert result[0]["email"] == "john@example.com"
        assert result[0]["note"] == "Hello, world!"
        assert result[1]["note"] == "Test & verify"
        # Verify strings are preserved (no conversion)
        assert isinstance(result[0]["name"], str)
        assert isinstance(result[0]["email"], str)

    def test_transform_empty_fwctable_returns_empty_list(self) -> None:
        """Test that empty FWCTABLE returns empty list."""
        input_data = ""

        assert self.transformer.transform(input_data) == []

    def test_transform_only_headers_returns_empty_list(self) -> None:
        """Test that FWCTABLE with only headers returns empty list."""
        input_data = "name    age  city"

        assert self.transformer.transform(input_data) == []

    def test_transform_only_headers_with_newline_returns_empty_list(self) -> None:
        """Test that FWCTABLE with only headers and newline returns empty list."""
        input_data = "name    age  city\n"

        assert self.transformer.transform(input_data) == []

    def test_transform_with_trailing_newlines(self) -> None:
        """Test transforming FWCTABLE with trailing newlines."""
        input_data = """name    age  city
John    30   New York
Jane    25   Boston

"""

        result = self.transformer.transform(input_data)

        expected = [
            {"name": "John", "age": 30, "city": "New York"},  # age is int
            {"name": "Jane", "age": 25, "city": "Boston"},
        ]
        assert result == expected
        assert len(result) == 2

    def test_transform_preserves_whitespace_in_values(self) -> None:
        """Test that whitespace within values is preserved but trimmed from edges."""
        input_data = """name    age  city
John    30   New York
Jane    25   Boston   """

        result = self.transformer.transform(input_data)

        # Whitespace is trimmed as part of value transformation
        assert result[0]["name"] == "John"  # Trimmed
        assert result[0]["age"] == 30  # Converted to int and trimmed
        assert result[0]["city"] == "New York"  # Trimmed
        assert result[1]["city"] == "Boston"  # Trimmed

    def test_transform_with_different_field_counts_uses_fieldnames(self) -> None:
        """Test FWCTABLE where rows have different number of fields."""
        # If a row has fewer fields, missing ones get None
        input_data = """name    age  city
John    30
Jane    25   Boston"""

        result = self.transformer.transform(input_data)

        assert result[0]["name"] == "John"
        assert result[0]["age"] == 30  # Now int
        assert result[0]["city"] is None
        assert result[1]["city"] == "Boston"

    def test_transform_with_type_conversions(self) -> None:
        """Test FWCTABLE data with various types that should be converted."""
        input_data = """name    age  price   active  rating  description
Alice   25   99.99   true    4.5     Great product
Bob     30   149.50  false   3.8     Good item
Charlie 35   0.99    True    5.0     Excellent"""

        result = self.transformer.transform(input_data)

        # Verify first row types
        assert result[0]["name"] == "Alice"
        assert result[0]["age"] == 25
        assert isinstance(result[0]["age"], int)

        assert result[0]["price"] == 99.99
        assert isinstance(result[0]["price"], float)

        assert result[0]["active"] is True
        assert isinstance(result[0]["active"], bool)

        assert result[0]["rating"] == 4.5
        assert isinstance(result[0]["rating"], float)

        assert result[0]["description"] == "Great product"
        assert isinstance(result[0]["description"], str)

        # Verify second row
        assert result[1]["age"] == 30
        assert result[1]["price"] == 149.50
        assert result[1]["active"] is False

        # Verify third row with different boolean case
        assert result[2]["active"] is True

    def test_transform_with_whitespace_trimming(self) -> None:
        """Test that values with whitespace are trimmed."""
        input_data = """name    age  city
  John    30   New York
Jane     25   Boston  """

        result = self.transformer.transform(input_data)

        # All values should be trimmed
        assert result[0]["name"] == "John"
        assert result[0]["age"] == 30  # Also converted to int
        assert result[0]["city"] == "New York"
        assert result[1]["name"] == "Jane"
        assert result[1]["age"] == 25
        assert result[1]["city"] == "Boston"

    def test_field_name_sanitization(self) -> None:
        """Test that FWCTABLE headers are sanitized to valid field names."""
        input_data = """First Name  user@email      Price ($)  Rating %  user.id   1st Place   2nd_Place  -start
Alice       alice@test.com  99.99      4.5       123       Gold        Silver     Negative
Bob         bob@test.com    149.99     5.0       456       Silver      Bronze     Positive"""

        result = self.transformer.transform(input_data)

        # Verify sanitized field names
        assert len(result) == 2

        # Spaces replaced with underscores
        assert "First_Name" in result[0]
        assert result[0]["First_Name"] == "Alice"

        # Special characters replaced with underscores
        assert "user_email" in result[0]
        assert "Price____" in result[0]
        assert "Rating__" in result[0]
        assert "user_id" in result[0]

        # Fields starting with numbers get "field_" prefix
        assert "field_1st_Place" in result[0]
        assert result[0]["field_1st_Place"] == "Gold"

        # Underscores are preserved
        assert "field_2nd_Place" in result[0]  # Still gets prefix due to number
        assert result[0]["field_2nd_Place"] == "Silver"

        # Fields starting with hyphen get "field_" prefix
        assert "field_-start" in result[0]
        assert result[0]["field_-start"] == "Negative"

        # Verify values are preserved correctly (with type conversion)
        assert result[1]["First_Name"] == "Bob"
        assert result[1]["user_email"] == "bob@test.com"
        assert result[1]["Price____"] == 149.99  # Converted to float
        assert result[1]["Rating__"] == 5.0  # Converted to float
        assert result[1]["user_id"] == 456  # Converted to int

    def test_transform_output_serializable_with_pydantic(self) -> None:
        """Test that transformer output can be serialized using Pydantic model_dump_json()."""

        # Create a simple Pydantic model for testing arrays
        class TestArrayModel(BaseModel):
            items: list

        # Test with FWCTABLE data (which is always array-like)
        input_data = """id  name   age
1   Alice  25
2   Bob    30"""
        result = self.transformer.transform(input_data)

        # Create a Pydantic model instance with the transformed data
        model = TestArrayModel(items=result)

        # Verify that model_dump_json() works without errors
        json_output = model.model_dump_json()
        assert isinstance(json_output, str)

        # Verify the JSON can be parsed back
        parsed_back = json.loads(json_output)
        assert "items" in parsed_back
        assert parsed_back["items"] == result

    def test_transform_output_accessible_with_jsonpath_ng_array(self) -> None:
        """Test that transformer output can be accessed using jsonpath_ng with dot notation."""
        # Test with FWCTABLE array of objects (using simple field names for dot notation)
        input_data = """id  name     city      age
1   Alice    New York  25
2   Bob      Boston    30
3   Charlie  Chicago   35"""

        result = self.transformer.transform(input_data)

        # Test various jsonpath expressions for array data using dot notation
        # Access root array
        root_path = parse("$")
        root_matches = [match.value for match in root_path.find(result)]
        assert len(root_matches) == 1
        assert root_matches[0] == result

        # Access all items in array
        all_items_path = parse("$[*]")
        all_items_matches = [match.value for match in all_items_path.find(result)]
        assert len(all_items_matches) == 3

        # Access specific item by index
        first_item_path = parse("$[0]")
        first_item_matches = [match.value for match in first_item_path.find(result)]
        assert len(first_item_matches) == 1
        assert first_item_matches[0]["name"] == "Alice"
        assert first_item_matches[0]["id"] == 1  # Now int, not string

        # Access all names using dot notation
        all_names_path = parse("$[*].name")
        all_names_matches = [match.value for match in all_names_path.find(result)]
        assert len(all_names_matches) == 3
        assert "Alice" in all_names_matches
        assert "Bob" in all_names_matches
        assert "Charlie" in all_names_matches

        # Access all cities using dot notation
        all_cities_path = parse("$[*].city")
        all_cities_matches = [match.value for match in all_cities_path.find(result)]
        assert len(all_cities_matches) == 3
        assert "New York" in all_cities_matches
        assert "Boston" in all_cities_matches
        assert "Chicago" in all_cities_matches

        # Access specific field by nested index using dot notation
        alice_age_path = parse("$[0].age")
        alice_age_matches = [match.value for match in alice_age_path.find(result)]
        assert len(alice_age_matches) == 1
        assert alice_age_matches[0] == 25  # Now int, not string

        # Access second person's name using dot notation
        bob_name_path = parse("$[1].name")
        bob_name_matches = [match.value for match in bob_name_path.find(result)]
        assert len(bob_name_matches) == 1
        assert bob_name_matches[0] == "Bob"

        # Access all IDs using dot notation
        all_ids_path = parse("$[*].id")
        all_ids = [match.value for match in all_ids_path.find(result)]
        assert len(all_ids) == 3
        assert 1 in all_ids  # Now int
        assert 2 in all_ids
        assert 3 in all_ids

    def test_transform_with_empty_lines_between_data(self) -> None:
        """Test FWCTABLE with empty lines between data rows."""
        input_data = """name    age  city
John    30   New York

Jane    25   Boston

"""

        result = self.transformer.transform(input_data)

        expected = [
            {"name": "John", "age": 30, "city": "New York"},
            {"name": "Jane", "age": 25, "city": "Boston"},
        ]
        assert result == expected
        assert len(result) == 2  # Empty lines should be filtered out


class TestFwctableInputDataTransformerDetectMyDataStructure:
    """Test cases for FwctableInputDataTransformer.detect_my_data_structure()."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.transformer = FwctableInputDataTransformer()

    def test_detect_valid_fwctable_with_multiple_spaces(self) -> None:
        """Test detection returns True for valid FWCTABLE with 2+ spaces (covers: pattern match)."""
        input_data = cast(
            InputData,
            {
                "id": "test1",
                "data": "name    age  city\nJohn    30   New York\nJane    25   Boston",
            },
        )
        assert self.transformer.detect_my_data_structure(input_data) is True

    def test_detect_valid_fwctable_with_tabs(self) -> None:
        """Test detection returns True for FWCTABLE with tabs (covers: tabs = 2+ whitespace)."""
        input_data = cast(
            InputData,
            {
                "id": "test2",
                "data": "name\t\tage\t\tcity\nJohn\t\t30\t\tNew York",
            },
        )
        assert self.transformer.detect_my_data_structure(input_data) is True

    def test_detect_invalid_single_space(self) -> None:
        """Test detection returns False for data with only single spaces (covers: pattern non-match)."""
        input_data = cast(
            InputData, {"id": "test3", "data": "name age city\nJohn 30 New York"}
        )
        assert self.transformer.detect_my_data_structure(input_data) is False

    def test_detect_invalid_single_line(self) -> None:
        """Test detection returns False for single line (covers: len(lines) < 2)."""
        input_data = cast(InputData, {"id": "test4", "data": "name    age  city"})
        assert self.transformer.detect_my_data_structure(input_data) is False

    def test_detect_empty_or_whitespace(self) -> None:
        """Test detection returns False for empty data (covers: no data)."""
        assert (
            self.transformer.detect_my_data_structure(
                cast(InputData, {"id": "test5", "data": ""})
            )
            is False
        )

    def test_detect_large_fwctable_samples_first_1kb(self) -> None:
        """Test detection with large FWCTABLE (>1KB) uses sampling (covers: 1KB sampling)."""
        header = "col1    col2    col3    col4\n"
        rows = "\n".join([f"val{i}    val{i}    val{i}    val{i}" for i in range(100)])
        input_data = cast(InputData, {"id": "test6", "data": header + rows})
        assert self.transformer.detect_my_data_structure(input_data) is True

    def test_detect_performance_for_large_data(self) -> None:
        """Test detection completes in <0.01s for large data (>1KB), verifying 1KB sampling works."""
        # Create 100KB of FWCTABLE data (much larger than 1KB sample)
        header = "col1      col2      col3      col4      col5      col6      col7      col8\n"
        rows = "\n".join(
            [
                f"val{i}      val{i}      val{i}      val{i}      val{i}      val{i}      val{i}      val{i}"
                for i in range(1000)
            ]
        )
        input_data = cast(InputData, {"id": "perf_test", "data": header + rows})

        start_time = time.perf_counter()
        result = self.transformer.detect_my_data_structure(input_data)
        elapsed_time = time.perf_counter() - start_time

        assert result is True
        assert (
            elapsed_time < 0.01
        ), f"Detection took {elapsed_time:.4f}s, expected <0.01s"

    def test_detect_invalid_column_count_mismatch_fewer_data_columns(self) -> None:
        """Test detection returns False when data line has fewer columns than header."""
        input_data = cast(
            InputData,
            {
                "id": "test7",
                "data": "name    age  city\nJohn    30",
            },
        )
        # Header has 3 columns but data line has only 2 columns
        assert self.transformer.detect_my_data_structure(input_data) is False

    def test_detect_invalid_column_count_mismatch_more_data_columns(self) -> None:
        """Test detection returns False when data line has more columns than header."""
        input_data = cast(
            InputData,
            {
                "id": "test8",
                "data": "name    age\nJohn    30   New York",
            },
        )
        # Header has 2 columns but data line has 3 columns
        assert self.transformer.detect_my_data_structure(input_data) is False

    def test_detect_invalid_single_space_delimited_data(self) -> None:
        """Test detection returns False when data rows use single spaces instead of 2+ whitespace."""
        input_data = cast(
            InputData,
            {
                "id": "test9",
                "data": "name    age  city\nJohn 30 New York\nJane 25 Boston",
            },
        )
        # Header has multiple spaces, but data rows use single spaces
        assert self.transformer.detect_my_data_structure(input_data) is False

    def test_detect_valid_when_data_aligns_with_header_columns(self) -> None:
        """Test detection returns True when data aligns with header column positions."""
        input_data = cast(
            InputData,
            {
                "id": "test10",
                "data": "name    age  city\nJohn    30   New York\nJane    25   Boston",
            },
        )
        # Both header and data rows have proper alignment with matching column counts
        assert self.transformer.detect_my_data_structure(input_data) is True
