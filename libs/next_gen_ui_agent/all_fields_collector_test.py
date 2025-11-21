from next_gen_ui_agent.all_fields_collector import (
    generate_all_fields,
    generate_field_name,
)
from next_gen_ui_agent.data_transform.data_transformer_utils import generate_field_id
from next_gen_ui_agent.types import DataField, UIComponentMetadata


def test_generate_all_fields_returns_none_for_unsupported_component():
    """Test that generate_all_fields returns None for components not in COMPONENTS_WITH_ALL_FIELDS."""
    component_metadata = UIComponentMetadata(
        component="unsupported_component",
        title="Test",
        fields=[
            DataField(
                id="field1",
                name="Field 1",
                data_path="items[*].name",
            )
        ],
        json_data={"items": [{"name": "test"}]},
    )

    result = generate_all_fields(component_metadata)
    assert result is None


def test_generate_all_fields_returns_none_when_fields_is_empty():
    """Test that generate_all_fields returns None when fields list is empty."""
    component_metadata = UIComponentMetadata(
        component="table",
        title="Test",
        fields=[],
        json_data={"items": [{"name": "test"}]},
    )

    result = generate_all_fields(component_metadata)
    assert result is None


def test_generate_all_fields_table_component_simple_fields():
    """Test that generate_all_fields correctly extracts all fields from a table component with simple fields."""
    component_metadata = UIComponentMetadata(
        component="table",
        title="Test Table",
        fields=[
            DataField(
                id="items-name",
                name="Name",
                data_path="items[*].name",
            )
        ],
        json_data={
            "items": [
                {"name": "John", "age": 30, "city": "New York"},
                {"name": "Jane", "age": 25, "city": "Boston"},
            ]
        },
    )

    result = generate_all_fields(component_metadata)

    assert result is not None
    assert len(result) == 3

    # Check that all fields are present with human-readable names
    field_names = {field.name for field in result}
    assert field_names == {"Name", "Age", "City"}

    # Check data paths - must be sanitized even they was not sanitized in the UIComponentMetadata
    field_paths = {field.data_path for field in result}
    assert "$..items[*].name" in field_paths
    assert "$..items[*].age" in field_paths
    assert "$..items[*].city" in field_paths

    # Check field IDs are correctly generated from sanitized data paths
    for field in result:
        assert isinstance(field, DataField)
        assert field.id is not None
        assert field.id == generate_field_id(field.data_path)


def test_generate_all_fields_set_of_cards_component():
    """Test that generate_all_fields correctly extracts all fields from a set-of-cards component."""
    component_metadata = UIComponentMetadata(
        component="set-of-cards",
        title="Test Cards",
        fields=[
            DataField(
                id="field1",
                name="Title",
                data_path="products[*].title",
            )
        ],
        json_data={
            "products": [
                {"title": "Product 1", "price": 100, "description": "Desc 1"},
                {"title": "Product 2", "price": 200, "description": "Desc 2"},
            ]
        },
    )

    result = generate_all_fields(component_metadata)

    assert result is not None
    assert len(result) == 3

    field_names = {field.name for field in result}
    assert field_names == {"Title", "Price", "Description"}


def test_generate_all_fields_with_nested_objects():
    """Test that generate_all_fields correctly handles nested objects and ignores fields containing arrays of objects."""
    component_metadata = UIComponentMetadata(
        component="table",
        title="Test Table",
        fields=[
            DataField(
                id="field1",
                name="Name",
                data_path="users[*].name",
            )
        ],
        json_data={
            "users": [
                {
                    "name": "John",
                    "address": {"street": "123 Main St", "zip": "12345"},
                    "age": 30,
                    "user_type": ["admin", "user"],
                    "ignored": [{}],
                },
                {
                    "name": "Jane",
                    "address": {"street": "456 Oak Ave", "zip": "67890"},
                    "age": 25,
                    "user_type": [],
                    "ignored": [{}],
                },
            ]
        },
    )

    result = generate_all_fields(component_metadata)

    assert result is not None
    # Should have: name, age, address.street, address.zip, user_type
    assert len(result) == 5

    field_names = {field.name for field in result}
    assert "Name" in field_names
    assert "Age" in field_names
    assert "Street" in field_names
    assert "Zip" in field_names
    assert "User Type" in field_names

    # Check nested paths
    field_paths = {field.data_path for field in result}
    assert "$..users[*].name" in field_paths
    assert "$..users[*].age" in field_paths
    assert "$..users[*].address.street" in field_paths
    assert "$..users[*].address.zip" in field_paths
    assert "$..users[*].user_type" in field_paths


