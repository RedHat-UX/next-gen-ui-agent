from unittest.mock import MagicMock, patch

import pytest
from next_gen_ui_agent.input_data_transform.csv_input_data_transformer import (
    CsvCommaInputDataTransformer,
    CsvSemicolonInputDataTransformer,
    CsvTabInputDataTransformer,
)
from next_gen_ui_agent.input_data_transform.input_data_transform import (
    BUILTIN_INPUT_DATA_TRANSFORMERS,
    PLUGGABLE_INPUT_DATA_TRANSFORMERS_NAMESPACE,
    c,
    get_input_data_transformer,
    get_input_data_transformer_name,
    init_input_data_transformers,
    input_data_transformer_extension_manager,
    perform_input_data_transformation,
    perform_input_data_transformation_with_transformer_name,
)
from next_gen_ui_agent.input_data_transform.json_input_data_transformer import (
    JsonInputDataTransformer,
)
from next_gen_ui_agent.input_data_transform.noop_input_data_transformer import (
    NoopInputDataTransformer,
)
from next_gen_ui_agent.input_data_transform.yaml_input_data_transformer import (
    YamlInputDataTransformer,
)
from next_gen_ui_agent.types import AgentConfig, AgentConfigDataType, InputData


class TestInitInputDataTransformers:
    def test_init_input_data_transformers_UNCONFIGURED(self) -> None:
        """Test initializing input data transformers for configured data type."""

        config = AgentConfig()
        init_input_data_transformers(config)

        assert c.default_data_transformer == "json"
        assert c.per_type_data_transformers == {}

    def test_init_input_data_transformers_CONFIGURED_PER_TYPE_AND_DEFAULT(self) -> None:
        """Test initializing input data transformers for configured data type."""

        config = AgentConfig(
            data_transformer="yaml",
            data_types={
                "yaml_data": AgentConfigDataType(data_transformer="yaml"),
                "json_data": AgentConfigDataType(data_transformer="json"),
            },
        )
        init_input_data_transformers(config)

        assert c.default_data_transformer == "yaml"
        assert c.per_type_data_transformers == {
            "yaml_data": "yaml",
            "json_data": "json",
        }

    def test_init_input_data_transformers_CONFIGURED_PER_TYPE_ERROR(self) -> None:
        """Test initializing input data transformers for configured data type with error."""

        config = AgentConfig(
            data_types={
                "yaml_data": AgentConfigDataType(data_transformer="unknown"),
            }
        )
        with pytest.raises(
            KeyError, match="No input data transformer found for name: unknown"
        ):
            init_input_data_transformers(config)

    def test_init_input_data_transformers_CONFIGURED_DEFAULT_ERROR(self) -> None:
        """Test initializing input data transformers for configured default transformer error."""

        config = AgentConfig(data_transformer="unknown")

        with pytest.raises(
            KeyError, match="No input data transformer found for name: unknown"
        ):
            init_input_data_transformers(config)


