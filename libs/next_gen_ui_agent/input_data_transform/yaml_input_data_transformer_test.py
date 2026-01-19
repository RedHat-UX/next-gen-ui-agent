import json
from typing import cast

import pytest
from jsonpath_ng import parse  # type: ignore
from next_gen_ui_agent.input_data_transform.yaml_input_data_transformer import (
    YamlInputDataTransformer,
)
from next_gen_ui_agent.types import InputData
from pydantic import BaseModel


class TestYamlInputDataTransformer:
    """Test cases for YamlInputDataTransformer."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.transformer = YamlInputDataTransformer()

    def test_transform_valid_yaml_object(self) -> None:
        """Test transforming a valid YAML object."""
        input_data = """
name: John
age: 30
city: New York
"""
        result = self.transformer.transform(input_data)

        expected = {"name": "John", "age": 30, "city": "New York"}
        assert result == expected
        assert isinstance(result, dict)

    def test_transform_valid_yaml_array(self) -> None:
        """Test transforming a valid YAML array."""
        input_data = """
- 1
- 2
- 3
- hello
- nested: object
"""
        result = self.transformer.transform(input_data)

        expected = [1, 2, 3, "hello", {"nested": "object"}]
        assert result == expected
        assert isinstance(result, list)

    def test_transform_valid_yaml_nested_structure(self) -> None:
        """Test transforming a complex nested YAML structure."""
        input_data = """
users:
  - id: 1
    name: Alice
    profile:
      age: 25
      preferences:
        theme: dark
        notifications: true
  - id: 2
    name: Bob
    profile:
      age: 30
      preferences:
        theme: light
        notifications: false
metadata:
  total: 2
  last_updated: "2024-01-01T00:00:00Z"
"""
        result = self.transformer.transform(input_data)

        assert isinstance(result, dict)
        assert "users" in result
        assert "metadata" in result
        assert len(result["users"]) == 2
        assert result["users"][0]["name"] == "Alice"
        assert result["users"][1]["name"] == "Bob"
        assert result["metadata"]["total"] == 2

    def test_transform_invalid_yaml_syntax(self) -> None:
        """Test transforming invalid YAML with syntax error."""
        input_data = """
name: John
age: 30
  city: New York  # Invalid indentation
"""

        with pytest.raises(ValueError, match="Invalid YAML format of the Input Data: "):
            self.transformer.transform(input_data)

    def test_transform_invalid_yaml_tabs(self) -> None:
        """Test transforming invalid YAML with tabs instead of spaces."""
        input_data = """
name: John
age: 30
\tcity: New York
"""

        with pytest.raises(ValueError, match="Invalid YAML format of the Input Data: "):
            self.transformer.transform(input_data)

    def test_transform_empty_string(self) -> None:
        """Test transforming empty string."""
        input_data = ""

        with pytest.raises(ValueError, match="Invalid YAML format of the Input Data: "):
            self.transformer.transform(input_data)

    def test_transform_whitespace_only(self) -> None:
        """Test transforming whitespace-only string."""
        input_data = "   \n\t  "

        with pytest.raises(ValueError, match="Invalid YAML format of the Input Data: "):
            self.transformer.transform(input_data)

    def test_transform_valid_yaml_with_comments(self) -> None:
        """Test transforming valid YAML with comments."""
        input_data = """
# This is a comment
name: John  # Another comment
age: 30
city: New York
"""
        result = self.transformer.transform(input_data)

        expected = {"name": "John", "age": 30, "city": "New York"}
        assert result == expected

    def test_transform_valid_yaml_with_multiline_strings(self) -> None:
        """Test transforming YAML with multiline strings."""
        input_data = """
description: |
  This is a multiline
  string that spans
  multiple lines
