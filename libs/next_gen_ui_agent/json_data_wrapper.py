import re
from typing import Any, Iterable


def _sanitize_field_name(field_name: str | None) -> str | None:
    """
    Sanitize a field name to be a valid JSON object key by replacing invalid characters with underscores.
    If `field_name` is `None` or empty string, `None` is returned.
    If `field_name` starts with a number or hyphen, `field_` is prepended to the field name.

    Args:
        field_name: The field name to sanitize

    Returns:
        A sanitized field name that is valid for use as a JSON object key
    """
    if not field_name or field_name.strip() == "":
        return None

    # Replace invalid characters with underscores
    # Keep only alphanumeric characters, underscores, and hyphens
    sanitized = re.sub(r"[^a-zA-Z0-9_-]", "_", field_name)

    # Ensure it doesn't start with a number or hyphen
    if sanitized and (sanitized[0].isdigit() or sanitized[0] == "-"):
        sanitized = "field_" + sanitized

    return sanitized


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
    field_name = _sanitize_field_name(data_type)

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
