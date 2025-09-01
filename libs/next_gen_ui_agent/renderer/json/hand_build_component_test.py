from next_gen_ui_agent.data_transform.types import ComponentDataHandBuildComponent
from next_gen_ui_agent.renderer.base_renderer import StrategyFactory
from next_gen_ui_agent.renderer.hand_build_component import (
    HandBuildComponentRenderStrategy,
)
from next_gen_ui_agent.renderer.hand_build_component_shareable_tests import (
    BaseHandBuildComponentRendererTests,
)
from next_gen_ui_agent.renderer.json.json_renderer import JsonStrategyFactory


class TestHandBuildComponentJsonRendererWithShareableTests(
    BaseHandBuildComponentRendererTests
):
    """Test class for JSON renderer using shared test cases for image component."""

    def get_strategy_factory(self) -> StrategyFactory:
        return JsonStrategyFactory()


def test_render_json_output() -> None:
    strategy = HandBuildComponentRenderStrategy()
    c = ComponentDataHandBuildComponent.model_validate(
        {
            "id": "test_id_1",
            "data": {
                "movies": [
                    {"title": "Toy Story", "authors": ["A1", "A2"]},
                    {"title": "Toy Story 2", "authors": ["A3"]},
                ]
            },
            "component": "hand-build-component",
            "component_type": "one-card-special",
        }
    )
    resultStr = strategy.render(c)
    # print(resultStr)
    assert resultStr == c.model_dump_json()
