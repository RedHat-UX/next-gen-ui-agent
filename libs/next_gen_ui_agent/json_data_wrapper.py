from typing import Any, Iterable, Optional

from next_gen_ui_agent.data_structure_tools import sanitize_field_name


def wrap_json_data(data: Any, data_type: str | None) -> Any:
    """
    Wrap data into a dictionary with a single field if the data is a dict with multiple fields or an array.

    Args:
        data: Input parsed JSON data
        data_type: Name of the field to use when wrapping the data (will be sanitized), if `None` or empty string, data is returned unchanged

    Returns:
        If data is a dict with more than one field, wraps it in another dict with one field named `data_type`.
        If data is an array, wraps it in a dict with one field named `data_type`.
        Otherwise, returns the data unchanged. Data are also unchanged if `data_type` is `None` or empty string.
        Sanitized `data_type` is used as a name of the field in the wrapped data.
    """

    # Sanitize the data_type to ensure it's a valid field name
    field_name = sanitize_field_name(data_type)

    # If data_type is `None` or empty string, return data unchanged
    if not field_name:
        return data

    if isinstance(data, dict) and len(data) > 1:
        # Check if data is a dict with more than one field
        return {field_name: data}
    elif isinstance(data, Iterable) and not isinstance(
        data, (str, bytes, bytearray, dict)
    ):
        # Check if data is an array (iterable not a string, bytes, bytearray, or dict)
        return {field_name: data}

    # Return data unchanged for all other cases
    return data


def wrap_string_as_json(
    data: str, data_type: Optional[str], max_length: Optional[int] = None
) -> Any:
    """
    Wrap string data into a dictionary with a single field.
    If `data_type` is `None` or empty string, `data` is used as a field name.
    If `max_length` is provided and `data` is longer than `max_length`, the data is truncated and "..." is added to the end.
    """
    field_name = sanitize_field_name(data_type)
    if not field_name:
        field_name = "data"
    if max_length and len(data) > max_length:
        data = data[:max_length] + "..."
    return {field_name: data}
