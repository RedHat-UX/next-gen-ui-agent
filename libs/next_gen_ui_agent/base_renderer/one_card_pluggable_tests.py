from abc import ABC, abstractmethod

from next_gen_ui_agent.base_renderer.base_renderer import StrategyFactory
from next_gen_ui_agent.json_renderer.json_renderer import JsonStrategyFactory
from next_gen_ui_agent.types import UIComponentMetadata

class BaseOneCardRendererTests(ABC):

    @abstractmethod
    def get_strategy_factory(self) -> StrategyFactory:
        pass
    
    def test_fields(self):
        c = UIComponentMetadata(
            {
                "id": "test_id_1",
                "title": "Toy Story Details",
                "reasonForTheComponentSelection": "One item available in the data",
                "confidenceScore": "100%",
                "component": "one-card",
                "fields": [
                    {"name": "DUMMY_NAME_VALUE", "data_path": "movie.title", "data": ["DUMMY_MOVIE_TITLE"]},
                    {
                        "name": "DUMMY_POSTER_NAME",
                        "data_path": "movie.posterUrl",
                        "data": [
                            "DUMMY_IMG_URL"
                        ],
                    },
                ],
            }
        )
        strategy = self.get_strategy_factory().get_render_strategy(c)
        result = strategy.render(c)
        assert "DUMMY_MOVIE_TITLE" in result
        assert "DUMMY_IMG_URL" in result
        assert "DUMMY_NAME_VALUE" in result
        assert "DUMMY_POSTER_NAME" in result


class TestJsonRenderer(BaseOneCardRendererTests):
    def get_strategy_factory(self) -> StrategyFactory:
        return JsonStrategyFactory()