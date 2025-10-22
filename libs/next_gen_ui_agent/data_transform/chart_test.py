from next_gen_ui_agent.data_transform.chart import ChartDataTransformer
from next_gen_ui_agent.types import InputData, UIComponentMetadata


def test_process_chart_with_series() -> None:
    """Test processing chart data that already has series structure"""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_chart_1",
            "title": "Sales Data",
            "component": "chart",
            "chartType": "bar",
        }
    )
    data = InputData(
        id="test_chart_1",
        data="""{
            "data": [
                {
                    "name": "Q1",
                    "data": [
                        {"x": "Jan", "y": 100},
                        {"x": "Feb", "y": 150},
                        {"x": "Mar", "y": 200}
                    ]
                },
                {
                    "name": "Q2",
                    "data": [
                        {"x": "Apr", "y": 180},
                        {"x": "May", "y": 220},
                        {"x": "Jun", "y": 250}
                    ]
                }
            ]
        }""",
    )
    result = ChartDataTransformer().process(c, data)
    assert result.title == "Sales Data"
    assert result.chartType == "bar"
    assert len(result.data) == 2
    assert result.data[0].name == "Q1"
    assert len(result.data[0].data) == 3
    assert result.data[0].data[0].x == "Jan"
    assert result.data[0].data[0].y == 100
    assert result.data[1].name == "Q2"
    assert len(result.data[1].data) == 3


def test_process_chart_with_flat_data() -> None:
    """Test processing flat key-value data"""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_chart_2",
            "title": "Product Sales",
            "component": "chart",
            "chartType": "pie",
        }
    )
    data = InputData(
        id="test_chart_2",
        data="""{
            "Apples": 45,
            "Oranges": 30,
            "Bananas": 25
        }""",
    )
    result = ChartDataTransformer().process(c, data)
    assert result.title == "Product Sales"
    assert result.chartType == "pie"
    assert len(result.data) == 1
    assert result.data[0].name == "Data"
    assert len(result.data[0].data) == 3
    assert result.data[0].data[0].x == "Apples"
    assert result.data[0].data[0].y == 45


def test_process_chart_with_array_data() -> None:
    """Test processing array of objects"""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_chart_3",
            "title": "Monthly Revenue",
            "component": "chart",
            "chartType": "line",
        }
    )
    data = InputData(
        id="test_chart_3",
        data="""[
            {"name": "January", "value": 1000},
            {"name": "February", "value": 1500},
            {"name": "March", "value": 1200}
        ]""",
    )
    result = ChartDataTransformer().process(c, data)
    assert result.title == "Monthly Revenue"
    assert result.chartType == "line"
    assert len(result.data) == 1
    assert len(result.data[0].data) == 3
    assert result.data[0].data[0].x == "January"
    assert result.data[0].data[0].y == 1000.0


def test_process_chart_with_x_y_fields() -> None:
    """Test processing array with x/y fields"""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_chart_4",
            "title": "Data Points",
            "component": "chart",
            "chartType": "donut",
        }
    )
    data = InputData(
        id="test_chart_4",
        data="""[
            {"x": "Category A", "y": 40},
            {"x": "Category B", "y": 30},
            {"x": "Category C", "y": 30}
        ]""",
    )
    result = ChartDataTransformer().process(c, data)
    assert result.title == "Data Points"
    assert result.chartType == "donut"
    assert len(result.data) == 1
    assert len(result.data[0].data) == 3
    assert result.data[0].data[0].x == "Category A"
    assert result.data[0].data[0].y == 40.0


def test_validate_OK() -> None:
    """Test validation passes with valid data"""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_chart_5",
            "title": "Valid Chart",
            "component": "chart",
            "chartType": "bar",
        }
    )
    data = InputData(
        id="test_chart_5",
        data="""{
            "data": [
                {
                    "name": "Series 1",
                    "data": [{"x": "A", "y": 10}]
                }
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
            "id": "test_chart_6",
            "title": "Invalid Chart",
            "component": "chart",
            "chartType": "bar",
        }
    )
    data = InputData(
        id="test_chart_6",
        data="""{}""",
    )
    errors = []
    ChartDataTransformer().validate(c, data, errors)
    assert len(errors) == 1
    assert errors[0]["code"] == "chart.noData"


def test_validate_no_chart_type() -> None:
    """Test validation fails without chartType"""
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_chart_7",
            "title": "Invalid Chart",
            "component": "chart",
        }
    )
    data = InputData(
        id="test_chart_7",
        data="""{
            "data": [
                {
                    "name": "Series 1",
                    "data": [{"x": "A", "y": 10}]
                }
            ]
        }""",
    )
    errors = []
    ChartDataTransformer().validate(c, data, errors)
    assert len(errors) == 1
    assert errors[0]["code"] == "chart.noChartType"