class TestGetInputDataTransformerName:
    def test_get_input_data_transformer_name_CONFIGURED_PER_TYPE(self) -> None:
        """Test getting transformer name for configured data type."""

        config = AgentConfig(
            data_types={
                "yaml_data": AgentConfigDataType(data_transformer="yaml"),
                "json_data": AgentConfigDataType(data_transformer="json"),
            }
        )
        init_input_data_transformers(config)

        input_data = InputData(id="1", data="test data", type="yaml_data")
        transformer_name = get_input_data_transformer_name(input_data)
        assert transformer_name == "yaml"

        # use default json for unconfigured type
        input_data = InputData(id="1", data="test data", type="other_data")
        transformer_name = get_input_data_transformer_name(input_data)
        assert transformer_name == "json"

        # use default json without type
        input_data = InputData(id="1", data="test data")
        transformer_name = get_input_data_transformer_name(input_data)
        assert transformer_name == "json"

    def test_get_input_data_transformer_name_UNCONFIGURED(self) -> None:
        """Test getting transformer name if no any mapping is configured."""

        config = AgentConfig()
        init_input_data_transformers(config)

        # use default json for unconfigured type
        input_data = InputData(id="1", data="test data", type="unconf_data")
        transformer_name = get_input_data_transformer_name(input_data)
        assert transformer_name == "json"

        # use default json without type
        input_data = InputData(id="1", data="test data")
        transformer_name = get_input_data_transformer_name(input_data)
        assert transformer_name == "json"

    def test_get_input_data_transformer_name_CONFIGURED_AGENT(self) -> None:
        """Test getting transformer name if no any mapping is configured."""

        config = AgentConfig(
            data_transformer=YamlInputDataTransformer.TRANSFORMER_NAME,
            data_types={
                "yaml_data": AgentConfigDataType(data_transformer="yaml"),
                "json_data": AgentConfigDataType(data_transformer="json"),
            },
        )
        init_input_data_transformers(config)

        # use configured default without type
        input_data = InputData(id="1", data="test data")
        transformer_name = get_input_data_transformer_name(input_data)
        assert transformer_name == "yaml"

        # use configured default for unconfigured type
        input_data = InputData(id="1", data="test data", type="unconf_data")
        transformer_name = get_input_data_transformer_name(input_data)
        assert transformer_name == "yaml"

        # use correct one for configured type
        input_data = InputData(id="1", data="test data", type="json_data")
        transformer_name = get_input_data_transformer_name(input_data)
        assert transformer_name == "json"

    def test_get_input_data_transformer_name_CONFIGURED_AGENT_ERROR(self) -> None:
        """Test getting transformer name if no any mapping is configured."""

        config = AgentConfig(
            data_transformer="unknown",
            data_types={
                "yaml_data": AgentConfigDataType(data_transformer="yaml"),
                "json_data": AgentConfigDataType(data_transformer="json"),
                "custom_data": AgentConfigDataType(
                    data_transformer="custom_transformer"
                ),
            },
        )

        with pytest.raises(
            KeyError, match="No input data transformer found for name: unknown"
        ):
            init_input_data_transformers(config)


class TestGetInputDataTransformer:
    """Test cases for input_data_transform module."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        init_input_data_transformers(AgentConfig())

    def test_get_input_data_transformer_yaml(self) -> None:
        """Test getting YAML input data transformer."""
        transformer = get_input_data_transformer("yaml")

        # Should return the same instance as tr_yaml
        assert (
            transformer
            is BUILTIN_INPUT_DATA_TRANSFORMERS[
                YamlInputDataTransformer.TRANSFORMER_NAME
            ]
        )
        assert transformer.__class__.__name__ == "YamlInputDataTransformer"

    def test_get_input_data_transformer_json(self) -> None:
        """Test getting JSON input data transformer."""
        transformer = get_input_data_transformer("json")

        # Should return the same instance as tr_json
        assert (
            transformer
            is BUILTIN_INPUT_DATA_TRANSFORMERS[
                JsonInputDataTransformer.TRANSFORMER_NAME
            ]
        )
        assert transformer.__class__.__name__ == "JsonInputDataTransformer"

    def test_get_input_data_transformer_csv_comma(self) -> None:
        """Test getting CSV comma input data transformer."""
        transformer = get_input_data_transformer("csv-comma")

        assert (
            transformer
            is BUILTIN_INPUT_DATA_TRANSFORMERS[
                CsvCommaInputDataTransformer.TRANSFORMER_NAME
            ]
        )
        assert transformer.__class__.__name__ == "CsvCommaInputDataTransformer"

    def test_get_input_data_transformer_csv_semicolon(self) -> None:
        """Test getting CSV semicolon input data transformer."""
        transformer = get_input_data_transformer("csv-semicolon")

        assert (
            transformer
            is BUILTIN_INPUT_DATA_TRANSFORMERS[
                CsvSemicolonInputDataTransformer.TRANSFORMER_NAME
            ]
        )
        assert transformer.__class__.__name__ == "CsvSemicolonInputDataTransformer"

    def test_get_input_data_transformer_csv_tab(self) -> None:
        """Test getting CSV tab input data transformer."""
        transformer = get_input_data_transformer("csv-tab")

        assert (
            transformer
            is BUILTIN_INPUT_DATA_TRANSFORMERS[
                CsvTabInputDataTransformer.TRANSFORMER_NAME
            ]
        )
        assert transformer.__class__.__name__ == "CsvTabInputDataTransformer"

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


class TestPerformInputDataTransformation:
    """Test cases for input_data_transform module."""

    def setup_method(self) -> None:
        """Set up test fixtures."""

    def test_perform_input_data_transformation_DEFAULT(self) -> None:
        """Test performing JSON input data transformation."""

        init_input_data_transformers(AgentConfig())
        input_data = InputData(
            id="1", data='{"name": "John", "age": 30, "city": "New York"}'
        )
        result, transformer_name = perform_input_data_transformation(input_data)

        expected = {"name": "John", "age": 30, "city": "New York"}
        assert result == expected
        assert isinstance(result, dict)
        assert transformer_name == "json"

    def test_perform_input_data_transformation_CONFIGURED_DEFAULT(self) -> None:
        """Test performing YAML input data transformation."""

        config = AgentConfig(data_transformer="yaml")
        init_input_data_transformers(config)

        input_data = InputData(
            id="1",
            data="""
