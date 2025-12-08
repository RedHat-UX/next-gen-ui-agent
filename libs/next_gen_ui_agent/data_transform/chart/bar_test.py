"""Tests for bar chart data transformer."""

from next_gen_ui_agent.data_transform.chart import BarChartDataTransformer
from next_gen_ui_agent.data_transform.validation.types import (
    ComponentDataValidationError,
)
from next_gen_ui_agent.types import InputData, UIComponentMetadata


def test_process_bar_chart_with_two_fields() -> None:
    """Test processing bar chart with x-axis and y-axis fields."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_chart_1",
            "title": "Movie Ratings",
            "component": "chart-bar",
            "fields": [
                {
                    "name": "Movie",
                    "data_path": "movies[*].title",
                },
                {
                    "name": "Rating",
                    "data_path": "movies[*].rating",
                },
            ],
        }
    )
    data = InputData(
        id="test_chart_1",
        data="""{
            "movies": [
                {"title": "Movie A", "rating": 8.5},
                {"title": "Movie B", "rating": 7.2},
                {"title": "Movie C", "rating": 9.1}
            ]
        }""",
    )
    result = BarChartDataTransformer().process(c, data)
    assert result.title == "Movie Ratings"
    assert result.component == "chart-bar"
    assert result.data is not None
    assert len(result.data) == 1  # One series (Rating)
    assert result.data[0].name == "Rating"
    assert len(result.data[0].data) == 3
    assert result.data[0].data[0].x == "Movie A"
    assert result.data[0].data[0].y == 8.5
    assert result.data[0].data[1].x == "Movie B"
    assert result.data[0].data[1].y == 7.2


def test_process_bar_chart_with_multiple_series() -> None:
    """Test processing bar chart with multiple y-axis series."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_bar_multi",
            "title": "Sales by Quarter",
            "component": "chart-bar",
            "fields": [
                {"name": "Quarter", "data_path": "data[*].quarter"},
                {"name": "Product A", "data_path": "data[*].productA"},
                {"name": "Product B", "data_path": "data[*].productB"},
            ],
        }
    )
    data = InputData(
        id="test_bar_multi",
        data="""{
            "data": [
                {"quarter": "Q1", "productA": 100, "productB": 80},
                {"quarter": "Q2", "productA": 120, "productB": 95}
            ]
        }""",
    )
    result = BarChartDataTransformer().process(c, data)
    assert result.component == "chart-bar"
    assert result.data is not None
    assert len(result.data) == 2  # Two series
    assert result.data[0].name == "Product A"
    assert result.data[1].name == "Product B"


def test_validate_bar_chart_ok() -> None:
    """Test validation passes with valid data."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_chart_6",
            "title": "Valid Chart",
            "component": "chart-bar",
            "fields": [
                {"name": "X", "data_path": "data[*].x"},
                {"name": "Y", "data_path": "data[*].y"},
            ],
        }
    )
    data = InputData(
        id="test_chart_6",
        data="""{
            "data": [
                {"x": "A", "y": 10},
                {"x": "B", "y": 20}
            ]
        }""",
    )
    errors: list[ComponentDataValidationError] = []
    result = BarChartDataTransformer().validate(c, data, errors)
    assert len(errors) == 0
    assert result.component == "chart-bar"


def test_validate_bar_chart_no_data() -> None:
    """Test validation fails with no data."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_chart_7",
            "title": "Invalid Chart",
            "component": "chart-bar",
            "fields": [
                {"name": "X", "data_path": "data[*].x"},
                {"name": "Y", "data_path": "data[*].y"},
            ],
        }
    )
    data = InputData(
        id="test_chart_7",
        data="""{"data": []}""",
    )
    errors: list[ComponentDataValidationError] = []
    BarChartDataTransformer().validate(c, data, errors)
    assert len(errors) >= 1
    assert any(e.code == "chart.noData" for e in errors)


def test_validate_bar_chart_invalid_data_path() -> None:
    """Test validation fails with invalid data path."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_chart_8",
            "title": "Invalid Path",
            "component": "chart-bar",
            "fields": [
                {"name": "X", "data_path": "nonexistent[*].field"},
                {"name": "Y", "data_path": "nonexistent[*].value"},
            ],
        }
    )
    data = InputData(
        id="test_chart_8",
        data="""{"data": [{"x": "A", "y": 10}]}""",
    )
    errors: list[ComponentDataValidationError] = []
    BarChartDataTransformer().validate(c, data, errors)
    assert len(errors) >= 1


def test_bar_chart_handle_none_values() -> None:
    """Test that None values are handled gracefully."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_chart_9",
            "title": "Chart with Nulls",
            "component": "chart-bar",
            "fields": [
                {"name": "Item", "data_path": "data[*].name"},
                {"name": "Value", "data_path": "data[*].value"},
            ],
        }
    )
    data = InputData(
        id="test_chart_9",
        data="""{
            "data": [
                {"name": "A", "value": 10},
                {"name": "B", "value": null},
                {"name": "C", "value": 30}
            ]
        }""",
    )
    result = BarChartDataTransformer().process(c, data)
    # Should skip the null value
    assert result.data is not None
    assert len(result.data[0].data) == 2
    assert result.data[0].data[0].y == 10
    assert result.data[0].data[1].y == 30


def test_bar_chart_insufficient_fields() -> None:
    """Test bar chart with only one field produces no data."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_bar_one_field",
            "title": "One Field Only",
            "component": "chart-bar",
            "fields": [
                {"name": "X", "data_path": "data[*].x"},
            ],
        }
    )
    data = InputData(
        id="test_bar_one_field",
        data="""{"data": [{"x": "A"}, {"x": "B"}]}""",
    )
    errors: list[ComponentDataValidationError] = []
    result = BarChartDataTransformer().validate(c, data, errors)
    # Should fail validation - needs at least 2 fields
    assert any(e.code == "chart.noData" for e in errors)
    assert result.data == []