title: "Simple Title"
"""
        result = self.transformer.transform(input_data)

        assert isinstance(result, dict)
        assert "description" in result
        assert "title" in result
        assert "multiline" in result["description"]

    def test_transform_empty_object(self) -> None:
        """Test transforming empty YAML object."""
        input_data = "{}"
        result = self.transformer.transform(input_data)

        assert result == {}
        assert isinstance(result, dict)

    def test_transform_empty_array(self) -> None:
        """Test transforming empty YAML array."""
        input_data = "[]"
        result = self.transformer.transform(input_data)

        assert result == []
        assert isinstance(result, list)

    def test_transform_rejects_string_root(self) -> None:
        """Test that string root values are rejected."""
        input_data = "hello world"

        with pytest.raises(
            ValueError,
            match="Invalid YAML format of the Input Data: YAML root must be an object or array",
        ):
            self.transformer.transform(input_data)

    def test_transform_rejects_number_root(self) -> None:
        """Test that number root values are rejected."""
        input_data = "42"

        with pytest.raises(
            ValueError,
            match="Invalid YAML format of the Input Data: YAML root must be an object or array",
        ):
            self.transformer.transform(input_data)

    def test_transform_rejects_float_root(self) -> None:
        """Test that float root values are rejected."""
        input_data = "3.14"

        with pytest.raises(
            ValueError,
            match="Invalid YAML format of the Input Data: YAML root must be an object or array",
        ):
            self.transformer.transform(input_data)

    def test_transform_rejects_boolean_root(self) -> None:
        """Test that boolean root values are rejected."""
        input_data = "true"

        with pytest.raises(
            ValueError,
            match="Invalid YAML format of the Input Data: YAML root must be an object or array",
        ):
            self.transformer.transform(input_data)

    def test_transform_rejects_null_root(self) -> None:
        """Test that null root values are rejected."""
        input_data = "null"

        with pytest.raises(
            ValueError,
            match="Invalid YAML format of the Input Data: YAML root must be an object or array",
        ):
            self.transformer.transform(input_data)

    def test_transform_accepts_object_root(self) -> None:
        """Test that object root values are accepted."""
        input_data = """
key: value
"""
        result = self.transformer.transform(input_data)

        assert result == {"key": "value"}
        assert isinstance(result, dict)

    def test_transform_accepts_array_root(self) -> None:
        """Test that array root values are accepted."""
        input_data = """
- 1
- 2
- 3
- test
"""
        result = self.transformer.transform(input_data)

        assert result == [1, 2, 3, "test"]
        assert isinstance(result, list)

    def test_transform_output_serializable_with_pydantic(self) -> None:
        """Test that transformer output can be serialized using Pydantic model_dump_json()."""

        # Create a simple Pydantic model for testing
        class TestModel(BaseModel):
            data: dict

        # Test with object root
        input_data = """
name: John
age: 30
city: New York
"""
        result = self.transformer.transform(input_data)

        # Create a Pydantic model instance with the transformed data
        model = TestModel(data=result)

        # Verify that model_dump_json() works without errors
        json_output = model.model_dump_json()
        assert isinstance(json_output, str)

        # Verify the JSON can be parsed back
        parsed_back = json.loads(json_output)
        assert "data" in parsed_back
        assert parsed_back["data"] == result

    def test_transform_output_serializable_with_pydantic_array(self) -> None:
        """Test that transformer output with array root can be serialized using Pydantic model_dump_json()."""

        # Create a simple Pydantic model for testing arrays
        class TestArrayModel(BaseModel):
            items: list

        # Test with array root
        input_data = """
- id: 1
  name: Alice
- id: 2
  name: Bob
"""
        result = self.transformer.transform(input_data)

        # Create a Pydantic model instance with the transformed data
        model = TestArrayModel(items=result)

        # Verify that model_dump_json() works without errors
        json_output = model.model_dump_json()
        assert isinstance(json_output, str)

        parsed_back = json.loads(json_output)
        assert "items" in parsed_back
        assert parsed_back["items"] == result

    def test_transform_output_accessible_with_jsonpath_ng_object(self) -> None:
        """Test that transformer output can be accessed using jsonpath_ng for object data."""
        # Test with complex nested object
        input_data = """
users:
  - id: 1
    name: Alice
    profile:
      age: 25
      preferences:
        theme: dark
        notifications: true
  - id: 2
    name: Bob
    profile:
      age: 30
      preferences:
        theme: light
        notifications: false