name: John
age: 30
city: New York
""",
        )
        result, transformer_name = perform_input_data_transformation(input_data)

        expected = {"name": "John", "age": 30, "city": "New York"}
        assert result == expected
        assert isinstance(result, dict)
        assert transformer_name == "yaml"

    def test_perform_input_data_transformation_CONFIGURED_PER_TYPE(self) -> None:
        """Test performing YAML input data transformation."""

        config = AgentConfig(
            data_types={
                "yaml_data": AgentConfigDataType(data_transformer="yaml"),
                "json_data": AgentConfigDataType(data_transformer="json"),
            }
        )
        init_input_data_transformers(config)

        input_data = InputData(
            id="1",
            type="yaml_data",
            data="""
name: John
age: 30
city: New York
""",
        )
        result, transformer_name = perform_input_data_transformation(input_data)

        expected = {"name": "John", "age": 30, "city": "New York"}
        assert result == expected
        assert isinstance(result, dict)
        assert transformer_name == "yaml"


class TestPerformInputDataTransformationWithTransformerName:
    """Test cases for input_data_transform module."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        init_input_data_transformers(AgentConfig())

    def test_perform_input_data_transformation_with_transformer_name(self) -> None:
        """Test performing YAML input data transformation with transformer name."""

        input_data = InputData(
            id="1",
            type="yaml_data",
            data="""
name: John
age: 30
city: New York
""",
        )
        result = perform_input_data_transformation_with_transformer_name(
            input_data, "yaml"
        )

        expected = {"name": "John", "age": 30, "city": "New York"}
        assert result == expected
        assert isinstance(result, dict)

    def test_perform_input_data_transformation_with_transformer_name_invalid_transformer_name(
        self,
    ) -> None:
        """Test performing YAML input data transformation with invalid transformer name."""

        input_data = InputData(
            id="1",
            data="",
        )
        with pytest.raises(
            KeyError, match="No input data transformer found for name: invalid"
        ):
            perform_input_data_transformation_with_transformer_name(
                input_data, "invalid"
            )


class TestConstantsAndGlobals:
    def setup_method(self) -> None:
        """Set up test fixtures."""
        init_input_data_transformers(AgentConfig())

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
        assert (
            BUILTIN_INPUT_DATA_TRANSFORMERS[
                YamlInputDataTransformer.TRANSFORMER_NAME
            ].__class__.__name__
            == "YamlInputDataTransformer"
        )
        assert (
            BUILTIN_INPUT_DATA_TRANSFORMERS[
                JsonInputDataTransformer.TRANSFORMER_NAME
            ].__class__.__name__
            == "JsonInputDataTransformer"
        )
        assert (
            BUILTIN_INPUT_DATA_TRANSFORMERS[
                CsvCommaInputDataTransformer.TRANSFORMER_NAME
            ].__class__.__name__
            == "CsvCommaInputDataTransformer"
        )
        assert (
            BUILTIN_INPUT_DATA_TRANSFORMERS[
                CsvSemicolonInputDataTransformer.TRANSFORMER_NAME
            ].__class__.__name__
            == "CsvSemicolonInputDataTransformer"
        )
        assert (
            BUILTIN_INPUT_DATA_TRANSFORMERS[
                CsvTabInputDataTransformer.TRANSFORMER_NAME
            ].__class__.__name__
            == "CsvTabInputDataTransformer"
        )
        assert (
            BUILTIN_INPUT_DATA_TRANSFORMERS[
                NoopInputDataTransformer.TRANSFORMER_NAME
            ].__class__.__name__
            == "NoopInputDataTransformer"
        )
