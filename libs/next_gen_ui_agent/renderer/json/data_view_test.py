from next_gen_ui_agent.data_transform.types import ComponentDataDataView
from next_gen_ui_agent.renderer.base_renderer import StrategyFactory
from next_gen_ui_agent.renderer.data_view import DataViewRenderStrategy
from next_gen_ui_agent.renderer.data_view_shareable_tests import (
    BaseDataViewRendererTests,
)
from next_gen_ui_agent.renderer.json.json_renderer import JsonStrategyFactory


class TestDataViewJsonRendererWithShareableTests(BaseDataViewRendererTests):
    """Test class for JSON renderer using shared test cases for data-view component."""

    def get_strategy_factory(self) -> StrategyFactory:
        return JsonStrategyFactory()


def test_render_json_output() -> None:
    """Test that JSON renderer outputs valid JSON matching the component data."""
    strategy = DataViewRenderStrategy()
    c = ComponentDataDataView.model_validate(
        {
            "id": "test_id_1",
            "title": "Movies",
            "component": "data-view",
            "fields": [
                {
                    "id": "movie_title",
                    "name": "Title",
                    "data_path": "movies[*].title",
                    "data": ["Toy Story", "Toy Story 2"],
                },
                {
                    "id": "movie_year",
                    "name": "Year",
                    "data_path": "movies[*].year",
                    "data": ["1995", "1999"],
                },
            ],
        }
    )
    result_str = strategy.render(c)
    assert result_str == c.model_dump_json()


def test_render_json_with_single_row() -> None:
    """Test JSON rendering with a single data row."""
    strategy = DataViewRenderStrategy()
    c = ComponentDataDataView.model_validate(
        {
            "id": "test_id_2",
            "title": "Single Movie",
            "component": "data-view",
            "fields": [
                {
                    "id": "movie_title",
                    "name": "Title",
                    "data_path": "movie.title",
                    "data": ["Toy Story"],
                },
                {
                    "id": "movie_year",
                    "name": "Year",
                    "data_path": "movie.year",
                    "data": ["1995"],
                },
            ],
        }
    )
    result_str = strategy.render(c)
    assert result_str == c.model_dump_json()
    assert "Toy Story" in result_str
    assert "1995" in result_str


def test_render_json_with_empty_data() -> None:
    """Test JSON rendering with empty data arrays."""
    strategy = DataViewRenderStrategy()
    c = ComponentDataDataView.model_validate(
        {
            "id": "test_id_3",
            "title": "Empty Data",
            "component": "data-view",
            "fields": [
                {
                    "id": "movie_title",
                    "name": "Title",
                    "data_path": "movies[*].title",
                    "data": [],
                },
                {
                    "id": "movie_year",
                    "name": "Year",
                    "data_path": "movies[*].year",
                    "data": [],
                },
            ],
        }
    )
    result_str = strategy.render(c)
    assert result_str == c.model_dump_json()
    # JSON is minified, so check for "data":[] (no space)
    assert '"data":[]' in result_str


def test_render_json_with_array_values() -> None:
    """Test JSON rendering with array values in field data."""
    strategy = DataViewRenderStrategy()
    c = ComponentDataDataView.model_validate(
        {
            "id": "test_id_4",
            "title": "Movies with Actors",
            "component": "data-view",
            "fields": [
                {
                    "id": "movie_title",
                    "name": "Title",
                    "data_path": "movies[*].title",
                    "data": ["Toy Story", "Toy Story 2"],
                },
                {
                    "id": "movie_actors",
                    "name": "Actors",
                    "data_path": "movies[*].actors",
                    "data": [["Tom Hanks", "Tim Allen"], ["Tom Hanks", "Tim Allen"]],
                },
            ],
        }
    )
    result_str = strategy.render(c)
    assert result_str == c.model_dump_json()
    assert "Toy Story" in result_str
    assert "Tom Hanks" in result_str