metadata:
  total: 2
  last_updated: "2024-01-01T00:00:00Z"
"""
        result = self.transformer.transform(input_data)

        # Test various jsonpath expressions
        # Access root level
        root_path = parse("$")
        root_matches = [match.value for match in root_path.find(result)]
        assert len(root_matches) == 1
        assert root_matches[0] == result

        # Access users array
        users_path = parse("$.users")
        users_matches = [match.value for match in users_path.find(result)]
        assert len(users_matches) == 1
        assert len(users_matches[0]) == 2

        # Access specific user by index
        first_user_path = parse("$.users[0]")
        first_user_matches = [match.value for match in first_user_path.find(result)]
        assert len(first_user_matches) == 1
        assert first_user_matches[0]["name"] == "Alice"
        assert first_user_matches[0]["id"] == 1

        # Access nested properties
        alice_age_path = parse("$.users[0].profile.age")
        alice_age_matches = [match.value for match in alice_age_path.find(result)]
        assert len(alice_age_matches) == 1
        assert alice_age_matches[0] == 25

        # Access all user names
        all_names_path = parse("$.users[*].name")
        all_names_matches = [match.value for match in all_names_path.find(result)]
        assert len(all_names_matches) == 2
        assert "Alice" in all_names_matches
        assert "Bob" in all_names_matches

        # Access metadata
        metadata_path = parse("$.metadata")
        metadata_matches = [match.value for match in metadata_path.find(result)]
        assert len(metadata_matches) == 1
        assert metadata_matches[0]["total"] == 2

    def test_transform_output_accessible_with_jsonpath_ng_array(self) -> None:
        """Test that transformer output can be accessed using jsonpath_ng for array data."""
        # Test with array of objects
        input_data = """
- id: 1
  name: Alice
  scores:
    - 85
    - 90
    - 78
- id: 2
  name: Bob
  scores:
    - 92
    - 88
    - 95
- id: 3
  name: Charlie
  scores:
    - 76
    - 82
    - 80
"""
        result = self.transformer.transform(input_data)

        # Test various jsonpath expressions for array data
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
        assert first_item_matches[0]["id"] == 1

        # Access all names
        all_names_path = parse("$[*].name")
        all_names_matches = [match.value for match in all_names_path.find(result)]
        assert len(all_names_matches) == 3
        assert "Alice" in all_names_matches
        assert "Bob" in all_names_matches
        assert "Charlie" in all_names_matches

        # Access all scores arrays
        all_scores_path = parse("$[*].scores")
        all_scores_matches = [match.value for match in all_scores_path.find(result)]
        assert len(all_scores_matches) == 3
        assert [85, 90, 78] in all_scores_matches
        assert [92, 88, 95] in all_scores_matches
        assert [76, 82, 80] in all_scores_matches

        # Access specific score by nested index
        alice_first_score_path = parse("$[0].scores[0]")
        alice_first_score_matches = [
            match.value for match in alice_first_score_path.find(result)
        ]
        assert len(alice_first_score_matches) == 1
        assert alice_first_score_matches[0] == 85

    def test_transform_output_accessible_with_jsonpath_ng_mixed_data(self) -> None:
        """Test that transformer output can be accessed using jsonpath_ng for mixed object/array data."""
        # Test with mixed structure
        input_data = """
departments:
  - name: Engineering
    employees:
      - name: Alice
        role: Developer
      - name: Bob
        role: Senior Developer
  - name: Marketing
    employees:
      - name: Charlie
        role: Manager
      - name: Diana
        role: Specialist
company:
  name: TechCorp
  founded: 2020
