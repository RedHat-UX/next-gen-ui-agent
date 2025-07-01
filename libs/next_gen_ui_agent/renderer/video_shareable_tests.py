# Substantial portions of this file were generated with help of Cursor AI

from abc import ABC, abstractmethod

from next_gen_ui_agent.data_transform.types import ComponentDataVideo
from next_gen_ui_agent.renderer.base_renderer import StrategyFactory

SAMPLE_VIDEO_DATA = {
    "id": "DUMMY_ID",
    "title": "DUMMY_MAIN_TITLE_VALUE",
    "component": "video-player",
    "video": "DUMMY_VIDEO_URL_VALUE",
    "video_img": "DUMMY_VIDEO_IMG_URL_VALUE",
}


class BaseVideoRendererTests(ABC):
    """Shareable video component tests.

    In order to have basic tests for your renderer, you can inherit from this class
    and implement the get_strategy_factory method. This class will then provide the
    basic tests for your renderer.

    Example:
        class TestVideoJsonRendererWithShareableTests(BaseVideoRendererTests):
            def get_strategy_factory(self) -> StrategyFactory:
                return JsonStrategyFactory()

    Note:
        If you intentionally want to omit one of the tests, you can override the test
        method with 'pass'.
    """

    @abstractmethod
    def get_strategy_factory(self) -> StrategyFactory:
        pass

    def _render_sample_video(self) -> str:
        c = ComponentDataVideo.model_validate(SAMPLE_VIDEO_DATA)
        strategy = self.get_strategy_factory().get_render_strategy(c)
        result = strategy.render(c)
        return result

    def test_renders_main_title_value(self):
        result = self._render_sample_video()
        assert "DUMMY_MAIN_TITLE_VALUE" in result

    def test_renders_video_url_value(self):
        result = self._render_sample_video()
        assert "DUMMY_VIDEO_URL_VALUE" in result

    def test_renders_video_img_url_value(self):
        result = self._render_sample_video()
        assert "DUMMY_VIDEO_IMG_URL_VALUE" in result
