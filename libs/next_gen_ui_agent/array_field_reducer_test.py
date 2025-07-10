# Substantial portions of this file were generated with help of Cursor AI

import json
from copy import deepcopy

from next_gen_ui_agent.array_field_reducer import reduce_arrays


def test_flat_dict_with_array():
    data = {"numbers": [1, 2, 3, 4], "label": "foo", "value": 42}
    deep_copy = deepcopy(data)
    expected = {"numbers[size: 4]": [1, 2], "label": "foo", "value": 42}
    assert reduce_arrays(data) == expected
    # make sure input data are not altered!
    assert data == deep_copy


def test_flat_dict_with_array_BOUNDARY_MORE():
    data = {"numbers": [1, 2, 3, 4], "label": "foo", "value": 42}
    expected = {"numbers[size over 3]": [1, 2], "label": "foo", "value": 42}
    assert reduce_arrays(data, 3) == expected


def test_flat_dict_with_array_BOUNDARY_SAME():
    data = {"numbers": [1, 2, 3, 4], "label": "foo", "value": 42}
    expected = {"numbers[size up to 4]": [1, 2], "label": "foo", "value": 42}
    assert reduce_arrays(data, 4) == expected


def test_flat_dict_with_array_BOUNDARY_LESS():
    data = {"numbers": [1, 2, 3, 4], "label": "foo", "value": 42}
    expected = {"numbers[size up to 5]": [1, 2], "label": "foo", "value": 42}
    assert reduce_arrays(data, 5) == expected


def test_nested_dict_with_array():
    data = {"a": {"b": [10, 20, 30, 40, 50], "c": "bar"}, "d": 99}
    expected = {"a": {"b[size: 5]": [10, 20], "c": "bar"}, "d": 99}
    assert reduce_arrays(data) == expected


def test_list_of_dicts():
    data = {
        "items": [{"x": [1, 2, 3], "name": "A"}, {"y": [4, 5, 6, 7], "name": "B"}],
        "meta": True,
    }
    expected = {
        "items[size: 2]": [
            {"x[size: 3]": [1, 2], "name": "A"},
            {"y[size: 4]": [4, 5], "name": "B"},
        ],
        "meta": True,
    }
    assert reduce_arrays(data) == expected


def test_array_of_arrays():
    data = {"matrix": [[1, 2, 3], [4]], "desc": "mat"}
    expected = {"matrix[size: 2]": [[1, 2], [4]], "desc": "mat"}
    assert reduce_arrays(data) == expected


def test_no_arrays():
    data = {"a": 1, "b": {"c": "hello", "d": 2.5}, "flag": False}
    expected = {"a": 1, "b": {"c": "hello", "d": 2.5}, "flag": False}
    assert reduce_arrays(data) == expected


def test_empty_array():
    data = {"empty": [], "note": "should stay"}
    expected = {"empty[size: 0]": [], "note": "should stay"}
    assert reduce_arrays(data) == expected


def test_complex_nesting():
    data = {
        "a": [
            {"b": [1, 2, 3, 4], "t": "x"},
            {"c": {"d": [5, 6, 7], "e": "y"}, "f": 123},
        ],
        "e": {"f": [[8, 9, 10], [11, 12]], "g": "z"},
        "h": "root",
    }
    expected = {
        "a[size: 2]": [
            {"b[size: 4]": [1, 2], "t": "x"},
            {"c": {"d[size: 3]": [5, 6], "e": "y"}, "f": 123},
        ],
        "e": {"f[size: 2]": [[8, 9], [11, 12]], "g": "z"},
        "h": "root",
    }
    assert reduce_arrays(data) == expected


def test_with_tuples():
    """Test that the function works with tuples as iterables."""
    data = {"coordinates": (1, 2, 3, 4, 5), "name": "point"}
    expected = {"coordinates[size: 5]": [1, 2], "name": "point"}
    assert reduce_arrays(data) == expected


def test_with_sets():
    """Test that the function works with sets as iterables."""
    data = {"unique_values": {1, 2, 3, 4, 5}, "description": "set"}
    result = reduce_arrays(data)
    # Sets don't preserve order, so we check the structure and size
    assert "unique_values[size: 5]" in result
    assert len(result["unique_values[size: 5]"]) == 2
    assert result["description"] == "set"


def test_with_generator():
    """Test that the function works with generators as iterables."""

    def number_gen():
        for i in range(1, 6):
            yield i

    data = {"generated": number_gen(), "type": "generator"}
    expected = {"generated[size: 5]": [1, 2], "type": "generator"}
    assert reduce_arrays(data) == expected


def test_strings_not_affected():
    """Test that strings are not treated as iterables to reduce."""
    data = {"text": "hello world", "length": 11}
    expected = {"text": "hello world", "length": 11}
    assert reduce_arrays(data) == expected


def test_bytes_not_affected():
    """Test that bytes are not treated as iterables to reduce."""
    data = {"binary": b"hello", "length": 5}
    expected = {"binary": b"hello", "length": 5}
    assert reduce_arrays(data) == expected


def test_json_loaded_data():
    """Test that reduce_arrays works with data loaded from a JSON string."""
    json_str = '{"numbers": [1, 2, 3, 4, 5], "info": {"tags": ["a", "b", "c"]}, "label": "test"}'
    data = json.loads(json_str)
    expected = {
        "numbers[size: 5]": [1, 2],
        "info": {"tags[size: 3]": ["a", "b"]},
        "label": "test",
    }
    assert reduce_arrays(data) == expected


def test_size_boundary_deep_nesting():
    """Test that size_boundary works correctly at deeper levels of nesting."""
    data = {
        "level1": {
            "level2": {
                "level3": {
                    "small_array": [1, 2],
                    "large_array": [10, 20, 30, 40, 50, 60],
                    "medium_array": [100, 200, 300, 400],
                },
                "other_data": "nested",
            },
            "direct_array": [5, 6, 7, 8, 9],
        },
        "root_array": [1000, 2000, 3000, 4000, 5000, 6000, 7000],
    }

    # Test with size_boundary = 4
    result = reduce_arrays(data, size_boundary=4)

    expected = {
        "level1": {
            "level2": {
                "level3": {
                    "small_array[size up to 4]": [1, 2],
                    "large_array[size over 4]": [10, 20],
                    "medium_array[size up to 4]": [100, 200],
                },
                "other_data": "nested",
            },
            "direct_array[size over 4]": [5, 6],
        },
        "root_array[size over 4]": [1000, 2000],
    }

    assert result == expected
