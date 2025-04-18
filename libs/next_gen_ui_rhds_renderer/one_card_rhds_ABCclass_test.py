from next_gen_ui_agent.renderer.one_card_base_ABCclass_test import BaseRendererTests
from next_gen_ui_agent.renderer.renderer_base import StrategyFactory
from next_gen_ui_rhds_renderer.rhds_renderer import RhdsStrategyFactory

class TestRHDSRenderer(BaseRendererTests):
    def get_strategy_factory(self) -> StrategyFactory:
        return RhdsStrategyFactory()