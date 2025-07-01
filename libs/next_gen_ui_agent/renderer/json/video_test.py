from next_gen_ui_agent.renderer.base_renderer import StrategyFactory
from next_gen_ui_agent.renderer.json.json_renderer import JsonStrategyFactory
from next_gen_ui_agent.renderer.video_shareable_tests import BaseVideoRendererTests


class TestVideoJsonRendererWithShareableTests(BaseVideoRendererTests):
    """Test class for JSON renderer using shared test cases for video component."""

    def get_strategy_factory(self) -> StrategyFactory:
        return JsonStrategyFactory()
