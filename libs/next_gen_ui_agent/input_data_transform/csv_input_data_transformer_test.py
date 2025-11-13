import json

from jsonpath_ng import parse  # type: ignore
from next_gen_ui_agent.input_data_transform.csv_input_data_transformer import (
    CsvCommaInputDataTransformer,
    CsvInputDataTransformer,
    CsvSemicolonInputDataTransformer,
    CsvTabInputDataTransformer,
)
from pydantic import BaseModel


class TestCsvInputDataTransformer:
    """Test cases for CSV input data transformer."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.transformer = CsvInputDataTransformer()

    def test_transform_basic_csv(self) -> None:
        """Test transforming basic CSV data with type conversion."""
        input_data = """name,age,city
John,30,New York
Jane,25,Boston"""

        result = self.transformer.transform(input_data)

        expected = [
            {"name": "John", "age": 30, "city": "New York"},  # age is int
            {"name": "Jane", "age": 25, "city": "Boston"},
        ]
        assert result == expected
        assert isinstance(result, list)
        assert len(result) == 2
        # Verify type conversion
        assert isinstance(result[0]["age"], int)
        assert isinstance(result[1]["age"], int)

    def test_transform_single_row(self) -> None:
        """Test transforming CSV with single data row."""
        input_data = """name,age,city
John,30,New York"""

        result = self.transformer.transform(input_data)

        expected = [{"name": "John", "age": 30, "city": "New York"}]  # age is int
        assert result == expected
        assert isinstance(result, list)
        assert len(result) == 1

    def test_transform_with_quotes(self) -> None:
        """Test transforming CSV with quoted values."""
        input_data = """name,age,description
