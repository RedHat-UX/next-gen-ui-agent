from abc import ABC, abstractmethod

from next_gen_ui_agent.data_transform.types import ComponentDataOneCard
from next_gen_ui_agent.renderer.base_renderer import StrategyFactory
from next_gen_ui_agent.renderer.json.json_renderer import JsonStrategyFactory


class BaseOneCardRendererTests(ABC):
    @abstractmethod
    def get_strategy_factory(self) -> StrategyFactory:
        pass

    def test_fields(self):
        c = ComponentDataOneCard.model_validate(
            {
                "id": "test_id_1",
                "title": "Toy Story Details",
                "component": "one-card",
                "fields": [
                    {
                        "name": "DUMMY_NAME_VALUE",
                        "data_path": "movie.title",
                        "data": ["DUMMY_MOVIE_TITLE"],
                    },
                    {
                        "name": "DUMMY_POSTER_NAME",
                        "data_path": "movie.poster",  # has not to end by url or link
                        "data": ["DUMMY_IMG_URL"],
                    },
                ],
            }
        )
        strategy = self.get_strategy_factory().get_render_strategy(c)
        result = strategy.generate_output(c)
        assert "DUMMY_MOVIE_TITLE" in result
        assert "DUMMY_IMG_URL" in result
        assert "DUMMY_NAME_VALUE" in result
        assert "DUMMY_POSTER_NAME" in result


class TestJsonRenderer(BaseOneCardRendererTests):
    def get_strategy_factory(self) -> StrategyFactory:
        return JsonStrategyFactory()
