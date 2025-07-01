# Substantial portions of this file were generated with help of Cursor AI

from abc import ABC, abstractmethod

from next_gen_ui_agent.data_transform.types import ComponentDataOneCard
from next_gen_ui_agent.renderer.base_renderer import StrategyFactory

SAMPLE_ONE_CARD_DATA = {
    "id": "DUMMY_ID",
    "title": "DUMMY_MAIN_TITLE_VALUE",
    "component": "one-card",
    "fields": [
        {
            "name": "DUMMY_TITLE_NAME",
            "data_path": "DUMMY_TITLE_DATA_PATH",
            "data": ["DUMMY_TITLE_VALUE"],
        },
        {
            "name": "DUMMY_IMAGE_NAME",
            "data_path": "DUMMY_IMAGE_DATA_PATH",  # has not to end by url or link
            "data": ["DUMMY_IMAGE_VALUE"],
        },
    ],
}


class BaseOneCardRendererTests(ABC):
    """Shareable one-card component tests.

    In order to have basic tests for your renderer, you can inherit from this class
    and implement the get_strategy_factory method. This class will then provide the
    basic tests for your renderer.

    Example:
        class TestOneCardJsonRendererWithShareableTests(BaseOneCardRendererTests):
            def get_strategy_factory(self) -> StrategyFactory:
                return JsonStrategyFactory()

    Note:
        If you intentionally want to omit one of the tests, you can override the test
        method with 'pass'.
    """

    @abstractmethod
    def get_strategy_factory(self) -> StrategyFactory:
        pass

    def _render_sample_one_card(self) -> str:
        c = ComponentDataOneCard.model_validate(SAMPLE_ONE_CARD_DATA)
        strategy = self.get_strategy_factory().get_render_strategy(c)
        result = strategy.render(c)
        return result

    def test_renders_main_title_value(self):
        result = self._render_sample_one_card()
        assert "DUMMY_MAIN_TITLE_VALUE" in result

    def test_renders_image_name(self):
        result = self._render_sample_one_card()
        assert "DUMMY_IMAGE_NAME" in result

    def test_renders_image_value(self):
        result = self._render_sample_one_card()
        assert "DUMMY_IMAGE_VALUE" in result

    def test_renders_title_name(self):
        result = self._render_sample_one_card()
        assert "DUMMY_TITLE_NAME" in result

    def test_renders_title_value(self):
        result = self._render_sample_one_card()
        assert "DUMMY_TITLE_VALUE" in result
