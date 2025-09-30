import json

from next_gen_ui_agent.json_data_wrapper import _sanitize_field_name, wrap_json_data


class TestSanitizeFieldName:
    """Test cases for _sanitize_field_name method."""

    def test_empty_string_returns_none(self):
        """Test that empty string returns None."""
        assert _sanitize_field_name("") is None

    def test_none_returns_none(self):
        """Test that None returns None."""
        assert _sanitize_field_name(None) is None

    def test_valid_field_names_unchanged(self):
        """Test that valid field names remain unchanged."""
        valid_names = [
            "field",
            "field_name",
            "field-name",
            "field123",
            "field_name_123",
            "field-name-123",
            "a",
            "A",
            "fieldName",
            "field_name_123_test",
        ]

        for name in valid_names:
            assert _sanitize_field_name(name) == name

    def test_invalid_characters_replaced_with_underscores(self):
        """Test that invalid characters are replaced with underscores."""
        test_cases = [
            ("field@name", "field_name"),
            ("field#name", "field_name"),
            ("field$name", "field_name"),
            ("field%name", "field_name"),
            ("field^name", "field_name"),
            ("field&name", "field_name"),
            ("field*name", "field_name"),
            ("field(name", "field_name"),
            ("field)name", "field_name"),
            ("field+name", "field_name"),
            ("field=name", "field_name"),
            ("field[name", "field_name"),
            ("field]name", "field_name"),
            ("field{name", "field_name"),
            ("field}name", "field_name"),
            ("field|name", "field_name"),
            ("field\\name", "field_name"),
            ("field:name", "field_name"),
            ("field;name", "field_name"),
            ("field'name", "field_name"),
            ('field"name', "field_name"),
            ("field<name", "field_name"),
            ("field>name", "field_name"),
            ("field,name", "field_name"),
            ("field.name", "field_name"),
            ("field?name", "field_name"),
            ("field/name", "field_name"),
            ("field name", "field_name"),
            ("field\tname", "field_name"),
            ("field\nname", "field_name"),
            ("field\rname", "field_name"),
        ]

        for input_name, expected in test_cases:
            assert _sanitize_field_name(input_name) == expected

    def test_starts_with_number_gets_field_prefix(self):
        """Test that field names starting with numbers get 'field_' prefix."""
        test_cases = [
            ("123field", "field_123field"),
            ("0field", "field_0field"),
            ("9field", "field_9field"),
            ("123", "field_123"),
            ("0", "field_0"),
        ]

        for input_name, expected in test_cases:
            assert _sanitize_field_name(input_name) == expected

    def test_starts_with_hyphen_gets_field_prefix(self):
        """Test that field names starting with hyphens get 'field_' prefix."""
        test_cases = [
            ("-field", "field_-field"),
            ("-123", "field_-123"),
            ("-", "field_-"),
            ("-field-name", "field_-field-name"),
        ]

        for input_name, expected in test_cases:
            assert _sanitize_field_name(input_name) == expected

    def test_multiple_invalid_characters(self):
        """Test field names with multiple invalid characters."""
        test_cases = [
            ("field@#$%name", "field____name"),
            ("@#$%field", "____field"),
            ("field@#$%", "field____"),
            ("@#$%", "____"),
        ]

        for input_name, expected in test_cases:
            assert _sanitize_field_name(input_name) == expected

    def test_only_invalid_characters(self):
        """Test field names with only invalid characters."""
        test_cases = [
            ("@#$%", "____"),
            ("!@#$%^&*()", "__________"),
            ("   ", None),
            ("\t\n\r", None),
        ]

        for input_name, expected in test_cases:
            assert _sanitize_field_name(input_name) == expected

    def test_mixed_valid_invalid_characters(self):
        """Test field names with mixed valid and invalid characters."""
        test_cases = [
            ("field@name123", "field_name123"),
            ("field-name@test", "field-name_test"),
            ("field_name@test#123", "field_name_test_123"),
            ("a@b#c$d%e^f&g", "a_b_c_d_e_f_g"),
        ]

        for input_name, expected in test_cases:
            assert _sanitize_field_name(input_name) == expected

    def test_unicode_characters(self):
        """Test field names with unicode characters."""
        test_cases = [
            ("fieldñame", "field_ame"),
            ("field中文", "field__"),
            ("fieldαβγ", "field___"),
            ("field🚀", "field_"),
        ]

        for input_name, expected in test_cases:
            assert _sanitize_field_name(input_name) == expected

    def test_very_long_field_names(self):
        """Test very long field names."""
        long_name = "a" * 1000
        assert _sanitize_field_name(long_name) == long_name

        long_name_with_invalid = "a" * 500 + "@" + "b" * 500
        expected = "a" * 500 + "_" + "b" * 500
        assert _sanitize_field_name(long_name_with_invalid) == expected

    def test_edge_cases(self):
        """Test edge cases."""
        # Single character
        assert _sanitize_field_name("a") == "a"
        assert _sanitize_field_name("1") == "field_1"
        assert _sanitize_field_name("-") == "field_-"
        assert _sanitize_field_name("@") == "_"

        # Only underscores and hyphens
        assert _sanitize_field_name("_") == "_"
        assert _sanitize_field_name("-") == "field_-"
        assert _sanitize_field_name("_-") == "_-"
        assert _sanitize_field_name("-_") == "field_-_"


