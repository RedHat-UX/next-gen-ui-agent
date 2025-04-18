from next_gen_ui_agent.base_renderer.audio import AudioPlayerRenderStrategy
from next_gen_ui_agent.base_renderer.chart_line import LineChartRenderStrategy
from next_gen_ui_agent.base_renderer.chart_pie import PieChartRenderStrategy
from next_gen_ui_agent.base_renderer.image import ImageRenderStrategy
from next_gen_ui_agent.base_renderer.one_card import OneCardRenderStrategy
from next_gen_ui_agent.base_renderer.base_renderer import StrategyFactory
from next_gen_ui_agent.base_renderer.set_of_cards import SetOfCardsRenderStrategy
from next_gen_ui_agent.base_renderer.table import TableRenderStrategy
from next_gen_ui_agent.base_renderer.video import VideoRenderStrategy
from next_gen_ui_agent.types import UIComponentMetadata


class JsonStrategyFactory(StrategyFactory):
    """JSON Renderer.

    Rendering output is JSON
    """

    def get_render_strategy(self, component: UIComponentMetadata):
        match component["component"]:
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
            case LineChartRenderStrategy.COMPONENT_NAME:
                return LineChartRenderStrategy()
            case PieChartRenderStrategy.COMPONENT_NAME:
                return PieChartRenderStrategy()
            case _:
                raise ValueError(
                    f"This component: {component['component']} is not supported by rendering plugin."
                )
