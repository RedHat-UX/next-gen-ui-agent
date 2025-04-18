import json

from next_gen_ui_agent.base_renderer.one_card_pluggable_tests import BaseOneCardRendererTests
from next_gen_ui_agent.base_renderer.base_renderer import StrategyFactory
from next_gen_ui_agent.base_renderer.one_card import OneCardRenderStrategy
from next_gen_ui_agent.base_renderer.types import RenderContextOneCard
from next_gen_ui_agent.json_renderer.json_renderer import JsonStrategyFactory
from next_gen_ui_agent.types import UIComponentMetadata

class TestOneCardJsonRenderer(BaseOneCardRendererTests):
    def get_strategy_factory(self) -> StrategyFactory:
        return JsonStrategyFactory()

def test_render_json():
    strategy = OneCardRenderStrategy()
    c = UIComponentMetadata(
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
    result: RenderContextOneCard = json.loads(resultStr)
    assert (
        result["image"]
        == "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg"
    )
    assert len(result["fields"]) == 1
    assert len(result["field_names"]) == 1