class TestWrapJsonData:
    """Test cases for wrap_json_data method."""

    def test_empty_data_type_returns_data_unchanged(self):
        """Test that empty or None data_type returns data unchanged."""
        test_data = {"key": "value"}

        # Empty string
        assert wrap_json_data(test_data, "") == test_data

        # None (if passed as string "None")
        assert wrap_json_data(test_data, "None") == test_data

        # Whitespace only
        assert wrap_json_data(test_data, "   ") == test_data

    def test_dict_with_multiple_fields_gets_wrapped(self):
        """Test that dict with multiple fields gets wrapped."""
        data = {"name": "John", "age": 30, "city": "New York"}
        result = wrap_json_data(data, "person")
        expected = {"person": {"name": "John", "age": 30, "city": "New York"}}
        assert result == expected

    def test_dict_with_single_field_unchanged(self):
        """Test that dict with single field remains unchanged."""
        data = {"name": "John"}
        result = wrap_json_data(data, "person")
        assert result == data

    def test_empty_dict_unchanged(self):
        """Test that empty dict remains unchanged."""
        data = {}
        result = wrap_json_data(data, "person")
        assert result == data

    def test_list_gets_wrapped(self):
        """Test that list gets wrapped."""
        data = [1, 2, 3, 4, 5]
        result = wrap_json_data(data, "numbers")
        expected = {"numbers": [1, 2, 3, 4, 5]}
        assert result == expected

    def test_empty_list_is_wrapped(self):
        """Test that empty list gets wrapped."""
        data = []
        result = wrap_json_data(data, "items")
        expected = {"items": []}
        assert result == expected

    def test_one_item_list_is_wrapped(self):
        """Test that empty list gets wrapped."""
        data = [{}]
        result = wrap_json_data(data, "items")
        expected = {"items": [{}]}
        assert result == expected

    def test_custom_iterable_gets_wrapped(self):
        """Test that custom iterable gets wrapped."""

        class CustomIterable:
            def __init__(self, items):
                self.items = items

            def __iter__(self):
                return iter(self.items)

            def __len__(self):
                return len(self.items)

            def __sizeof__(self) -> int:
                return len(self.items)

        data = CustomIterable([1, 2, 3])
        result = wrap_json_data(data, "custom")
        expected = {"custom": data}
        assert result == expected

    def test_data_type_sanitization(self):
        """Test that data_type is properly sanitized."""
        # Use a dict with multiple fields so it gets wrapped
        data = {"key1": "value1", "key2": "value2"}

        # Invalid characters in data_type
        result = wrap_json_data(data, "my@data#type")
        expected = {"my_data_type": {"key1": "value1", "key2": "value2"}}
        assert result == expected

        # Data_type starting with number
        result = wrap_json_data(data, "123type")
        expected = {"field_123type": {"key1": "value1", "key2": "value2"}}
        assert result == expected

        # Data_type starting with hyphen
        result = wrap_json_data(data, "-type")
        expected = {"field_-type": {"key1": "value1", "key2": "value2"}}
        assert result == expected

    def test_nested_structures(self):
        """Test with nested data structures."""
        # Nested dict
        data = {
            "user": {"name": "John", "age": 30},
            "settings": {"theme": "dark", "notifications": True},
        }
        result = wrap_json_data(data, "config")
        expected = {"config": data}
        assert result == expected

        # List of dicts
        data = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
        result = wrap_json_data(data, "items")
        expected = {"items": data}
        assert result == expected

    def test_large_data_structures(self):
        """Test with large data structures."""
        # Large list
        data = list(range(1000))
        result = wrap_json_data(data, "large_list")
        expected = {"large_list": data}
        assert result == expected

        # Large dict
        data = {f"key_{i}": f"value_{i}" for i in range(100)}
        result = wrap_json_data(data, "large_dict")
        expected = {"large_dict": data}
        assert result == expected

    def test_single_item_dict_not_wrapped(self):
        """Test single item dict is not wrapped."""

        data = {"single_key": "single_value"}
        result = wrap_json_data(data, "wrapper")
        assert result == data

    def test_json_loaded_data(self):
        # dict with multiple fields
        json_str = '{"numbers": [1, 2, 3, 4, 5], "info": {"tags": ["a", "b", "c"]}, "label": "test"}'
        data = json.loads(json_str)
        result = wrap_json_data(data, "large_dict")
        expected = {"large_dict": data}
        assert result == expected

        # array
        json_str = "[1, 2, 3, 4, 5]"
        data = json.loads(json_str)
        result = wrap_json_data(data, "large_dict")
        expected = {"large_dict": data}
        assert result == expected
