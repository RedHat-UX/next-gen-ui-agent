from next_gen_ui_agent.renderer.one_card_base_functions_test import test_fields
from next_gen_ui_rhds_renderer.rhds_renderer import RhdsStrategyFactory
from pytest import fixture

@fixture
def strategy_factory():
    return RhdsStrategyFactory()