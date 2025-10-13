import json

from jsonpath_ng import parse  # type: ignore
from next_gen_ui_agent.input_data_transform.noop_input_data_transformer import (
    NoopInputDataTransformer,
)
from pydantic import BaseModel


class TestNoopInputDataTransformer:
    """Test cases for NoopInputDataTransformer."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.transformer = NoopInputDataTransformer()

    def test_transform_valid_string_object(self) -> None:
        """Test transforming a valid Noop object."""
        input_data = """line 1
line 2
line 3
"""
        result = self.transformer.transform(input_data)

        assert isinstance(result, str)
        assert result == input_data

    def test_transform_empty_string(self) -> None:
        """Test transforming empty string."""
        input_data = ""

        result = self.transformer.transform(input_data)
        assert isinstance(result, str)
        assert result == input_data

    def test_transform_whitespace_only(self) -> None:
        """Test transforming whitespace-only string."""
        input_data = "   \n\t  "

        result = self.transformer.transform(input_data)
        assert isinstance(result, str)
        assert result == input_data

    def test_transform_output_serializable_with_pydantic(self) -> None:
        """Test that transformer output can be serialized using Pydantic model_dump_json()."""

        # Create a simple Pydantic model for testing
        class TestModel(BaseModel):
            data: str

        # Test with object root
        input_data = """line 1
line 2
line 3

"""
        result = self.transformer.transform(input_data)

        # Create a Pydantic model instance with the transformed data
        model = TestModel(data=result)

        # Verify that model_dump_json() works without errors
        json_output = model.model_dump_json()
        assert isinstance(json_output, str)

        # Verify the JSON can be parsed back
        parsed_back = json.loads(json_output)
        assert "data" in parsed_back
        assert parsed_back["data"] == result

    def test_transform_output_accessible_with_jsonpath_ng_object(self) -> None:
        """Test that transformer output can be accessed using jsonpath_ng for object data."""
        # Test with complex nested object
        input_data = """line 1
line 2
line 3

"""
        result = self.transformer.transform(input_data)

        # test with wrapping into JSON object structure as it must be performed before LLM is used anf JSONPath used to extract data values
        result_wrapped = {"data": result}

        # Test various jsonpath expressions
        # Access data
        data_path = parse("$.data")
        data_matches = [match.value for match in data_path.find(result_wrapped)]
        assert data_matches[0] == input_data
