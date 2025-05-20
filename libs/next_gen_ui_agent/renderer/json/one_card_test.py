from next_gen_ui_agent.data_transform.types import ComponentDataOneCard
from next_gen_ui_agent.renderer.base_renderer import StrategyFactory
from next_gen_ui_agent.renderer.json.json_renderer import JsonStrategyFactory
from next_gen_ui_agent.renderer.one_card import OneCardRenderStrategy
from next_gen_ui_agent.renderer.one_card_shareable_tests import BaseOneCardRendererTests


class TestOneCardJsonRenderer(BaseOneCardRendererTests):
    def get_strategy_factory(self) -> StrategyFactory:
        return JsonStrategyFactory()


def test_render_json_output() -> None:
    strategy = OneCardRenderStrategy()
    c = ComponentDataOneCard.model_validate(
        {
            "id": "test_id_1",
            "title": "Toy Story Details",
            "component": "one-card",
            "fields": [
                {"name": "Title", "data_path": "movie.title", "data": ["Toy Story"]}
            ],
            "image": "https://image.tmdb.org/t/p/b.jpg",
        }
    )
    resultStr = strategy.generate_output(c)
    # print(resultStr)
    assert resultStr == c.model_dump_json()
