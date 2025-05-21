from urllib.parse import urlparse

from next_gen_ui_agent.data_transform.validation.types import (
    ComponentDataValidationError,
)


def is_url_http(url: str) -> bool:
    """Validate that the URL string is valid and is http/s"""

    if url:
        parsed = urlparse(url)
        if (
            parsed.scheme
            and parsed.hostname
            and (parsed.scheme.lower() in ["http", "https"])
        ):
            return True
    return False


def assert_array_not_empty(
    value_object,
    value_name: str,
    error_code: str,
    errors: list[ComponentDataValidationError],
    err_msg=None,
):
    """Assert that array value expected under `value_name` in the `value_object` is not empty, add `error_code` into `errors` if it is empty and return `False`"""
    try:
        if isinstance(value_object, dict):
            value = value_object[value_name]
        else:
            value = getattr(value_object, value_name)

        if not value or value is None or len(value) == 0:
            errors.append(
                ComponentDataValidationError(
                    error_code, err_msg if err_msg else f"array is '{value}'"
                )
            )
            return False
        else:
            return True
    except KeyError:
        errors.append(
            ComponentDataValidationError(
                error_code, err_msg if err_msg else "array is missing"
            )
        )
        return False


def assert_str_not_blank(
    value_object,
    value_name: str,
    error_code: str,
    errors: list[ComponentDataValidationError],
    err_msg=None,
):
    """Assert that string value expected under `value_name` in the `value_object` is not a blank string, add `error_code` into `errors` if it is blank and return `False`"""
    try:
        if isinstance(value_object, dict):
            value = value_object[value_name]
        else:
            value = getattr(value_object, value_name)

        if not value or value is None or len(value.strip()) == 0:
            errors.append(
                ComponentDataValidationError(
                    error_code, err_msg if err_msg else f"string value is '{value}'"
                )
            )
            return False
        else:
            return True
    except KeyError:
        errors.append(
            ComponentDataValidationError(
                error_code, err_msg if err_msg else "string is missing"
            )
        )
        return False
