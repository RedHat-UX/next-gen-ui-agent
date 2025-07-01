# Substantial portions of this file were generated with help of Cursor AI

from abc import ABC, abstractmethod

from next_gen_ui_agent.data_transform.types import ComponentDataImage
from next_gen_ui_agent.renderer.base_renderer import StrategyFactory

SAMPLE_IMAGE_DATA = {
    "id": "DUMMY_ID",
    "title": "DUMMY_MAIN_TITLE_VALUE",
    "component": "image",
    "image": "DUMMY_IMAGE_URL_VALUE",
}


class BaseImageRendererTests(ABC):
    """Shareable image component tests.

    In order to have basic tests for your renderer, you can inherit from this class
    and implement the get_strategy_factory method. This class will then provide the
    basic tests for your renderer.

    Example:
        class TestImageJsonRendererWithShareableTests(BaseImageRendererTests):
            def get_strategy_factory(self) -> StrategyFactory:
                return JsonStrategyFactory()

    Note:
        If you intentionally want to omit one of the tests, you can override the test
        method with 'pass'.
    """

    @abstractmethod
    def get_strategy_factory(self) -> StrategyFactory:
        pass

    def _render_sample_image(self) -> str:
        c = ComponentDataImage.model_validate(SAMPLE_IMAGE_DATA)
        strategy = self.get_strategy_factory().get_render_strategy(c)
        result = strategy.render(c)
        return result

    def test_renders_main_title_value(self):
        result = self._render_sample_image()
        assert "DUMMY_MAIN_TITLE_VALUE" in result

    def test_renders_image_url_value(self):
        result = self._render_sample_image()
        assert "DUMMY_IMAGE_URL_VALUE" in result
