from next_gen_ui_agent.renderer.audio import AudioPlayerRenderStrategy
from next_gen_ui_agent.renderer.chart_line import LineChartRenderStrategy
from next_gen_ui_agent.renderer.chart_pie import PieChartRenderStrategy
from next_gen_ui_agent.renderer.image import ImageRenderStrategy
from next_gen_ui_agent.renderer.one_card import OneCardRenderStrategy
from next_gen_ui_agent.renderer.renderer_base import StrategyFactory
from next_gen_ui_agent.renderer.set_of_cards import SetOfCardsRenderStrategy
from next_gen_ui_agent.renderer.table import TableRenderStrategy
from next_gen_ui_agent.renderer.video import VideoRenderStrategy
from next_gen_ui_agent.types import UIComponentMetadata


class JsonStrategyFactory(StrategyFactory):
    """JSON Renderer.

    Rendering output is JSON
    """

    def get_render_strategy(self, component: UIComponentMetadata):
        match component["component"]:
            case OneCardRenderStrategy.COMPONENT_NAME:
                return OneCardRenderStrategy()
            case "table":
                return TableRenderStrategy()
            case "set-of-cards":
                return SetOfCardsRenderStrategy()
            case "image":
                return ImageRenderStrategy()
            case "video-player":
                return VideoRenderStrategy()
            case "audio-player":
                return AudioPlayerRenderStrategy()
            case "chart-line":
                return LineChartRenderStrategy()
            case "chart-pie":
                return PieChartRenderStrategy()
            case _:
                raise ValueError(
                    f"This component: {component['component']} is not supported by rendering plugin."
                )