def test_generate_all_fields_with_deeply_nested_objects():
    """Test that generate_all_fields correctly handles deeply nested objects."""
    component_metadata = UIComponentMetadata(
        component="table",
        title="Test Table",
        fields=[
            DataField(
                id="field1",
                name="Name",
                data_path="data[*].name",
            )
        ],
        json_data={
            "data": [
                {
                    "name": "Item 1",
                    "metadata": {
                        "author": {
                            "first": "John",
                            "last": "Doe",
                        },
                        "date": "2024-01-01",
                    },
                }
            ]
        },
    )

    result = generate_all_fields(component_metadata)

    assert result is not None
    # Should have: name, metadata.author.first, metadata.author.last, metadata.date
    assert len(result) == 4

    field_names = {field.name for field in result}
    assert "Name" in field_names
    assert "First" in field_names
    assert "Last" in field_names
    assert "Date" in field_names


def test_generate_all_fields_with_empty_array():
    """Test that generate_all_fields handles empty array in json_data  - this should never happen but just to be sure it works as expected."""
    component_metadata = UIComponentMetadata(
        component="table",
        title="Test Table",
        fields=[
            DataField(
                id="field1",
                name="Name",
                data_path="items[*].name",
            )
        ],
        json_data={"items": []},
    )

    result = generate_all_fields(component_metadata)
    assert result is None


def test_generate_all_fields_with_missing_data_path():
    """Test that generate_all_fields handles missing data in json_data gracefully."""
    component_metadata = UIComponentMetadata(
        component="table",
        title="Test Table",
        fields=[
            DataField(
                id="field1",
                name="Name",
                data_path="items[*].name",
            )
        ],
        json_data={"other_data": [{"value": "test"}]},
    )

    result = generate_all_fields(component_metadata)

    assert result is None


def test_generate_all_fields_with_non_dict_array_items():
    """Test that generate_all_fields handles array items that are not dictionaries."""
    component_metadata = UIComponentMetadata(
        component="table",
        title="Test Table",
        fields=[
            DataField(
                id="field1",
                name="Name",
                data_path="items[*].name",
            )
        ],
        json_data={"items": ["string1", "string2", 123]},
    )

    result = generate_all_fields(component_metadata)

    assert result is None


def test_generate_field_name_with_underscore():
    """Test that generate_field_name converts underscore-separated words to title case."""
    assert generate_field_name("first_name") == "First Name"
    assert generate_field_name("user_id") == "User Id"
    assert generate_field_name("first_name_last_name") == "First Name Last Name"


def test_generate_field_name_with_hyphen():
    """Test that generate_field_name converts hyphen-separated words to title case."""
    assert generate_field_name("user-id") == "User Id"
    assert generate_field_name("first-name") == "First Name"
    assert generate_field_name("first-name-last-name") == "First Name Last Name"


def test_generate_field_name_with_mixed_separators():
    """Test that generate_field_name handles mixed underscore and hyphen separators."""
    assert generate_field_name("user_id-name") == "User Id Name"
    assert generate_field_name("first-name_last") == "First Name Last"


def test_generate_field_name_single_word():
    """Test that generate_field_name handles single words."""
    assert generate_field_name("name") == "Name"
    assert generate_field_name("age") == "Age"
    assert generate_field_name("title") == "Title"


def test_generate_field_name_already_title_case():
    """Test that generate_field_name handles already title-cased words."""
    assert generate_field_name("FirstName") == "Firstname"
    assert generate_field_name("UserID") == "Userid"


def test_generate_field_name_with_multiple_spaces():
    """Test that generate_field_name handles multiple consecutive separators."""
    assert generate_field_name("first__name") == "First Name"
    assert generate_field_name("first--name") == "First Name"
    assert generate_field_name("first_-name") == "First Name"


def test_generate_field_name_empty_string():
    """Test that generate_field_name handles empty string."""
    assert generate_field_name("") == ""


def test_generate_field_name_uppercase():
    """Test that generate_field_name converts uppercase to title case."""
    assert generate_field_name("FIRST_NAME") == "First Name"
    assert generate_field_name("USER_ID") == "User Id"