John,30,"Lives in New York, NY"
Jane,25,"Works at Company, Inc."""

        result = self.transformer.transform(input_data)

        expected = [
            {
                "name": "John",
                "age": 30,
                "description": "Lives in New York, NY",
            },  # age is int
            {"name": "Jane", "age": 25, "description": "Works at Company, Inc."},
        ]
        assert result == expected

    def test_transform_with_empty_fields(self) -> None:
        """Test transforming CSV with empty fields."""
        input_data = """name,age,city
John,,New York
,25,Bost\"\"on"""

        result = self.transformer.transform(input_data)

        expected = [
            {"name": "John", "age": None, "city": "New York"},
            {"name": None, "age": 25, "city": 'Bost""on'},  # age is int
        ]
        assert result == expected

    def test_transform_with_special_characters(self) -> None:
        """Test transforming CSV with special characters in values."""
        input_data = """name,email,note
John Doe,john@example.com,"Hello, world!"
Jane Smith,jane@test.org,Test & verify"""

        result = self.transformer.transform(input_data)

        assert result[0]["name"] == "John Doe"
        assert result[0]["email"] == "john@example.com"
        assert result[0]["note"] == "Hello, world!"
        assert result[1]["note"] == "Test & verify"
        # Verify strings are preserved (no conversion)
        assert isinstance(result[0]["name"], str)
        assert isinstance(result[0]["email"], str)

    def test_transform_with_multiline_fields(self) -> None:
        """Test transforming CSV with multiline quoted fields."""
        input_data = """name,age,address
John,30,"123 Main St
New York, NY"
Jane,25,"456 Oak Ave
Boston, MA"""

        result = self.transformer.transform(input_data)

        assert result[0]["name"] == "John"
        assert "123 Main St\nNew York, NY" in result[0]["address"]
        assert result[1]["name"] == "Jane"
        assert "456 Oak Ave\nBoston, MA" in result[1]["address"]

    def test_transform_empty_csv_raises_error(self) -> None:
        """Test that empty CSV returns empty list."""
        input_data = ""

        assert self.transformer.transform(input_data) == []

    def test_transform_only_headers_raises_error(self) -> None:
        """Test that CSV with only headers returns empty list."""
        input_data = "name,age,city"

        assert self.transformer.transform(input_data) == []

    def test_transform_only_headers_with_newline_raises_error(self) -> None:
        """Test that CSV with only headers and newline returns empty list."""
        input_data = "name,age,city\n"

        assert self.transformer.transform(input_data) == []

    def test_transform_with_trailing_newlines(self) -> None:
        """Test transforming CSV with trailing newlines."""
        input_data = """name,age,city
John,30,New York
Jane,25,Boston

"""

        result = self.transformer.transform(input_data)

        expected = [
            {"name": "John", "age": 30, "city": "New York"},  # age is int
            {"name": "Jane", "age": 25, "city": "Boston"},
        ]
        assert result == expected
        assert len(result) == 2

    def test_transform_preserves_whitespace_in_unquoted_fields(self) -> None:
        """Test that whitespace in unquoted fields is now TRIMMED."""
        input_data = """name,age,city
John ,30, New York
Jane,25,Boston\t """

        result = self.transformer.transform(input_data)

        # Whitespace is now trimmed as part of value transformation
        assert result[0]["name"] == "John"  # Trimmed
        assert result[0]["age"] == 30  # Converted to int and trimmed
        assert result[0]["city"] == "New York"  # Trimmed
        assert result[1]["city"] == "Boston"  # Trimmed

    def test_transform_with_different_field_counts_uses_fieldnames(self) -> None:
        """Test CSV where rows have different number of fields."""
        # If a row has fewer fields, missing ones get None
        input_data = """name,age,city
John,30
Jane,25,Boston"""

        result = self.transformer.transform(input_data)

        assert result[0]["name"] == "John"
        assert result[0]["age"] == 30  # Now int
        assert result[0]["city"] is None
        assert result[1]["city"] == "Boston"

    def test_transform_custom_delimiter(self) -> None:
        """Test transforming CSV with custom delimiter."""
        transformer = CsvInputDataTransformer(delimiter="|")
        input_data = """name|age|city
John|30|New York
Jane|25|Boston"""

        result = transformer.transform(input_data)

        expected = [
            {"name": "John", "age": 30, "city": "New York"},  # age is int
            {"name": "Jane", "age": 25, "city": "Boston"},
        ]
        assert result == expected

    def test_transform_with_type_conversions(self) -> None:
        """Test CSV data with various types that should be converted."""
        input_data = """name,age,price,active,rating,description
Alice,25,99.99,true,4.5,Great product
Bob,30,149.50,false,3.8,Good item
Charlie,35,0.99,True,5.0,Excellent"""

        result = self.transformer.transform(input_data)

        # Verify first row types
        assert result[0]["name"] == "Alice"
        assert result[0]["age"] == 25
        assert isinstance(result[0]["age"], int)

        assert result[0]["price"] == 99.99
        assert isinstance(result[0]["price"], float)

        assert result[0]["active"] is True
        assert isinstance(result[0]["active"], bool)

        assert result[0]["rating"] == 4.5
        assert isinstance(result[0]["rating"], float)

        assert result[0]["description"] == "Great product"
        assert isinstance(result[0]["description"], str)

        # Verify second row
        assert result[1]["age"] == 30
        assert result[1]["price"] == 149.50
        assert result[1]["active"] is False

        # Verify third row with different boolean case
        assert result[2]["active"] is True

    def test_transform_with_whitespace_trimming(self) -> None:
        """Test that values with whitespace are trimmed."""
        input_data = """name,age,city
  John  , 30 ,  New York
Jane,  25,Boston  """

        result = self.transformer.transform(input_data)

        # All values should be trimmed
        assert result[0]["name"] == "John"
        assert result[0]["age"] == 30  # Also converted to int
        assert result[0]["city"] == "New York"
        assert result[1]["name"] == "Jane"
        assert result[1]["age"] == 25
        assert result[1]["city"] == "Boston"

    def test_field_name_sanitization(self) -> None:
        """Test that CSV headers are sanitized to valid field names."""
        input_data = """First Name,user@email,Price ($),Rating %,user.id,1st Place,2nd_Place,-start
Alice,alice@test.com,99.99,4.5,123,Gold,Silver,Negative
Bob,bob@test.com,149.99,5.0,456,Silver,Bronze,Positive"""

        result = self.transformer.transform(input_data)

        # Verify sanitized field names
        assert len(result) == 2

        # Spaces replaced with underscores
        assert "First_Name" in result[0]
        assert result[0]["First_Name"] == "Alice"

        # Special characters replaced with underscores
        assert "user_email" in result[0]
        assert "Price____" in result[0]
        assert "Rating__" in result[0]
        assert "user_id" in result[0]

        # Fields starting with numbers get "field_" prefix
        assert "field_1st_Place" in result[0]
        assert result[0]["field_1st_Place"] == "Gold"

        # Underscores are preserved
        assert "field_2nd_Place" in result[0]  # Still gets prefix due to number

        # Fields starting with hyphen get "field_" prefix
        assert "field_-start" in result[0]
        assert result[0]["field_-start"] == "Negative"

        # Hyphens in the middle are preserved
        # (Note: in our case, all are preserved, they're valid in field names)

        # Verify values are preserved correctly (with type conversion)
        assert result[1]["First_Name"] == "Bob"
        assert result[1]["user_email"] == "bob@test.com"
        assert result[1]["Price____"] == 149.99  # Converted to float
        assert result[1]["Rating__"] == 5.0  # Converted to float
        assert result[1]["user_id"] == 456  # Converted to int

    def test_transform_output_serializable_with_pydantic(self) -> None:
        """Test that transformer output can be serialized using Pydantic model_dump_json()."""

        # Create a simple Pydantic model for testing arrays
        class TestArrayModel(BaseModel):
            items: list

        # Test with CSV data (which is always array-like)
        input_data = """id,name,age
1,Alice,25
2,Bob,30"""
        result = self.transformer.transform(input_data)

        # Create a Pydantic model instance with the transformed data
        model = TestArrayModel(items=result)

        # Verify that model_dump_json() works without errors
        json_output = model.model_dump_json()
        assert isinstance(json_output, str)

        # Verify the JSON can be parsed back
        parsed_back = json.loads(json_output)
        assert "items" in parsed_back
        assert parsed_back["items"] == result

    def test_transform_output_accessible_with_jsonpath_ng_array(self) -> None:
        """Test that transformer output can be accessed using jsonpath_ng with dot notation."""
        # Test with CSV array of objects (using simple field names for dot notation)
        input_data = """id,name,city,age
1,Alice,New York,25
2,Bob,Boston,30
3,Charlie,Chicago,35"""

        result = self.transformer.transform(input_data)

        # Test various jsonpath expressions for array data using dot notation
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
        assert first_item_matches[0]["id"] == 1  # Now int, not string

        # Access all names using dot notation
        all_names_path = parse("$[*].name")
        all_names_matches = [match.value for match in all_names_path.find(result)]
        assert len(all_names_matches) == 3
        assert "Alice" in all_names_matches
        assert "Bob" in all_names_matches
        assert "Charlie" in all_names_matches

        # Access all cities using dot notation
        all_cities_path = parse("$[*].city")
        all_cities_matches = [match.value for match in all_cities_path.find(result)]
        assert len(all_cities_matches) == 3
        assert "New York" in all_cities_matches
        assert "Boston" in all_cities_matches
        assert "Chicago" in all_cities_matches

        # Access specific field by nested index using dot notation
        alice_age_path = parse("$[0].age")
        alice_age_matches = [match.value for match in alice_age_path.find(result)]
        assert len(alice_age_matches) == 1
        assert alice_age_matches[0] == 25  # Now int, not string

        # Access second person's name using dot notation
        bob_name_path = parse("$[1].name")
        bob_name_matches = [match.value for match in bob_name_path.find(result)]
        assert len(bob_name_matches) == 1
        assert bob_name_matches[0] == "Bob"

        # Access all IDs using dot notation
        all_ids_path = parse("$[*].id")
        all_ids = [match.value for match in all_ids_path.find(result)]
        assert len(all_ids) == 3
        assert 1 in all_ids  # Now int
        assert 2 in all_ids
        assert 3 in all_ids

    def test_transform_output_accessible_with_jsonpath_ng_filtering(self) -> None:
        """Test that transformer output supports jsonpath_ng dot notation for filtering."""
        # Test with CSV data using simple field names for dot notation
        input_data = """name,department,salary,active
Alice,Engineering,75000,true
Bob,Marketing,65000,true
Charlie,Engineering,80000,false
Diana,Sales,70000,true"""

        result = self.transformer.transform(input_data)

        # Access all departments using dot notation
        dept_path = parse("$[*].department")
        dept_matches = [match.value for match in dept_path.find(result)]
        assert len(dept_matches) == 4
        assert dept_matches.count("Engineering") == 2

        # Access specific records by index using dot notation
        second_record_path = parse("$[1]")
        second_record_matches = [
            match.value for match in second_record_path.find(result)
        ]
        assert len(second_record_matches) == 1
        assert second_record_matches[0]["name"] == "Bob"
        assert second_record_matches[0]["department"] == "Marketing"

        # Access all names using dot notation
        names_path = parse("$[*].name")
        names_matches = [match.value for match in names_path.find(result)]
        assert "Alice" in names_matches
        assert "Bob" in names_matches
        assert "Charlie" in names_matches
        assert "Diana" in names_matches

        # Access all salaries using dot notation
        salaries_path = parse("$[*].salary")
        salaries = [match.value for match in salaries_path.find(result)]
        assert 75000 in salaries  # Now int
        assert 80000 in salaries

        # Access active status using dot notation
        active_path = parse("$[*].active")
        active_values = [match.value for match in active_path.find(result)]
        assert True in active_values  # Now boolean
        assert False in active_values

        # Access first person's department using dot notation
        first_dept_path = parse("$[0].department")
        first_dept = [match.value for match in first_dept_path.find(result)]
        assert first_dept[0] == "Engineering"

    def test_transform_output_with_none_values_serializable(self) -> None:
        """Test that transformer output with None values can be serialized with Pydantic."""

        class TestModel(BaseModel):
            data: list

        # CSV with missing values (will be None)
        input_data = """name,age,city
John,30,
,25,Boston"""

        result = self.transformer.transform(input_data)

        # Verify None values are present
        assert result[0]["city"] is None
        assert result[1]["name"] is None

        # Create Pydantic model
        model = TestModel(data=result)

        # Verify serialization works
        json_output = model.model_dump_json()
        assert isinstance(json_output, str)

        # Verify deserialization
        parsed = json.loads(json_output)
        assert parsed["data"][0]["city"] is None
        assert parsed["data"][1]["name"] is None

    def test_transform_output_jsonpath_with_none_values(self) -> None:
        """Test that jsonpath_ng can access data with None values."""
        input_data = """name,age,city
John,,New York
Jane,25,"""

        result = self.transformer.transform(input_data)

        # Access all records
        all_records_path = parse("$[*]")
        all_records = [match.value for match in all_records_path.find(result)]
        assert len(all_records) == 2

        # Access specific fields with None
        all_ages_path = parse("$[*].age")
        all_ages = [match.value for match in all_ages_path.find(result)]
        assert None in all_ages
        assert 25 in all_ages  # Now int

        all_cities_path = parse("$[*].city")
        all_cities = [match.value for match in all_cities_path.find(result)]
        assert "New York" in all_cities
        assert None in all_cities

    def test_transform_with_special_chars_in_headers_pydantic(self) -> None:
        """Test CSV with special characters in headers are sanitized for Pydantic."""

        class TestModel(BaseModel):
            data: list

        # CSV with problematic header names (not valid Python identifiers)
        # These will be sanitized: spaces->_, special chars->_, etc.
        input_data = """First Name,Last-Name,Email@Address,Price ($),Rating %,user.id
John,Doe,john@example.com,99.99,4.5,123
Jane,Smith,jane@example.com,149.99,5.0,456"""

        result = self.transformer.transform(input_data)

        # Verify the data structure with sanitized keys
        assert len(result) == 2
        assert "First_Name" in result[0]  # Space replaced with underscore
        assert "Last-Name" in result[0]  # Hyphen preserved
        assert "Email_Address" in result[0]  # @ replaced with underscore
        assert "Price____" in result[0]  # Special chars replaced with underscores
        assert "Rating__" in result[0]  # % replaced with underscore
        assert "user_id" in result[0]  # Dot replaced with underscore

        # Verify values
        assert result[0]["First_Name"] == "John"
        assert result[0]["Email_Address"] == "john@example.com"
        assert result[0]["Price____"] == 99.99

        # Test Pydantic serialization
        model = TestModel(data=result)
        json_output = model.model_dump_json()
        assert isinstance(json_output, str)

        # Verify JSON round-trip with sanitized keys
        parsed = json.loads(json_output)
        assert "First_Name" in parsed["data"][0]
        assert "Last-Name" in parsed["data"][0]
        assert "Email_Address" in parsed["data"][0]
        assert parsed["data"][0]["First_Name"] == "John"
        assert parsed["data"][1]["First_Name"] == "Jane"

    def test_transform_with_special_chars_in_headers_jsonpath(self) -> None:
        """Test CSV with special characters in headers are sanitized for jsonpath_ng dot notation."""
        input_data = """User Name,Birth-Date,Contact@Email,Salary ($)
Alice Smith,1990-01-15,alice@test.com,75000
Bob Jones,1985-06-20,bob@test.com,85000
Charlie Brown,1992-03-10,charlie@test.com,65000"""

        result = self.transformer.transform(input_data)

        # Verify basic structure with sanitized field names
        assert len(result) == 3
        assert "User_Name" in result[0]  # Space replaced with underscore
        assert "Birth-Date" in result[0]  # Hyphen preserved
        assert "Contact_Email" in result[0]  # @ replaced with underscore
        assert "Salary____" in result[0]  # Special chars replaced with underscores

        # Test jsonpath_ng access - root level
        root_path = parse("$")
        root_matches = [match.value for match in root_path.find(result)]
        assert len(root_matches) == 1
        assert root_matches[0] == result

        # Access all items
        all_items_path = parse("$[*]")
        all_items = [match.value for match in all_items_path.find(result)]
        assert len(all_items) == 3

        # Access specific item
        first_item_path = parse("$[0]")
        first_item = [match.value for match in first_item_path.find(result)]
        assert len(first_item) == 1
        assert first_item[0]["User_Name"] == "Alice Smith"

        # Now we can use dot notation! Sanitized field names are valid identifiers
        user_names_path = parse("$[*].User_Name")
        user_names = [match.value for match in user_names_path.find(result)]
        assert len(user_names) == 3
        assert "Alice Smith" in user_names
        assert "Bob Jones" in user_names
        assert "Charlie Brown" in user_names

        # Access email field using dot notation (@ was sanitized to _)
        emails_path = parse("$[*].Contact_Email")
        emails = [match.value for match in emails_path.find(result)]
        assert "alice@test.com" in emails
        assert "bob@test.com" in emails
        assert "charlie@test.com" in emails

        # Access field with hyphen using bracket notation (hyphens preserved but need brackets)
        dates_path = parse("$[*]['Birth-Date']")
        dates = [match.value for match in dates_path.find(result)]
        assert "1990-01-15" in dates
        assert "1985-06-20" in dates

        # Access field with sanitized special chars using dot notation
        salaries_path = parse("$[*].Salary____")
        salaries = [match.value for match in salaries_path.find(result)]
        assert 75000 in salaries  # Now int
        assert 85000 in salaries
        assert 65000 in salaries

    def test_transform_with_numeric_and_reserved_headers(self) -> None:
        """Test CSV with numeric starts and Python reserved words are sanitized."""

        class TestModel(BaseModel):
            records: list

        # Headers with numbers and reserved words - will be sanitized
        input_data = """1st Place,2nd Place,class,def,return,for
Alice,Bob,A,B,C,D
Charlie,Diana,E,F,G,H"""

        result = self.transformer.transform(input_data)

        # Verify structure with sanitized headers
        assert len(result) == 2
        # Numbers at start get "field_" prefix, spaces become underscores
        assert "field_1st_Place" in result[0]
        assert "field_2nd_Place" in result[0]
        # Reserved words are just strings in dict, no sanitization needed
        assert "class" in result[0]
        assert "def" in result[0]
        assert "return" in result[0]
        assert "for" in result[0]

        # Verify values
        assert result[0]["field_1st_Place"] == "Alice"
        assert result[0]["class"] == "A"
        assert result[0]["def"] == "B"
        assert result[1]["return"] == "G"

        # Test Pydantic serialization works
        model = TestModel(records=result)
        json_output = model.model_dump_json()
        parsed = json.loads(json_output)

        # Verify sanitized and reserved words work in JSON
        assert parsed["records"][0]["field_1st_Place"] == "Alice"
        assert parsed["records"][0]["class"] == "A"
        assert parsed["records"][0]["def"] == "B"
        assert parsed["records"][0]["return"] == "C"

        # Test jsonpath_ng access with dot notation for sanitized fields
        first_place_path = parse("$[*].field_1st_Place")
        first_places = [match.value for match in first_place_path.find(result)]
        assert "Alice" in first_places
        assert "Charlie" in first_places

        # Access reserved word fields using dot notation (they're valid dict keys)
        class_path = parse("$[*].class")
        classes = [match.value for match in class_path.find(result)]
        assert "A" in classes
        assert "E" in classes

        # Access other fields using dot notation
        def_path = parse("$[*].def")
        defs = [match.value for match in def_path.find(result)]
        assert "B" in defs
        assert "F" in defs


