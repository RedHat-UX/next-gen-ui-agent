"""Tests for line chart data transformer."""

from next_gen_ui_agent.data_transform.chart import LineChartDataTransformer
from next_gen_ui_agent.data_transform.validation.types import (
    ComponentDataValidationError,
)
from next_gen_ui_agent.types import InputData, UIComponentMetadata


def test_process_line_chart_standard() -> None:
    """Test processing standard line chart with multiple y-axis series."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_chart_5",
            "title": "Sales Trends",
            "component": "chart-line",
            "fields": [
                {"name": "Month", "data_path": "data[*].month"},
                {"name": "Sales", "data_path": "data[*].sales"},
                {"name": "Profit", "data_path": "data[*].profit"},
                {"name": "Expenses", "data_path": "data[*].expenses"},
            ],
        }
    )
    data = InputData(
        id="test_chart_5",
        data="""{
            "data": [
                {"month": "Jan", "sales": 100, "profit": 20, "expenses": 80},
                {"month": "Feb", "sales": 150, "profit": 35, "expenses": 115},
                {"month": "Mar", "sales": 120, "profit": 25, "expenses": 95}
            ]
        }""",
    )
    result = LineChartDataTransformer().process(c, data)
    assert result.component == "chart-line"
    assert result.title == "Sales Trends"
    assert result.data is not None
    assert len(result.data) == 3  # Three series (Sales, Profit, Expenses)
    assert result.data[0].name == "Sales"
    assert result.data[1].name == "Profit"
    assert result.data[2].name == "Expenses"
    assert len(result.data[0].data) == 3
    assert result.data[0].data[0].x == "Jan"
    assert result.data[0].data[0].y == 100
    assert result.data[1].data[0].x == "Jan"
    assert result.data[1].data[0].y == 20


def test_process_line_chart_two_fields() -> None:
    """Test processing line chart with just x and y fields."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_line_simple",
            "title": "Simple Line",
            "component": "chart-line",
            "fields": [
                {"name": "X", "data_path": "points[*].x"},
                {"name": "Y", "data_path": "points[*].y"},
            ],
        }
    )
    data = InputData(
        id="test_line_simple",
        data="""{
            "points": [
                {"x": "1", "y": 10},
                {"x": "2", "y": 25},
                {"x": "3", "y": 15}
            ]
        }""",
    )
    result = LineChartDataTransformer().process(c, data)
    assert result.component == "chart-line"
    assert result.data is not None
    assert len(result.data) == 1
    assert result.data[0].name == "Y"
    assert len(result.data[0].data) == 3


def test_process_line_chart_standard_three_fields() -> None:
    """Test processing standard line chart with 3 fields (x, y1, y2) - 2 lines."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_line_two_metrics",
            "title": "Sales and Profit Over Time",
            "component": "chart-line",
            "fields": [
                {"name": "Month", "data_path": "data[*].month"},
                {"name": "Sales", "data_path": "data[*].sales"},
                {"name": "Profit", "data_path": "data[*].profit"},
            ],
        }
    )
    data = InputData(
        id="test_line_two_metrics",
        data="""{
            "data": [
                {"month": "Jan", "sales": 100, "profit": 20},
                {"month": "Feb", "sales": 150, "profit": 35},
                {"month": "Mar", "sales": 120, "profit": 25}
            ]
        }""",
    )
    result = LineChartDataTransformer().process(c, data)
    assert result.component == "chart-line"
    assert result.data is not None
    assert len(result.data) == 2  # Two series (Sales and Profit)
    assert result.data[0].name == "Sales"
    assert result.data[1].name == "Profit"
    assert len(result.data[0].data) == 3
    assert len(result.data[1].data) == 3
    # Verify Sales data
    assert result.data[0].data[0].x == "Jan"
    assert result.data[0].data[0].y == 100
    assert result.data[0].data[1].x == "Feb"
    assert result.data[0].data[1].y == 150
    # Verify Profit data
    assert result.data[1].data[0].x == "Jan"
    assert result.data[1].data[0].y == 20
    assert result.data[1].data[1].x == "Feb"
    assert result.data[1].data[1].y == 35
    # Verify x-axis label is set from first field name
    assert result.x_axis_label == "Month"


def test_process_line_chart_multi_series() -> None:
    """Test processing multi-series line chart with 3 fields (series_id, x, y)."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_line_multi",
            "title": "Weekly Revenue by Movie",
            "component": "chart-line",
            "fields": [
                {"name": "Movie", "data_path": "movies[*].title"},
                {"name": "Week", "data_path": "movies[*].weeklyData[*].week"},
                {"name": "Revenue", "data_path": "movies[*].weeklyData[*].revenue"},
            ],
        }
    )
    data = InputData(
        id="test_line_multi",
        data="""{
            "movies": [
                {
                    "title": "Movie A",
                    "weeklyData": [
                        {"week": "W1", "revenue": 100},
                        {"week": "W2", "revenue": 150}
                    ]
                },
                {
                    "title": "Movie B",
                    "weeklyData": [
                        {"week": "W1", "revenue": 80},
                        {"week": "W2", "revenue": 120}
                    ]
                }
            ]
        }""",
    )
    result = LineChartDataTransformer().process(c, data)
    assert result.component == "chart-line"
    assert result.data is not None
    assert len(result.data) == 2  # Two series (Movie A and Movie B)
    assert result.data[0].name == "Movie A"
    assert result.data[1].name == "Movie B"
    # Each series should have 2 data points
    assert len(result.data[0].data) == 2
    assert len(result.data[1].data) == 2
    # Check Movie A's data
    assert result.data[0].data[0].x == "W1"
    assert result.data[0].data[0].y == 100
    assert result.data[0].data[1].x == "W2"
    assert result.data[0].data[1].y == 150
    # Verify x-axis label is set from second field name (x-axis) for multi-series
    assert result.x_axis_label == "Week"


