from unittest.mock import MagicMock, patch

import pytest
from next_gen_ui_agent.input_data_transform.input_data_transform import (
    PLUGGABLE_INPUT_DATA_TRANSFORMERS_NAMESPACE,
    get_input_data_transformer,
    input_data_transformer_extension_manager,
    perform_input_data_transformation,
    tr_json,
    tr_yaml,
)


class TestInputDataTransform:
    """Test cases for input_data_transform module."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        pass

    def test_get_input_data_transformer_yaml(self) -> None:
        """Test getting YAML input data transformer."""
        transformer = get_input_data_transformer("yaml")

        # Should return the same instance as tr_yaml
        assert transformer is tr_yaml
        assert transformer.__class__.__name__ == "YamlInputDataTransformer"

    def test_get_input_data_transformer_json(self) -> None:
        """Test getting JSON input data transformer."""
        transformer = get_input_data_transformer("json")

        # Should return the same instance as tr_json
        assert transformer is tr_json
        assert transformer.__class__.__name__ == "JsonInputDataTransformer"

    def test_get_input_data_transformer_invalid_name(self) -> None:
        """Test getting transformer with invalid name raises KeyError."""
        with pytest.raises(
            KeyError, match="No input data transformer found for name: invalid"
        ):
            get_input_data_transformer("invalid")

    def test_get_input_data_transformer_empty_name(self) -> None:
        """Test getting transformer with empty name raises KeyError."""
        with pytest.raises(
            KeyError, match="No input data transformer found for name: "
        ):
            get_input_data_transformer("")

    @patch(
        "next_gen_ui_agent.input_data_transform.input_data_transform.input_data_transformer_extension_manager"
    )
    def test_get_input_data_transformer_extension_manager(
        self, mock_extension_manager
    ) -> None:
        """Test getting transformer from extension manager."""
        # Mock the extension manager
        mock_transformer = MagicMock()
        mock_extension_manager.__contains__.return_value = True
        mock_extension_manager.__getitem__.return_value.obj = mock_transformer

        transformer = get_input_data_transformer("custom_transformer")

        assert transformer is mock_transformer
        mock_extension_manager.__contains__.assert_called_once_with(
            "custom_transformer"
        )
        mock_extension_manager.__getitem__.assert_called_once_with("custom_transformer")

    def test_perform_input_data_transformation_yaml(self) -> None:
        """Test performing YAML input data transformation."""
        input_data = """
name: John
age: 30
city: New York
"""
        result = perform_input_data_transformation("yaml", input_data)

        expected = {"name": "John", "age": 30, "city": "New York"}
        assert result == expected
        assert isinstance(result, dict)

    def test_perform_input_data_transformation_json(self) -> None:
        """Test performing JSON input data transformation."""
        input_data = '{"name": "John", "age": 30, "city": "New York"}'
        result = perform_input_data_transformation("json", input_data)

        expected = {"name": "John", "age": 30, "city": "New York"}
        assert result == expected
        assert isinstance(result, dict)

    def test_perform_input_data_transformation_none_input(self) -> None:
        """Test performing transformation with None input raises ValueError."""
        with pytest.raises(ValueError, match="Input data not provided"):
            perform_input_data_transformation("json", None)

    def test_perform_input_data_transformation_invalid_transformer(self) -> None:
        """Test performing transformation with invalid transformer name."""
        with pytest.raises(
            KeyError, match="No input data transformer found for name: invalid"
        ):
            perform_input_data_transformation("invalid", '{"test": "data"}')

    def test_perform_input_data_transformation_invalid_yaml(self) -> None:
        """Test performing transformation with invalid YAML data."""
        input_data = """
name: John
age: 30
  city: New York  # Invalid indentation
"""
        with pytest.raises(ValueError, match="Invalid YAML format of the Input Data"):
            perform_input_data_transformation("yaml", input_data)

    def test_perform_input_data_transformation_invalid_json(self) -> None:
        """Test performing transformation with invalid JSON data."""
        input_data = '{"name": "John", "age": 30'  # Missing closing brace
        with pytest.raises(ValueError, match="Invalid JSON format of the Input Data"):
            perform_input_data_transformation("json", input_data)

    def test_constants_and_globals(self) -> None:
        """Test that constants and global variables are properly set."""
        # Test namespace constant
        assert (
            PLUGGABLE_INPUT_DATA_TRANSFORMERS_NAMESPACE
            == "next_gen_ui.agent.input_data_transformer_factory"
        )

        # Test that extension manager is created
        assert input_data_transformer_extension_manager is not None

        # Test that default transformers are created
        assert tr_yaml is not None
        assert tr_json is not None
        assert tr_yaml.__class__.__name__ == "YamlInputDataTransformer"
        assert tr_json.__class__.__name__ == "JsonInputDataTransformer"
