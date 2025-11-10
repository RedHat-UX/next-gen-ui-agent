from next_gen_ui_agent.data_transform.chart import ChartDataTransformer
from next_gen_ui_agent.types import InputData, UIComponentMetadata


def test_process_chart_with_two_fields() -> None:
    """Test processing chart with x-axis and y-axis fields"""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_chart_1",
            "title": "Movie Ratings",
            "component": "chart",
            "chartType": "bar",
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
    result = ChartDataTransformer().process(c, data)
    assert result.title == "Movie Ratings"
    assert result.chartType == "bar"
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
            "component": "chart",
            "chartType": "mirrored-bar",
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
    result = ChartDataTransformer().process(c, data)
    assert result.title == "Movie Revenue vs Budget"
    assert result.chartType == "mirrored-bar"
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
            "component": "chart",
            "chartType": "pie",
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
    result = ChartDataTransformer().process(c, data)
    assert result.title == "Genre Distribution"
    assert result.chartType == "pie"
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
            "component": "chart",
            "chartType": "donut",
            "fields": [
                {
                    "name": "Genres",
                    "data_path": "movies[*].genres[*]",
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
    result = ChartDataTransformer().process(c, data)
    assert result.title == "All Genres"
    assert result.chartType == "donut"
    assert len(result.data) == 1
    # Action should appear 2 times
    action_point = next(p for p in result.data[0].data if p.x == "Action")
    assert action_point.y == 2.0


def test_chart_type_inference_from_title() -> None:
    """Test that chart type can be inferred from title"""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_chart_5",
            "title": "Trends over time - line chart",
            "component": "chart",
            "fields": [
                {"name": "Month", "data_path": "data[*].month"},
                {"name": "Sales", "data_path": "data[*].sales"},
            ],
        }
    )
    data = InputData(
        id="test_chart_5",
        data="""{
            "data": [
                {"month": "Jan", "sales": 100},
                {"month": "Feb", "sales": 150}
            ]
        }""",
    )
    result = ChartDataTransformer().process(c, data)
    assert result.chartType == "line"  # Inferred from "line chart" in title


def test_validate_OK() -> None:
    """Test validation passes with valid data"""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_chart_6",
            "title": "Valid Chart",
            "component": "chart",
            "chartType": "bar",
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
    result = ChartDataTransformer().validate(c, data, errors)
    assert len(errors) == 0
    assert result.chartType == "bar"


def test_validate_no_data() -> None:
    """Test validation fails with no data"""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_chart_7",
            "title": "Invalid Chart",
            "component": "chart",
            "chartType": "bar",
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
    ChartDataTransformer().validate(c, data, errors)
    assert len(errors) >= 1
    # Should have chart.noData error
    assert any(e["code"] == "chart.noData" for e in errors)


def test_validate_invalid_data_path() -> None:
    """Test validation fails with invalid data path"""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_chart_8",
            "title": "Invalid Path",
            "component": "chart",
            "chartType": "bar",
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
    ChartDataTransformer().validate(c, data, errors)
    # Should have validation errors for invalid paths
    assert len(errors) >= 1


def test_handle_none_values() -> None:
    """Test that None values are handled gracefully"""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_chart_9",
            "title": "Chart with Nulls",
            "component": "chart",
            "chartType": "bar",
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
    result = ChartDataTransformer().process(c, data)
    # Should skip the null value
    assert len(result.data[0].data) == 2
    assert result.data[0].data[0].y == 10
    assert result.data[0].data[1].y == 30