class TestCsvCommaInputDataTransformer:
    """Test cases for CSV comma delimiter transformer."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.transformer = CsvCommaInputDataTransformer()

    def test_transformer_name(self) -> None:
        """Test that transformer has correct name."""
        assert self.transformer.TRANSFORMER_NAME == "csv-comma"

    def test_transform_basic_csv(self) -> None:
        """Test transforming basic CSV data with comma delimiter."""
        input_data = """name,age,city
John,30,New York
Jane,25,Boston"""

        result = self.transformer.transform(input_data)

        expected = [
            {"name": "John", "age": 30, "city": "New York"},
            {"name": "Jane", "age": 25, "city": "Boston"},
        ]
        assert result == expected
        assert isinstance(result, list)
        assert len(result) == 2

    def test_transform_output_serializable_with_pydantic(self) -> None:
        """Test that comma transformer output is serializable with Pydantic."""

        class TestModel(BaseModel):
            records: list

        input_data = """id,name,score
1,Alice,95
2,Bob,87"""
        result = self.transformer.transform(input_data)

        model = TestModel(records=result)
        json_output = model.model_dump_json()
        assert isinstance(json_output, str)

        parsed = json.loads(json_output)
        assert len(parsed["records"]) == 2
        assert parsed["records"][0]["name"] == "Alice"

    def test_transform_output_accessible_with_jsonpath_ng(self) -> None:
        """Test that comma transformer output works with jsonpath_ng dot notation."""
        input_data = """id,name,email
