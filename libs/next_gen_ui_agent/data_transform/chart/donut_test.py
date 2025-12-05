"""Tests for donut chart data transformer."""

from next_gen_ui_agent.data_transform.chart import DonutChartDataTransformer
from next_gen_ui_agent.data_transform.validation.types import (
    ComponentDataValidationError,
)
from next_gen_ui_agent.types import InputData, UIComponentMetadata


def test_process_donut_chart_with_frequency_counting() -> None:
    """Test processing donut chart with frequency counting."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_donut_freq",
            "title": "Status Distribution",
            "component": "chart-donut",
            "fields": [
                {
                    "name": "Status",
                    "data_path": "tasks[*].status",
                }
            ],
        }
    )
    data = InputData(
        id="test_donut_freq",
        data="""{
            "tasks": [
                {"status": "Complete"},
                {"status": "In Progress"},
                {"status": "Complete"},
                {"status": "Complete"},
                {"status": "Pending"}
            ]
        }""",
    )
    result = DonutChartDataTransformer().process(c, data)
    assert result.title == "Status Distribution"
    assert result.component == "chart-donut"
    assert result.data is not None
    assert len(result.data) == 1
    assert result.data[0].name == "Status"
    assert len(result.data[0].data) == 3  # 3 unique statuses
    complete_point = next(p for p in result.data[0].data if p.x == "Complete")
    assert complete_point.y == 3.0


def test_process_donut_chart_with_array_flattening() -> None:
    """Test processing donut chart with array values that need flattening."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_chart_4",
            "title": "All Genres",
            "component": "chart-donut",
            "fields": [
                {
                    "name": "Genres",
                    "data_path": "movies[*].genres",
                }
            ],
        }
    )
    data = InputData(
        id="test_chart_4",
        data="""{
            "movies": [
                {"genres": ["Action", "Sci-Fi"]},
                {"genres": ["Comedy"]},
                {"genres": ["Action", "Drama"]}
            ]
        }""",
    )
    result = DonutChartDataTransformer().process(c, data)
    assert result.title == "All Genres"
    assert result.component == "chart-donut"
    assert result.data is not None
    assert len(result.data) == 1
    # Action should appear 2 times
    action_point = next(p for p in result.data[0].data if p.x == "Action")
    assert action_point.y == 2.0


def test_validate_donut_chart_ok() -> None:
    """Test validation passes with valid data."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_donut_valid",
            "title": "Valid Donut",
            "component": "chart-donut",
            "fields": [
                {"name": "Category", "data_path": "data[*].category"},
            ],
        }
    )
    data = InputData(
        id="test_donut_valid",
        data="""{
            "data": [
                {"category": "A"},
                {"category": "B"},
                {"category": "A"}
            ]
        }""",
    )
    errors: list[ComponentDataValidationError] = []
    result = DonutChartDataTransformer().validate(c, data, errors)
    assert len(errors) == 0
    assert result.component == "chart-donut"


def test_validate_donut_chart_no_data() -> None:
    """Test validation fails with no data."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_donut_empty",
            "title": "Empty Donut",
            "component": "chart-donut",
            "fields": [
                {"name": "Category", "data_path": "data[*].category"},
            ],
        }
    )
    data = InputData(
        id="test_donut_empty",
        data="""{"data": []}""",
    )
    errors: list[ComponentDataValidationError] = []
    DonutChartDataTransformer().validate(c, data, errors)
    assert len(errors) >= 1
    assert any(e.code == "chart.noData" for e in errors)


def test_validate_donut_chart_invalid_path() -> None:
    """Test validation fails with invalid data path."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_donut_invalid_path",
            "title": "Invalid Path",
            "component": "chart-donut",
            "fields": [
                {"name": "Category", "data_path": "nonexistent[*].field"},
            ],
        }
    )
    data = InputData(
        id="test_donut_invalid_path",
        data="""{"data": [{"category": "A"}]}""",
    )
    errors: list[ComponentDataValidationError] = []
    DonutChartDataTransformer().validate(c, data, errors)
    assert len(errors) >= 1


def test_donut_chart_wrong_field_count() -> None:
    """Test donut chart with more than one field produces no data."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_donut_multi_field",
            "title": "Multiple Fields",
            "component": "chart-donut",
            "fields": [
                {"name": "Category", "data_path": "data[*].category"},
                {"name": "Extra", "data_path": "data[*].extra"},
            ],
        }
    )
    data = InputData(
        id="test_donut_multi_field",
        data="""{
            "data": [
                {"category": "A", "extra": "X"},
                {"category": "B", "extra": "Y"}
            ]
        }""",
    )
    errors: list[ComponentDataValidationError] = []
    result = DonutChartDataTransformer().validate(c, data, errors)
    # Donut chart expects exactly 1 field
    assert any(e.code == "chart.noData" for e in errors)
    assert result.data == []


def test_donut_chart_handles_none_values() -> None:
    """Test that None values are skipped in frequency counting."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_donut_nulls",
            "title": "Donut with Nulls",
            "component": "chart-donut",
            "fields": [
                {"name": "Priority", "data_path": "items[*].priority"},
            ],
        }
    )
    data = InputData(
        id="test_donut_nulls",
        data="""{
            "items": [
                {"priority": "high"},
                {"priority": null},
                {"priority": "high"},
                {"priority": "low"}
            ]
        }""",
    )
    result = DonutChartDataTransformer().process(c, data)
    assert result.data is not None
    # Should only have high (2) and low (1), not null
    assert len(result.data[0].data) == 2
    high_point = next(p for p in result.data[0].data if p.x == "high")
    assert high_point.y == 2.0
