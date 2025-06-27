from next_gen_ui_agent.data_transform.types import ComponentDataImage
from next_gen_ui_agent.renderer.base_renderer import StrategyFactory
from next_gen_ui_agent.renderer.image import ImageRenderStrategy
from next_gen_ui_agent.renderer.image_shareable_tests import BaseImageRendererTests
from next_gen_ui_agent.renderer.json.json_renderer import JsonStrategyFactory


# Test class for JSON renderer using shared test cases
class TestImageJsonRendererWithShareableTests(BaseImageRendererTests):
    def get_strategy_factory(self) -> StrategyFactory:
        return JsonStrategyFactory()


def test_render_json_output() -> None:
    strategy = ImageRenderStrategy()
    c = ComponentDataImage.model_validate(
        {
            "id": "test_id_1",
            "image": "https://image.tmdb.org/test_path.jpg",
            "title": "Toy Story Poster",
            "component": "image",
        }
    )
    resultStr = strategy.render(c)
    # print(resultStr)
    assert resultStr == c.model_dump_json()
