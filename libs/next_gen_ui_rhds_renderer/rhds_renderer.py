from jinja2 import Environment, FileSystemLoader
from next_gen_ui_agent.base_renderer import (
    AudioPlayerRenderStrategy,
    ImageRenderStrategy,
    OneCardRenderStrategy,
    RenderStrategy,
    SetOfCardsRenderStrategy,
    StrategyFactory,
    TableRenderStrategy,
    VideoRenderStrategy,
)
from next_gen_ui_agent.types import UIComponentMetadata

templates_env = Environment(
    loader=FileSystemLoader("./genie_agent/utils"), trim_blocks=True
)


class RhdsStrategyBase(RenderStrategy):
    def generate_output(self, component):
        template = templates_env.get_template(
            f'rhds_templates/{component["component"]}.jinja'
        )
        return template.render(self._rendering_context)


class RhdsOneCardRenderStrategy(OneCardRenderStrategy, RhdsStrategyBase):
    pass


class RhdsTableRenderStrategy(TableRenderStrategy, RhdsStrategyBase):
    pass


class RhdsSetOfCardsRenderStrategy(SetOfCardsRenderStrategy, RhdsStrategyBase):
    pass


class RhdsImageRenderStrategy(ImageRenderStrategy, RhdsStrategyBase):
    pass


class RhdsVideoRenderStrategy(VideoRenderStrategy, RhdsStrategyBase):
    pass


class RhdsAudioPlayerRenderStrategy(AudioPlayerRenderStrategy, RhdsStrategyBase):
    pass


class RhdsStrategyFactory(StrategyFactory):
    def get_render_strategy(self, component: UIComponentMetadata):
        match component["component"]:
            case "one-card":
                return RhdsOneCardRenderStrategy()
            case "table":
                return RhdsTableRenderStrategy()
            case "set-of-cards":
                return RhdsSetOfCardsRenderStrategy()
            case "image":
                return RhdsImageRenderStrategy()
            case "video-player":
                return RhdsVideoRenderStrategy()
            case "audio-player":
                return RhdsAudioPlayerRenderStrategy()
            case _:
                raise ValueError(
                    f"This component: {component['component']} is not supported by Red Hat Design System rendering plugin."
                )
