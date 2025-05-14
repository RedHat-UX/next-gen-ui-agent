from next_gen_ui_agent.renderer.base_renderer import StrategyFactory
from next_gen_ui_agent.renderer.json.json_renderer import JsonStrategyFactory
from next_gen_ui_agent.renderer.one_card import OneCardRenderStrategy
from next_gen_ui_agent.renderer.one_card_shareable_tests import BaseOneCardRendererTests
from next_gen_ui_agent.types import UIComponentMetadata


class TestOneCardJsonRenderer(BaseOneCardRendererTests):
    def get_strategy_factory(self) -> StrategyFactory:
        return JsonStrategyFactory()


def test_render_json_output() -> None:
    strategy = OneCardRenderStrategy()
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_id_1",
            "title": "Toy Story Details",
            "reasonForTheComponentSelection": "One item available in the data",
            "confidenceScore": "100%",
            "component": "one-card",
            "fields": [
                {"name": "Title", "data_path": "movie.title", "data": ["Toy Story"]},
                {
                    "name": "Poster",
                    "data_path": "movie.posterUrl",
                    "data": [
                        "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg"
                    ],
                },
            ],
        }
    )
    resultStr = strategy.render(c)
    # print(resultStr)
    assert (
        resultStr
        == """{"component":"one-card","image":"https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg","title":"Toy Story Details","fields":[{"name":"Title","data_path":"movie.title","data":["Toy Story"]}],"data_length":1,"field_names":["Title"]}"""
    )
