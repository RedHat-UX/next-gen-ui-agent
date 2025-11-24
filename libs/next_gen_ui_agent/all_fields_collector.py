import re

from next_gen_ui_agent.data_transform.data_transformer_utils import (
    generate_field_id,
    get_data_value_for_path,
    sanitize_data_path,
)
from next_gen_ui_agent.types import DataField, UIComponentMetadata

COMPONENTS_WITH_ALL_FIELDS = ["table", "set-of-cards"]
""" List of component names where `generate_all_fields()` function generates all possible fields to be shown in the UI."""


def generate_all_fields(
    component_metadata: UIComponentMetadata,
) -> list[DataField] | None:
    """
    Generate all possible fields to be shown in the UI for the component based on input data and fields currently selected to be shown.
    Currently, all fields are generated only for `table` and `set-of-cards` components. If component does not support all fields, return `None`.
    """

    if (
        component_metadata.component not in COMPONENTS_WITH_ALL_FIELDS
        or component_metadata.fields is None
        or len(component_metadata.fields) == 0
    ):
        return None

    # base path is the array of objects we visualize in the UI component, we have to take one of this objects and parse all its fields
    base_path = sanitize_data_path(
        component_metadata.fields[0].data_path.split("[*]")[0]
    )

    if not base_path:
        return None

    base_path += "[*]"

    aobj = get_data_value_for_path(base_path, component_metadata.json_data)
    if aobj is None or len(aobj) == 0:
        return None

    obj = aobj[0]
    if not isinstance(obj, dict):
        return None

    all_fields: list[DataField] = []
    all_field_names: list[str] = []

    collect_all_fields_from_input_data(all_fields, all_field_names, obj, base_path)

    return all_fields


def collect_all_fields_from_input_data(
    all_fields: list[DataField],
    all_field_names: list[str],
    data_object: dict,
    base_path: str,
    field_name_prefix: str | None = None,
):
    """
    Collect all viewable fields into `all_fields` list from input data object `data_object`.
    Fields are collected recursively, all fields with somple value, dict or list of simple values are collected, lists of objects are skipped.

    Args:
        all_fields: list of all fields to be collected
        all_field_names: list of all field names to avoid duplicit field names in recursive calls
        data_object: input data object to collect fields from
        base_path: base path to the data object used to generate `data_path` and `id` for the fields
        field_name_prefix: prefix to the field name if it is a nested object used to avoid duplicit field names in recursive calls
    """

    nested_objects: list[tuple[str, dict]] = []

    for key, value in data_object.items():
        # process nested objects later after all fileds are processed to avoid duplicit field names
        if isinstance(value, dict):
            nested_objects.append((key, value))
        else:
            # skip fields containing array of objects as we can't render them in the UI component
            if (
                isinstance(value, list)
                and len(value) > 0
                and isinstance(value[0], dict)
            ):
                continue

            field_id = generate_field_id(base_path + "." + key)

            field_name = generate_field_name(key)
            if field_name in all_field_names and field_name_prefix:
                field_name = field_name_prefix + " " + field_name

            all_fields.append(
                DataField(
                    id=field_id,
                    name=field_name,
                    data_path=base_path + "." + key,
                )
            )
            all_field_names.append(field_name)

    for nested_object in nested_objects:
        collect_all_fields_from_input_data(
            all_fields,
            all_field_names,
            nested_object[1],
            base_path + "." + nested_object[0],
            generate_field_name(nested_object[0]),
        )


def generate_field_name(key: str) -> str:
    """
    Generate a human readable name from a data object field key.

    Replaces `-` and `_` with spaces to get multiple words, splits camelCase
    into individual words, then converts every word to begin with uppercase
    letter and continue with lowercase letters.

    Examples:
        first_name -> First Name
        user-id -> User Id
        firstName -> First Name
    """
    # Split camelCase: insert space between lowercase/digit and uppercase letters
    # This handles cases like: firstName -> first Name, but preserves USER_ID
    key = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", key)

    # Replace - and _ with spaces
    words = key.replace("-", " ").replace("_", " ").split()

    # Convert each word to title case (first letter uppercase, rest lowercase)
    title_words = [word.capitalize() for word in words]

    # Join words with spaces
    return " ".join(title_words)