1,Alice,alice@example.com
2,Bob,bob@example.com"""
        result = self.transformer.transform(input_data)

        # Access all emails using dot notation
        emails_path = parse("$[*].email")
        emails = [match.value for match in emails_path.find(result)]
        assert "alice@example.com" in emails
        assert "bob@example.com" in emails

        # Access all names using dot notation
        names_path = parse("$[*].name")
        names = [match.value for match in names_path.find(result)]
        assert "Alice" in names
        assert "Bob" in names

        # Access specific field using dot notation
        first_email_path = parse("$[0].email")
        first_email = [match.value for match in first_email_path.find(result)]
        assert first_email[0] == "alice@example.com"


class TestCsvSemicolonInputDataTransformer:
    """Test cases for CSV semicolon delimiter transformer."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.transformer = CsvSemicolonInputDataTransformer()

    def test_transformer_name(self) -> None:
        """Test that transformer has correct name."""
        assert self.transformer.TRANSFORMER_NAME == "csv-semicolon"

    def test_transform_basic_csv(self) -> None:
        """Test transforming basic CSV data with semicolon delimiter."""
        input_data = """name;age;city
John;30;New York
Jane;25;Boston"""

        result = self.transformer.transform(input_data)

        expected = [
            {"name": "John", "age": 30, "city": "New York"},
            {"name": "Jane", "age": 25, "city": "Boston"},
        ]
        assert result == expected
        assert isinstance(result, list)
        assert len(result) == 2

    def test_transform_with_commas_in_data(self) -> None:
        """Test that commas in data are not treated as delimiters."""
        input_data = """name;age;description
John;30;Lives in New York, NY
Jane;25;Works at Company, Inc."""

        result = self.transformer.transform(input_data)

        # Commas should be preserved in data since semicolon is the delimiter
        assert result[0]["description"] == "Lives in New York, NY"
        assert result[1]["description"] == "Works at Company, Inc."

    def test_transform_output_serializable_with_pydantic(self) -> None:
        """Test that semicolon transformer output is serializable with Pydantic."""

        class TestModel(BaseModel):
            data: list

        input_data = """name;country;population
France;Paris;2200000
Germany;Berlin;3700000"""
        result = self.transformer.transform(input_data)

        model = TestModel(data=result)
        json_output = model.model_dump_json()
        assert isinstance(json_output, str)

        parsed = json.loads(json_output)
        assert len(parsed["data"]) == 2
        assert parsed["data"][0]["country"] == "Paris"

    def test_transform_output_accessible_with_jsonpath_ng(self) -> None:
        """Test that semicolon transformer output works with jsonpath_ng dot notation."""
        input_data = """product;price;category
Laptop;1200;Electronics
Mouse;25;Electronics
Desk;350;Furniture"""
        result = self.transformer.transform(input_data)

        # Access all categories using dot notation
        categories_path = parse("$[*].category")
        categories = [match.value for match in categories_path.find(result)]
        assert categories.count("Electronics") == 2
        assert "Furniture" in categories

        # Access specific product using dot notation
        first_product_path = parse("$[0].product")
        first_product = [match.value for match in first_product_path.find(result)]
        assert first_product[0] == "Laptop"

        # Access all prices using dot notation
        prices_path = parse("$[*].price")
        prices = [match.value for match in prices_path.find(result)]
        assert 1200 in prices
        assert 25 in prices
        assert 350 in prices

        # Access all products using dot notation
        products_path = parse("$[*].product")
        products = [match.value for match in products_path.find(result)]
        assert "Laptop" in products
        assert "Mouse" in products
        assert "Desk" in products


