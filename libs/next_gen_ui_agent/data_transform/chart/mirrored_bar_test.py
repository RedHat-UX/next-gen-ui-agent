"""Tests for mirrored bar chart data transformer."""

from next_gen_ui_agent.data_transform.chart import MirroredBarChartDataTransformer
from next_gen_ui_agent.data_transform.validation.types import (
    ComponentDataValidationError,
)
from next_gen_ui_agent.types import InputData, UIComponentMetadata


def test_process_mirrored_bar_chart() -> None:
    """Test processing mirrored bar chart with two metrics."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_chart_2",
            "title": "Movie Revenue vs Budget",
            "component": "chart-mirrored-bar",
            "fields": [
                {"name": "Movie", "data_path": "movies[*].title"},
                {"name": "Revenue", "data_path": "movies[*].revenue"},
                {"name": "Budget", "data_path": "movies[*].budget"},
            ],
        }
    )
    data = InputData(
        id="test_chart_2",
        data="""{
            "movies": [
                {"title": "Movie A", "revenue": 150, "budget": 100},
                {"title": "Movie B", "revenue": 200, "budget": 120},
                {"title": "Movie C", "revenue": 180, "budget": 90}
            ]
        }""",
    )
    result = MirroredBarChartDataTransformer().process(c, data)
    assert result.title == "Movie Revenue vs Budget"
    assert result.component == "chart-mirrored-bar"
    assert result.data is not None
    assert len(result.data) == 2  # Two series (Revenue and Budget)
    assert result.data[0].name == "Revenue"
    assert result.data[1].name == "Budget"
    assert len(result.data[0].data) == 3
    assert result.data[0].data[0].x == "Movie A"
    assert result.data[0].data[0].y == 150


def test_validate_mirrored_bar_chart_ok() -> None:
    """Test validation passes with exactly 2 series."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_mirrored_valid",
            "title": "Valid Mirrored",
            "component": "chart-mirrored-bar",
            "fields": [
                {"name": "Category", "data_path": "data[*].category"},
                {"name": "Metric1", "data_path": "data[*].metric1"},
                {"name": "Metric2", "data_path": "data[*].metric2"},
            ],
        }
    )
    data = InputData(
        id="test_mirrored_valid",
        data="""{
            "data": [
                {"category": "A", "metric1": 10, "metric2": 20},
                {"category": "B", "metric1": 15, "metric2": 25}
            ]
        }""",
    )
    errors: list[ComponentDataValidationError] = []
    result = MirroredBarChartDataTransformer().validate(c, data, errors)
    assert len(errors) == 0
    assert result.component == "chart-mirrored-bar"
    assert result.data is not None
    assert len(result.data) == 2


def test_validate_mirrored_bar_chart_requires_exactly_two_series() -> None:
    """Test validation fails when not exactly 2 series."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_mirrored_invalid",
            "title": "Invalid Mirrored - Only One Series",
            "component": "chart-mirrored-bar",
            "fields": [
                {"name": "Category", "data_path": "data[*].category"},
                {"name": "Metric1", "data_path": "data[*].metric1"},
            ],
        }
    )
    data = InputData(
        id="test_mirrored_invalid",
        data="""{
            "data": [
                {"category": "A", "metric1": 10},
                {"category": "B", "metric1": 15}
            ]
        }""",
    )
    errors: list[ComponentDataValidationError] = []
    MirroredBarChartDataTransformer().validate(c, data, errors)
    # Should fail - mirrored bar needs exactly 3 fields (x + 2 metrics)
    assert len(errors) >= 1
    assert any(e.code == "chart.invalidSeriesCount" for e in errors)


def test_validate_mirrored_bar_chart_no_data() -> None:
    """Test validation fails with no data."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_mirrored_empty",
            "title": "Empty Mirrored",
            "component": "chart-mirrored-bar",
            "fields": [
                {"name": "Category", "data_path": "data[*].category"},
                {"name": "Metric1", "data_path": "data[*].metric1"},
                {"name": "Metric2", "data_path": "data[*].metric2"},
            ],
        }
    )
    data = InputData(
        id="test_mirrored_empty",
        data="""{"data": []}""",
    )
    errors: list[ComponentDataValidationError] = []
    MirroredBarChartDataTransformer().validate(c, data, errors)
    assert len(errors) >= 1
    assert any(e.code == "chart.invalidSeriesCount" for e in errors)


def test_mirrored_bar_chart_wrong_field_count() -> None:
    """Test mirrored bar chart with wrong number of fields."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_mirrored_4fields",
            "title": "Four Fields",
            "component": "chart-mirrored-bar",
            "fields": [
                {"name": "Category", "data_path": "data[*].category"},
                {"name": "Metric1", "data_path": "data[*].m1"},
                {"name": "Metric2", "data_path": "data[*].m2"},
                {"name": "Metric3", "data_path": "data[*].m3"},
            ],
        }
    )
    data = InputData(
        id="test_mirrored_4fields",
        data="""{
            "data": [
                {"category": "A", "m1": 10, "m2": 20, "m3": 30}
            ]
        }""",
    )
    errors: list[ComponentDataValidationError] = []
    result = MirroredBarChartDataTransformer().validate(c, data, errors)
    # Should fail - mirrored bar expects exactly 3 fields
    assert any(e.code == "chart.invalidSeriesCount" for e in errors)
    assert result.data == []
