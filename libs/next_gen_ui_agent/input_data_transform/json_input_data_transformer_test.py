import json

import pytest
from next_gen_ui_agent.input_data_transform.json_input_data_transformer import (
    JsonInputDataTransformer,
)


class TestJsonInputDataTransformer:
    """Test cases for JsonInputDataTransformer."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.transformer = JsonInputDataTransformer()

    def test_transform_valid_json_object(self) -> None:
        """Test transforming a valid JSON object."""
        input_data = '{"name": "John", "age": 30, "city": "New York"}'
        result = self.transformer.transform(input_data)

        expected = {"name": "John", "age": 30, "city": "New York"}
        assert result == expected
        assert isinstance(result, dict)

    def test_transform_valid_json_array(self) -> None:
        """Test transforming a valid JSON array."""
        input_data = '[1, 2, 3, "hello", {"nested": "object"}]'
        result = self.transformer.transform(input_data)

        expected = [1, 2, 3, "hello", {"nested": "object"}]
        assert result == expected
        assert isinstance(result, list)

    def test_transform_valid_json_nested_structure(self) -> None:
        """Test transforming a complex nested JSON structure."""
        input_data = """
        {
            "users": [
                {
                    "id": 1,
                    "name": "Alice",
                    "profile": {
                        "age": 25,
                        "preferences": {
                            "theme": "dark",
                            "notifications": true
                        }
                    }
                },
                {
                    "id": 2,
                    "name": "Bob",
                    "profile": {
                        "age": 30,
                        "preferences": {
                            "theme": "light",
                            "notifications": false
                        }
                    }
                }
            ],
            "metadata": {
                "total": 2,
                "last_updated": "2024-01-01T00:00:00Z"
            }
        }
        """
        result = self.transformer.transform(input_data)

        assert isinstance(result, dict)
        assert "users" in result
        assert "metadata" in result
        assert len(result["users"]) == 2
        assert result["users"][0]["name"] == "Alice"
        assert result["users"][1]["name"] == "Bob"
        assert result["metadata"]["total"] == 2

    def test_transform_invalid_json_missing_quote(self) -> None:
        """Test transforming invalid JSON with missing quote."""
        input_data = '{"name": "John, "age": 30}'

        with pytest.raises(ValueError, match="Invalid JSON format of the Input Data"):
            self.transformer.transform(input_data)

    def test_transform_invalid_json_missing_brace(self) -> None:
        """Test transforming invalid JSON with missing closing brace."""
        input_data = '{"name": "John", "age": 30'

        with pytest.raises(ValueError, match="Invalid JSON format of the Input Data"):
            self.transformer.transform(input_data)

    def test_transform_invalid_json_trailing_comma(self) -> None:
        """Test transforming invalid JSON with trailing comma."""
        input_data = '{"name": "John", "age": 30,}'

        with pytest.raises(ValueError, match="Invalid JSON format of the Input Data"):
            self.transformer.transform(input_data)

    def test_transform_invalid_json_undefined(self) -> None:
        """Test transforming invalid JSON with undefined value."""
        input_data = '{"name": "John", "age": undefined}'

        with pytest.raises(ValueError, match="Invalid JSON format of the Input Data"):
            self.transformer.transform(input_data)

    def test_transform_invalid_json_single_quotes(self) -> None:
        """Test transforming invalid JSON with single quotes."""
        input_data = "{'name': 'John', 'age': 30}"

        with pytest.raises(ValueError, match="Invalid JSON format of the Input Data"):
            self.transformer.transform(input_data)

    def test_transform_empty_string(self) -> None:
        """Test transforming empty string."""
        input_data = ""

        with pytest.raises(ValueError, match="Invalid JSON format of the Input Data"):
            self.transformer.transform(input_data)

    def test_transform_whitespace_only(self) -> None:
        """Test transforming whitespace-only string."""
        input_data = "   \n\t  "

        with pytest.raises(ValueError, match="Invalid JSON format of the Input Data"):
            self.transformer.transform(input_data)

    def test_transform_valid_json_with_whitespace(self) -> None:
        """Test transforming valid JSON with extra whitespace."""
        input_data = '  {  "name"  :  "John"  ,  "age"  :  30  }  '
        result = self.transformer.transform(input_data)

        expected = {"name": "John", "age": 30}
        assert result == expected

    def test_transform_valid_json_with_newlines(self) -> None:
        """Test transforming valid JSON with newlines and indentation."""
        input_data = """{
            "name": "John",
            "age": 30,
            "city": "New York"
        }"""
        result = self.transformer.transform(input_data)

        expected = {"name": "John", "age": 30, "city": "New York"}
        assert result == expected

    def test_transform_special_characters(self) -> None:
        """Test transforming JSON with special characters."""
        input_data = (
            '{"message": "Hello, \\"World\\"! \\n Line break \\t tab", "unicode": "🚀"}'
        )
        result = self.transformer.transform(input_data)

        expected = {"message": 'Hello, "World"! \n Line break \t tab', "unicode": "🚀"}
        assert result == expected

    def test_transform_empty_object(self) -> None:
        """Test transforming empty JSON object."""
        input_data = "{}"
        result = self.transformer.transform(input_data)

        assert result == {}
        assert isinstance(result, dict)

    def test_transform_empty_array(self) -> None:
        """Test transforming empty JSON array."""
        input_data = "[]"
        result = self.transformer.transform(input_data)

        assert result == []
        assert isinstance(result, list)

    def test_transform_numeric_edge_cases(self) -> None:
        """Test transforming numeric edge cases."""
        test_cases = [
            ("0", 0),
            ("-0", 0),
            ("1.0", 1.0),
            ("-1.0", -1.0),
            ("1e10", 1e10),
            ("1E-10", 1e-10),
            ("-1e10", -1e10),
        ]

        for input_data, expected in test_cases:
            result = self.transformer.transform(input_data)
            assert result == expected

    def test_transform_boolean_edge_cases(self) -> None:
        """Test transforming boolean edge cases."""
        test_cases = [
            ("true", True),
            ("false", False),
        ]

        for input_data, expected in test_cases:
            result = self.transformer.transform(input_data)
            assert result == expected

    def test_transform_large_json(self) -> None:
        """Test transforming a large JSON structure."""
        # Create a large JSON structure
        large_data = {
            "items": [{"id": i, "value": f"item_{i}"} for i in range(1000)],
            "metadata": {"count": 1000, "type": "large_dataset"},
        }
        input_data = json.dumps(large_data)

        result = self.transformer.transform(input_data)

        assert result == large_data
        assert len(result["items"]) == 1000
        assert result["metadata"]["count"] == 1000