"""
        result = self.transformer.transform(input_data)

        # Test complex jsonpath expressions
        # Access all employee names across all departments
        all_employee_names_path = parse("$.departments[*].employees[*].name")
        all_employee_names_matches = [
            match.value for match in all_employee_names_path.find(result)
        ]
        assert len(all_employee_names_matches) == 4
        assert "Alice" in all_employee_names_matches
        assert "Bob" in all_employee_names_matches
        assert "Charlie" in all_employee_names_matches
        assert "Diana" in all_employee_names_matches

        # Access all roles
        all_roles_path = parse("$.departments[*].employees[*].role")
        all_roles_matches = [match.value for match in all_roles_path.find(result)]
        assert len(all_roles_matches) == 4
        assert "Developer" in all_roles_matches
        assert "Senior Developer" in all_roles_matches
        assert "Manager" in all_roles_matches
        assert "Specialist" in all_roles_matches

        # Access company name
        company_name_path = parse("$.company.name")
        company_name_matches = [match.value for match in company_name_path.find(result)]
        assert len(company_name_matches) == 1
        assert company_name_matches[0] == "TechCorp"

        # Access specific department
        engineering_path = parse("$.departments[0]")
        engineering_matches = [match.value for match in engineering_path.find(result)]
        assert len(engineering_matches) == 1
        assert engineering_matches[0]["name"] == "Engineering"
        assert len(engineering_matches[0]["employees"]) == 2


class TestYamlInputDataTransformerDetectMyDataStructure:
    """Test cases for YamlInputDataTransformer.detect_my_data_structure()."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.transformer = YamlInputDataTransformer()

    def test_detect_valid_yaml_with_document_marker(self) -> None:
        """Test detection returns True for YAML with document marker (covers: --- pattern)."""
        input_data = cast(
            InputData, {"id": "test1", "data": "---\nname: John\nage: 30"}
        )
        assert self.transformer.detect_my_data_structure(input_data) is True

    def test_detect_valid_yaml_with_colon_space(self) -> None:
        """Test detection returns True for YAML with key: value (covers: ': ' pattern)."""
        input_data = cast(InputData, {"id": "test2", "data": "name: John\nage: 30"})
        assert self.transformer.detect_my_data_structure(input_data) is True

    def test_detect_valid_yaml_with_colon_newline(self) -> None:
        """Test detection returns True for YAML with key:\\n (covers: ':\\n' pattern)."""
        input_data = cast(
            InputData, {"id": "test3", "data": "key:\n  - value1\n  - value2"}
        )
        assert self.transformer.detect_my_data_structure(input_data) is True

    def test_detect_valid_yaml_with_list_marker(self) -> None:
        """Test detection returns True for YAML with list markers (covers: '\\n- ' or starts with '- ')."""
        input_data = cast(
            InputData, {"id": "test4", "data": "- item1\n- item2\n- item3"}
        )
        assert self.transformer.detect_my_data_structure(input_data) is True

    def test_detect_invalid_json_exclusion(self) -> None:
        """Test detection returns False for JSON (covers: starts with { or [ exclusion)."""
        assert (
            self.transformer.detect_my_data_structure(
                cast(InputData, {"id": "test5", "data": '{"name": "John"}'})
            )
            is False
        )
        assert (
            self.transformer.detect_my_data_structure(
                cast(InputData, {"id": "test6", "data": "[1, 2, 3]"})
            )
            is False
        )

    def test_detect_invalid_no_yaml_patterns(self) -> None:
        """Test detection returns False when no YAML patterns found (covers: no match case)."""
        input_data = cast(InputData, {"id": "test7", "data": "This is just plain text"})
        assert self.transformer.detect_my_data_structure(input_data) is False

    def test_detect_empty_or_whitespace(self) -> None:
        """Test detection returns False for empty/whitespace data (covers: empty check)."""
        assert (
            self.transformer.detect_my_data_structure(
                cast(InputData, {"id": "test8", "data": ""})
            )
            is False
        )

    def test_detect_large_yaml_samples_first_1kb(self) -> None:
        """Test detection with large YAML (>1KB) uses sampling (covers: 1KB sampling)."""
        large_yaml = "---\n" + "\n".join([f"item_{i}: value_{i}" for i in range(100)])
        input_data = cast(InputData, {"id": "test9", "data": large_yaml})
        assert self.transformer.detect_my_data_structure(input_data) is True
