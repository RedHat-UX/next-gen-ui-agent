from next_gen_ui_agent.data_structure_tools import sanitize_field_name, transform_value


class TestTransformValue:
    """Test the _transform_value method independently."""

    def test_transform_value_method_none_empty_blank_string(self) -> None:
        # Test None/empty/blank conversions
        assert transform_value(None) is None
        assert transform_value("") is None
        assert transform_value("\n") is None
        assert transform_value("\r") is None
        assert transform_value("   ") is None
        assert transform_value("  \t ") is None
        assert transform_value("  \n ") is None
        assert transform_value("  \r ") is None
        assert transform_value("  \n\t\r ") is None

    def test_transform_value_method_whitespace_trimming(self) -> None:
        # Test whitespace trimming
        assert transform_value("  hello") == "hello"
        assert transform_value("hello  ") == "hello"
        assert transform_value("hello\t") == "hello"
        assert transform_value("hello\r") == "hello"
        assert transform_value("hello\n") == "hello"
        assert transform_value("  hello  ") == "hello"
        assert transform_value("\tworld \n") == "world"

    def test_transform_value_method_boolean_conversions(self) -> None:
        # Test boolean conversions (case-insensitive)
        assert transform_value("true") is True
        assert transform_value("True") is True
        assert transform_value("TRUE") is True
        assert transform_value("false") is False
        assert transform_value("False") is False
        assert transform_value("FALsE") is False
        assert transform_value("  true  ") is True
        assert transform_value("  fAlse  ") is False

    def test_transform_value_method_integer_conversions(self) -> None:
        # Test integer conversions
        assert transform_value("42") == 42
        assert transform_value("0") == 0
        assert transform_value("-123") == -123
        assert transform_value("  100  ") == 100
        assert transform_value("  -123  ") == -123

    def test_transform_value_method_float_conversions(self) -> None:
        # Test float conversions
        assert transform_value("3.14") == 3.14
        assert transform_value("0.5") == 0.5
        assert transform_value(".5") == 0.5
        assert transform_value("-.5") == -0.5
        assert transform_value("-2.718") == -2.718
        assert transform_value("1e5") == 1e5
        assert transform_value("1.5E-3") == 1.5e-3
        assert transform_value("  1.5E-3   ") == 1.5e-3
        assert transform_value("   -.5  ") == -0.5

    def test_transform_value_method_strings(self) -> None:
        # Test strings (no conversion)
        assert transform_value("hello") == "hello"
        assert transform_value("123abc") == "123abc"
        assert transform_value("yes") == "yes"
        assert transform_value("no") == "no"
        assert transform_value("null") == "null"

        # Edge cases
        assert transform_value("True123") == "True123"  # Not purely boolean
        assert transform_value("42.5.6") == "42.5.6"  # Invalid number
        assert transform_value("42.") == "42."  # Invalid number
        assert transform_value("42.5.") == "42.5."  # Invalid number


class TestSanitizeFieldName:
    """Test cases for sanitize_field_name method."""

    def test_empty_string_returns_none(self):
        """Test that empty string returns None."""
        assert sanitize_field_name("") is None

    def test_none_returns_none(self):
        """Test that None returns None."""
        assert sanitize_field_name(None) is None

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
            assert sanitize_field_name(name) == name

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
            assert sanitize_field_name(input_name) == expected

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
            assert sanitize_field_name(input_name) == expected

    def test_starts_with_hyphen_gets_field_prefix(self):
        """Test that field names starting with hyphens get 'field_' prefix."""
        test_cases = [
            ("-field", "field_-field"),
            ("-123", "field_-123"),
            ("-", "field_-"),
            ("-field-name", "field_-field-name"),
        ]

        for input_name, expected in test_cases:
            assert sanitize_field_name(input_name) == expected

    def test_multiple_invalid_characters(self):
        """Test field names with multiple invalid characters."""
        test_cases = [
            ("field@#$%name", "field____name"),
            ("@#$%field", "____field"),
            ("field@#$%", "field____"),
            ("@#$%", "____"),
        ]

        for input_name, expected in test_cases:
            assert sanitize_field_name(input_name) == expected

    def test_only_invalid_characters(self):
        """Test field names with only invalid characters."""
        test_cases = [
            ("@#$%", "____"),
            ("!@#$%^&*()", "__________"),
            ("   ", None),
            ("\t\n\r", None),
        ]

        for input_name, expected in test_cases:
            assert sanitize_field_name(input_name) == expected

    def test_mixed_valid_invalid_characters(self):
        """Test field names with mixed valid and invalid characters."""
        test_cases = [
            ("field@name123", "field_name123"),
            ("field-name@test", "field-name_test"),
            ("field_name@test#123", "field_name_test_123"),
            ("a@b#c$d%e^f&g", "a_b_c_d_e_f_g"),
        ]

        for input_name, expected in test_cases:
            assert sanitize_field_name(input_name) == expected

    def test_unicode_characters(self):
        """Test field names with unicode characters."""
        test_cases = [
            ("fieldñame", "field_ame"),
            ("field中文", "field__"),
            ("fieldαβγ", "field___"),
            ("field🚀", "field_"),
        ]

        for input_name, expected in test_cases:
            assert sanitize_field_name(input_name) == expected

    def test_very_long_field_names(self):
        """Test very long field names."""
        long_name = "a" * 1000
        assert sanitize_field_name(long_name) == long_name

        long_name_with_invalid = "a" * 500 + "@" + "b" * 500
        expected = "a" * 500 + "_" + "b" * 500
        assert sanitize_field_name(long_name_with_invalid) == expected

    def test_edge_cases(self):
        """Test edge cases."""
        # Single character
        assert sanitize_field_name("a") == "a"
        assert sanitize_field_name("1") == "field_1"
        assert sanitize_field_name("-") == "field_-"
        assert sanitize_field_name("@") == "_"

        # Only underscores and hyphens
        assert sanitize_field_name("_") == "_"
        assert sanitize_field_name("-") == "field_-"
        assert sanitize_field_name("_-") == "_-"
        assert sanitize_field_name("-_") == "field_-_"
