from next_gen_ui_agent.renderer_base import (
    AudioPlayerRenderStrategy,
    ImageRenderStrategy,
    LineChartRenderStrategy,
    OneCardRenderStrategy,
    PieChartRenderStrategy,
    SetOfCardsRenderStrategy,
    StrategyFactory,
    TableRenderStrategy,
    VideoRenderStrategy,
)
from next_gen_ui_agent.types import ComponentName, UIComponentMetadata


class JsonStrategyFactory(StrategyFactory):
    """JSON Renderer.

    Rendering output is JSON
    """

    def get_render_strategy(self, component: UIComponentMetadata):
        match component["component"]:
            case ComponentName.ONE_CARD.value:
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
