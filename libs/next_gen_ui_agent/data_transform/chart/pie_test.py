"""Tests for pie chart data transformer."""

from next_gen_ui_agent.data_transform.chart import PieChartDataTransformer
from next_gen_ui_agent.data_transform.validation.types import (
    ComponentDataValidationError,
)
from next_gen_ui_agent.types import InputData, UIComponentMetadata


def test_process_pie_chart_with_frequency_counting() -> None:
    """Test processing pie chart with frequency counting."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_chart_3",
            "title": "Genre Distribution",
            "component": "chart-pie",
            "fields": [
                {
                    "name": "Genre",
                    "data_path": "movies[*].genre",
                }
            ],
        }
    )
    data = InputData(
        id="test_chart_3",
        data="""{
            "movies": [
                {"genre": "Action"},
                {"genre": "Comedy"},
                {"genre": "Action"},
                {"genre": "Drama"},
                {"genre": "Action"}
            ]
        }""",
    )
    result = PieChartDataTransformer().process(c, data)
    assert result.title == "Genre Distribution"
    assert result.component == "chart-pie"
    assert result.data is not None
    assert len(result.data) == 1
    assert result.data[0].name == "Genre"
    assert len(result.data[0].data) == 3  # 3 unique genres
    # Check that Action appears 3 times
    action_point = next(p for p in result.data[0].data if p.x == "Action")
    assert action_point.y == 3.0


def test_process_pie_chart_with_array_flattening() -> None:
    """Test processing pie chart with array values that need flattening."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_pie_array",
            "title": "Tags Distribution",
            "component": "chart-pie",
            "fields": [
                {
                    "name": "Tags",
                    "data_path": "items[*].tags",
                }
            ],
        }
    )
    data = InputData(
        id="test_pie_array",
        data="""{
            "items": [
                {"tags": ["important", "urgent"]},
                {"tags": ["important"]},
                {"tags": ["urgent", "review"]}
            ]
        }""",
    )
    result = PieChartDataTransformer().process(c, data)
    assert result.component == "chart-pie"
    assert result.data is not None
    # important: 2, urgent: 2, review: 1
    important_point = next(p for p in result.data[0].data if p.x == "important")
    assert important_point.y == 2.0
    urgent_point = next(p for p in result.data[0].data if p.x == "urgent")
    assert urgent_point.y == 2.0


def test_validate_pie_chart_ok() -> None:
    """Test validation passes with valid data."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_pie_valid",
            "title": "Valid Pie",
            "component": "chart-pie",
            "fields": [
                {"name": "Category", "data_path": "data[*].category"},
            ],
        }
    )
    data = InputData(
        id="test_pie_valid",
        data="""{
            "data": [
                {"category": "A"},
                {"category": "B"},
                {"category": "A"}
            ]
        }""",
    )
    errors: list[ComponentDataValidationError] = []
    result = PieChartDataTransformer().validate(c, data, errors)
    assert len(errors) == 0
    assert result.component == "chart-pie"


def test_validate_pie_chart_no_data() -> None:
    """Test validation fails with no data."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_pie_empty",
            "title": "Empty Pie",
            "component": "chart-pie",
            "fields": [
                {"name": "Category", "data_path": "data[*].category"},
            ],
        }
    )
    data = InputData(
        id="test_pie_empty",
        data="""{"data": []}""",
    )
    errors: list[ComponentDataValidationError] = []
    PieChartDataTransformer().validate(c, data, errors)
    assert len(errors) >= 1
    assert any(e.code == "chart.noData" for e in errors)


def test_validate_pie_chart_invalid_path() -> None:
    """Test validation fails with invalid data path."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_pie_invalid_path",
            "title": "Invalid Path",
            "component": "chart-pie",
            "fields": [
                {"name": "Category", "data_path": "nonexistent[*].field"},
            ],
        }
    )
    data = InputData(
        id="test_pie_invalid_path",
        data="""{"data": [{"category": "A"}]}""",
    )
    errors: list[ComponentDataValidationError] = []
    PieChartDataTransformer().validate(c, data, errors)
    assert len(errors) >= 1


def test_pie_chart_wrong_field_count() -> None:
    """Test pie chart with more than one field uses only the first."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_pie_multi_field",
            "title": "Multiple Fields",
            "component": "chart-pie",
            "fields": [
                {"name": "Category", "data_path": "data[*].category"},
                {"name": "Extra", "data_path": "data[*].extra"},
            ],
        }
    )
    data = InputData(
        id="test_pie_multi_field",
        data="""{
            "data": [
                {"category": "A", "extra": "X"},
                {"category": "B", "extra": "Y"}
            ]
        }""",
    )
    errors: list[ComponentDataValidationError] = []
    result = PieChartDataTransformer().validate(c, data, errors)
    # Pie chart expects exactly 1 field, so should produce no data
    assert any(e.code == "chart.noData" for e in errors)
    assert result.data == []


def test_pie_chart_handles_none_values() -> None:
    """Test that None values are skipped in frequency counting."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_pie_nulls",
            "title": "Pie with Nulls",
            "component": "chart-pie",
            "fields": [
                {"name": "Status", "data_path": "items[*].status"},
            ],
        }
    )
    data = InputData(
        id="test_pie_nulls",
        data="""{
            "items": [
                {"status": "active"},
                {"status": null},
                {"status": "active"},
                {"status": "inactive"}
            ]
        }""",
    )
    result = PieChartDataTransformer().process(c, data)
    assert result.data is not None
    # Should only have active (2) and inactive (1), not null
    assert len(result.data[0].data) == 2
    active_point = next(p for p in result.data[0].data if p.x == "active")
    assert active_point.y == 2.0
