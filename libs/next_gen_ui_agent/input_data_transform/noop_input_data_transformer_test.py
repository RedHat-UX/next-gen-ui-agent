import json
import time
from typing import cast

from jsonpath_ng import parse  # type: ignore
from next_gen_ui_agent.input_data_transform.noop_input_data_transformer import (
    NoopInputDataTransformer,
)
from next_gen_ui_agent.types import InputData
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


class TestNoopInputDataTransformerDetectMyDataStructure:
    """Test cases for NoopInputDataTransformer.detect_my_data_structure()."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.transformer = NoopInputDataTransformer()

    def test_detect_always_returns_false(self) -> None:
        """Test detection always returns False - NOOP should not be auto-detected."""
        input_data = cast(InputData, {"id": "test1", "data": "any text"})
        assert self.transformer.detect_my_data_structure(input_data) is False

    def test_detect_performance_for_large_data(self) -> None:
        """Test detection completes in <0.01s for large data, always returns False instantly."""
        # Create 100KB of data (NOOP should return False instantly regardless of size)
        large_text = "line of text " * 10000
        input_data = cast(InputData, {"id": "perf_test", "data": large_text})

        start_time = time.perf_counter()
        result = self.transformer.detect_my_data_structure(input_data)
        elapsed_time = time.perf_counter() - start_time

        assert result is False
        assert (
            elapsed_time < 0.01
        ), f"Detection took {elapsed_time:.4f}s, expected <0.01s"
