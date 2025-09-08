from next_gen_ui_agent.data_transform.types import ComponentDataBase
from next_gen_ui_agent.renderer.audio import AudioPlayerRenderStrategy
from next_gen_ui_agent.renderer.base_renderer import StrategyFactory
from next_gen_ui_agent.renderer.hand_build_component import (
    HandBuildComponentRenderStrategy,
)
from next_gen_ui_agent.renderer.image import ImageRenderStrategy
from next_gen_ui_agent.renderer.one_card import OneCardRenderStrategy
from next_gen_ui_agent.renderer.set_of_cards import SetOfCardsRenderStrategy
from next_gen_ui_agent.renderer.table import TableRenderStrategy
from next_gen_ui_agent.renderer.video import VideoRenderStrategy


class JsonStrategyFactory(StrategyFactory):
    """JSON Renderer.

    Rendering output is JSON
    """

    def get_component_system_name(self) -> str:
        return "json"

    def get_output_mime_type(self) -> str:
        return "application/json"

    def get_render_strategy(self, component: ComponentDataBase):
        match component.component:
            case OneCardRenderStrategy.COMPONENT_NAME:
                return OneCardRenderStrategy()
            case TableRenderStrategy.COMPONENT_NAME:
                return TableRenderStrategy()
            case SetOfCardsRenderStrategy.COMPONENT_NAME:
                return SetOfCardsRenderStrategy()
            case ImageRenderStrategy.COMPONENT_NAME:
                return ImageRenderStrategy()
            case VideoRenderStrategy.COMPONENT_NAME:
                return VideoRenderStrategy()
            case AudioPlayerRenderStrategy.COMPONENT_NAME:
                return AudioPlayerRenderStrategy()
            case _:  # for unknown component type use hand-build component renderer which simply renders JSON. Might be made pluggable in the future.
                return HandBuildComponentRenderStrategy()
