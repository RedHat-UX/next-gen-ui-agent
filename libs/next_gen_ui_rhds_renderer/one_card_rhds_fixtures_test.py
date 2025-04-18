from next_gen_ui_agent.renderer.one_card_base_fixtures_test import BaseRendererTests
from next_gen_ui_rhds_renderer.rhds_renderer import RhdsStrategyFactory
from pytest import fixture

@fixture
def strategy_factory():
    return RhdsStrategyFactory()

class TestRhdsRenderer(BaseRendererTests):
    pass