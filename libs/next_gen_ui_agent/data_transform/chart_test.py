from next_gen_ui_agent.data_transform.chart import (
    BarChartDataTransformer,
    DonutChartDataTransformer,
    LineChartDataTransformer,
    MirroredBarChartDataTransformer,
    PieChartDataTransformer,
)
from next_gen_ui_agent.types import InputData, UIComponentMetadata


def test_process_chart_with_two_fields() -> None:
    """Test processing chart with x-axis and y-axis fields"""
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
    assert len(result.data) == 1  # One series (Rating)
    assert result.data[0].name == "Rating"
    assert len(result.data[0].data) == 3
    assert result.data[0].data[0].x == "Movie A"
    assert result.data[0].data[0].y == 8.5
    assert result.data[0].data[1].x == "Movie B"
    assert result.data[0].data[1].y == 7.2


def test_process_chart_with_multiple_series() -> None:
    """Test processing chart with x-axis and multiple y-axis series"""
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
    assert len(result.data) == 2  # Two series (Revenue and Budget)
    assert result.data[0].name == "Revenue"
    assert result.data[1].name == "Budget"
    assert len(result.data[0].data) == 3
    assert result.data[0].data[0].x == "Movie A"
    assert result.data[0].data[0].y == 150


def test_process_pie_chart_with_single_field() -> None:
    """Test processing pie chart with frequency counting"""
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
    assert len(result.data) == 1
    assert result.data[0].name == "Genre"
    assert len(result.data[0].data) == 3  # 3 unique genres
    # Check that Action appears 3 times
    action_point = next(p for p in result.data[0].data if p.x == "Action")
    assert action_point.y == 3.0


def test_process_donut_chart_with_array_flattening() -> None:
    """Test processing donut chart with array values that need flattening"""
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
    assert len(result.data) == 1
    # Action should appear 2 times
    action_point = next(p for p in result.data[0].data if p.x == "Action")
    assert action_point.y == 2.0


def test_process_line_chart_with_time_series() -> None:
    """Test processing standard line chart with multiple y-axis series"""
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
    assert len(result.data) == 3  # Three series (Sales, Profit, Expenses)
    assert result.data[0].name == "Sales"
    assert result.data[1].name == "Profit"
    assert result.data[2].name == "Expenses"
    assert len(result.data[0].data) == 3
    assert result.data[0].data[0].x == "Jan"
    assert result.data[0].data[0].y == 100
    assert result.data[1].data[0].x == "Jan"
    assert result.data[1].data[0].y == 20


def test_validate_OK() -> None:
    """Test validation passes with valid data"""
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
    errors = []
    result = BarChartDataTransformer().validate(c, data, errors)
    assert len(errors) == 0
    assert result.component == "chart-bar"


def test_validate_no_data() -> None:
    """Test validation fails with no data"""
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
    errors = []
    BarChartDataTransformer().validate(c, data, errors)
    assert len(errors) >= 1
    # Should have chart.noData error
    assert any(e.code == "chart.noData" for e in errors)


def test_validate_invalid_data_path() -> None:
    """Test validation fails with invalid data path"""
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
    errors = []
    BarChartDataTransformer().validate(c, data, errors)
    # Should have validation errors for invalid paths
    assert len(errors) >= 1


def test_handle_none_values() -> None:
    """Test that None values are handled gracefully"""
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
    assert len(result.data[0].data) == 2
    assert result.data[0].data[0].y == 10
    assert result.data[0].data[1].y == 30