class TestCsvTabInputDataTransformer:
    """Test cases for CSV tab delimiter transformer."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.transformer = CsvTabInputDataTransformer()

    def test_transformer_name(self) -> None:
        """Test that transformer has correct name."""
        assert self.transformer.TRANSFORMER_NAME == "csv-tab"

    def test_transform_basic_tsv(self) -> None:
        """Test transforming basic TSV (tab-separated values) data."""
        input_data = """name\tage\tcity
John\t30\tNew York
Jane\t25\tBoston"""

        result = self.transformer.transform(input_data)

        expected = [
            {"name": "John", "age": 30, "city": "New York"},
            {"name": "Jane", "age": 25, "city": "Boston"},
        ]
        assert result == expected
        assert isinstance(result, list)
        assert len(result) == 2

    def test_transform_with_spaces_in_data(self) -> None:
        """Test that spaces in data are preserved."""
        input_data = """name\tage\tdescription
John Doe\t30\tSenior Developer at Company
Jane Smith\t25\tJunior Developer"""

        result = self.transformer.transform(input_data)

        # Spaces should be preserved in data since tab is the delimiter
        assert result[0]["name"] == "John Doe"
        assert result[0]["description"] == "Senior Developer at Company"
        assert result[1]["name"] == "Jane Smith"

    def test_transform_output_serializable_with_pydantic(self) -> None:
        """Test that tab transformer output is serializable with Pydantic."""

        class TestModel(BaseModel):
            entries: list

        input_data = """title\tauthor\tyear