def test_validate_line_chart_ok() -> None:
    """Test validation passes with valid data."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_line_valid",
            "title": "Valid Line",
            "component": "chart-line",
            "fields": [
                {"name": "X", "data_path": "data[*].x"},
                {"name": "Y", "data_path": "data[*].y"},
            ],
        }
    )
    data = InputData(
        id="test_line_valid",
        data="""{
            "data": [
                {"x": "A", "y": 10},
                {"x": "B", "y": 20}
            ]
        }""",
    )
    errors: list[ComponentDataValidationError] = []
    result = LineChartDataTransformer().validate(c, data, errors)
    assert len(errors) == 0
    assert result.component == "chart-line"


def test_validate_line_chart_no_data() -> None:
    """Test validation fails with no data."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_line_empty",
            "title": "Empty Line",
            "component": "chart-line",
            "fields": [
                {"name": "X", "data_path": "data[*].x"},
                {"name": "Y", "data_path": "data[*].y"},
            ],
        }
    )
    data = InputData(
        id="test_line_empty",
        data="""{"data": []}""",
    )
    errors: list[ComponentDataValidationError] = []
    LineChartDataTransformer().validate(c, data, errors)
    assert len(errors) >= 1
    assert any(e.code == "chart.noData" for e in errors)


def test_validate_line_chart_invalid_path() -> None:
    """Test validation fails with invalid data path."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_line_invalid_path",
            "title": "Invalid Path",
            "component": "chart-line",
            "fields": [
                {"name": "X", "data_path": "nonexistent[*].x"},
                {"name": "Y", "data_path": "nonexistent[*].y"},
            ],
        }
    )
    data = InputData(
        id="test_line_invalid_path",
        data="""{"data": [{"x": "A", "y": 10}]}""",
    )
    errors: list[ComponentDataValidationError] = []
    LineChartDataTransformer().validate(c, data, errors)
    assert len(errors) >= 1


def test_line_chart_insufficient_fields() -> None:
    """Test line chart with only one field produces no data."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_line_one_field",
            "title": "One Field Only",
            "component": "chart-line",
            "fields": [
                {"name": "X", "data_path": "data[*].x"},
            ],
        }
    )
    data = InputData(
        id="test_line_one_field",
        data="""{"data": [{"x": "A"}, {"x": "B"}]}""",
    )
    errors: list[ComponentDataValidationError] = []
    result = LineChartDataTransformer().validate(c, data, errors)
    # Should fail validation - needs at least 2 fields
    assert any(e.code == "chart.noData" for e in errors)
    assert result.data == []


def test_line_chart_handles_none_values() -> None:
    """Test that None values are handled gracefully."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_line_nulls",
            "title": "Line with Nulls",
            "component": "chart-line",
            "fields": [
                {"name": "X", "data_path": "data[*].x"},
                {"name": "Y", "data_path": "data[*].y"},
            ],
        }
    )
    data = InputData(
        id="test_line_nulls",
        data="""{
            "data": [
                {"x": "A", "y": 10},
                {"x": "B", "y": null},
                {"x": "C", "y": 30}
            ]
        }""",
    )
    result = LineChartDataTransformer().process(c, data)
    assert result.data is not None
    # Should skip the null value
    assert len(result.data[0].data) == 2
    assert result.data[0].data[0].y == 10
    assert result.data[0].data[1].y == 30


def test_line_chart_multi_series_uneven_data() -> None:
    """Test multi-series line chart fails gracefully with uneven data."""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_line_uneven",
            "title": "Uneven Data",
            "component": "chart-line",
            "fields": [
                {"name": "Series", "data_path": "items[*].name"},
                {"name": "X", "data_path": "items[*].data[*].x"},
                {"name": "Y", "data_path": "items[*].data[*].y"},
            ],
        }
    )
    data = InputData(
        id="test_line_uneven",
        data="""{
            "items": [
                {
                    "name": "Series A",
                    "data": [{"x": "1", "y": 10}, {"x": "2", "y": 20}]
                },
                {
                    "name": "Series B",
                    "data": [{"x": "1", "y": 15}]
                }
            ]
        }""",
    )
    # This should handle gracefully - uneven data points across series
    errors: list[ComponentDataValidationError] = []
    result = LineChartDataTransformer().validate(c, data, errors)
    # The multi-series logic expects evenly divisible data
    # With 2 series and 3 total points, it should fail/warn
    assert result.data == []  # No data produced due to uneven distribution
