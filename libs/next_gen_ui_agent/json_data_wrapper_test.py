import json

from next_gen_ui_agent.json_data_wrapper import wrap_json_data, wrap_string_as_json


class TestWrapStringAsJson:
    """Test cases for wrap_string_as_json method."""

    def test_empty_data_type_returns_data_unchanged(self):
        """Test that empty or None data_type returns data unchanged."""
        assert wrap_string_as_json("val", "") == {"data": "val"}

    def test_none_data_type_returns_data_unchanged(self):
        """Test that None data_type returns data unchanged."""
        assert wrap_string_as_json("test", None) == {"data": "test"}

    def test_valid_data_type_returns_data_wrapped(self):
        """Test that valid data_type returns data wrapped."""
        assert wrap_string_as_json("test \nvalue", "test.type") == {
            "test_type": "test \nvalue"
        }

    def test_empty_data_are_wrapped(self):
        """Test that empty data are wrapped."""
        assert wrap_string_as_json("", "test.type") == {"test_type": ""}

    def test_max_length_truncates_data(self):
        """Test that max_length truncates data."""
        assert wrap_string_as_json("test \nvalue", "test.type", max_length=5) == {
            "test_type": "test ..."
        }

    def test_max_length_truncates_data_short(self):
        """Test that max_length truncates data."""
        assert wrap_string_as_json("test \nvalue", "test.type", max_length=500) == {
            "test_type": "test \nvalue"
        }


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
