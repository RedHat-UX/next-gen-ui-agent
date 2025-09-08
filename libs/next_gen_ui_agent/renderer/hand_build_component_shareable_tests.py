# Substantial portions of this file were generated with help of Cursor AI

from abc import ABC, abstractmethod

from next_gen_ui_agent.data_transform.types import ComponentDataHandBuildComponent
from next_gen_ui_agent.renderer.base_renderer import StrategyFactory

SAMPLE_HAND_BUILD_COMPONENT_DATA = {
    "id": "DUMMY_ID",
    "component": "DUMMY_COMPONENT_TYPE",
    "data": {
        "DUMMY_DATA": "DUMMY_VALUE",
    },
}


class BaseHandBuildComponentRendererTests(ABC):
    """Shareable hand-build component tests.

    In order to have basic tests for your renderer, you can inherit from this class
    and implement the get_strategy_factory method. This class will then provide the
    basic tests for your renderer.

    Example:
        class TestHandBuildComponentJsonRendererWithShareableTests(BaseHandBuildComponentRendererTests):
            def get_strategy_factory(self) -> StrategyFactory:
                return JsonStrategyFactory()

    Note:
        If you intentionally want to omit one of the tests, you can override the test
        method with 'pass'.
    """

    @abstractmethod
    def get_strategy_factory(self) -> StrategyFactory:
        pass

    def _render_sample_hand_build_component(self) -> str:
        c = ComponentDataHandBuildComponent.model_validate(
            SAMPLE_HAND_BUILD_COMPONENT_DATA
        )
        strategy = self.get_strategy_factory().get_render_strategy(c)
        result = strategy.render(c)
        return result

    def test_renders_component_type_value(self):
        result = self._render_sample_hand_build_component()
        assert "DUMMY_COMPONENT_TYPE" in result

    def test_renders_data_value(self):
        result = self._render_sample_hand_build_component()
        assert "DUMMY_DATA" in result
        assert "DUMMY_VALUE" in result