Book One\tAuthor A\t2020
Book Two\tAuthor B\t2021"""
        result = self.transformer.transform(input_data)

        model = TestModel(entries=result)
        json_output = model.model_dump_json()
        assert isinstance(json_output, str)

        parsed = json.loads(json_output)
        assert len(parsed["entries"]) == 2
        assert parsed["entries"][0]["title"] == "Book One"

    def test_transform_output_accessible_with_jsonpath_ng(self) -> None:
        """Test that tab transformer output works with jsonpath_ng dot notation."""
        input_data = """code\tname\tvalue
A01\tItem Alpha\t100
B02\tItem Beta\t200
C03\tItem Gamma\t150"""
        result = self.transformer.transform(input_data)

        # Access all codes using dot notation
        codes_path = parse("$[*].code")
        codes = [match.value for match in codes_path.find(result)]
        assert len(codes) == 3
        assert "A01" in codes
        assert "B02" in codes
        assert "C03" in codes

        # Access specific item name using dot notation
        second_name_path = parse("$[1].name")
        second_name = [match.value for match in second_name_path.find(result)]
        assert second_name[0] == "Item Beta"

        # Access all values using dot notation
        values_path = parse("$[*].value")
        values = [match.value for match in values_path.find(result)]
        assert 100 in values
        assert 200 in values
        assert 150 in values

        # Access all names using dot notation
        names_path = parse("$[*].name")
        names = [match.value for match in names_path.find(result)]
        assert "Item Alpha" in names
        assert "Item Beta" in names
        assert "Item Gamma" in names

        # Access first item code using dot notation
        first_code_path = parse("$[0].code")
        first_code = [match.value for match in first_code_path.find(result)]
        assert first_code[0] == "A01"

        # Access third item value using dot notation
        third_value_path = parse("$[2].value")
        third_value = [match.value for match in third_value_path.find(result)]
        assert third_value[0] == 150
