import re
from typing import Optional

""" Tools to work with Input Data structure, used in input data transformations and json wrapping """


def sanitize_field_name(field_name: str | None) -> str | None:
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

    field_name = field_name.strip()

    # Replace invalid characters with underscores
    # Keep only alphanumeric characters, underscores, and hyphens
    sanitized = re.sub(r"[^a-zA-Z0-9_-]", "_", field_name)

    # Ensure it doesn't start with a number or hyphen
    if sanitized and (sanitized[0].isdigit() or sanitized[0] == "-"):
        sanitized = "field_" + sanitized

    return sanitized


def transform_value(value: Optional[str]) -> str | bool | int | float | None:
    """
    Transform a field string value to appropriate Python type.

    Transformations applied:
    1. Strip/trim whitespace from both ends
    2. Convert empty strings to None
    3. Convert "true"/"false" (case-insensitive) to boolean
    4. Convert numeric strings to int or float
    5. Return string as-is if no conversion applies

    Args:
        value: The string value from CSV to transform

    Returns:
        Transformed value (None, bool, int, float, or str)
    """
    # Strip whitespace
    if not value:
        return None

    trimmed = value.strip()

    # Empty after trimming
    if not trimmed:
        return None

    # Check for boolean values (case-insensitive)
    lower_value = trimmed.lower()
    if lower_value == "true":
        return True
    elif lower_value == "false":
        return False

    # Check if value ends with a digit before trying number conversion
    if not trimmed[-1].isdigit():
        return trimmed

    # Try to convert to number
    try:
        # Try integer first
        if "." not in trimmed and "e" not in lower_value and "E" not in trimmed:
            return int(trimmed)
        else:
            # Check if dot is not the last character
            if trimmed.endswith("."):
                return trimmed
            # Try float
            return float(trimmed)
    except ValueError:
        # Not a number, return as string
        return trimmed
