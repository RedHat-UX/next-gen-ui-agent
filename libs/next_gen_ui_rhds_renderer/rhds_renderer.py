from jinja2 import Environment, PackageLoader  # pants: no-infer-dep
from next_gen_ui_agent.data_transform.types import ComponentDataBase
from next_gen_ui_agent.renderer.audio import AudioPlayerRenderStrategy
from next_gen_ui_agent.renderer.base_renderer import RenderStrategyBase, StrategyFactory
from next_gen_ui_agent.renderer.image import ImageRenderStrategy
from next_gen_ui_agent.renderer.one_card import OneCardRenderStrategy
from next_gen_ui_agent.renderer.set_of_cards import SetOfCardsRenderStrategy
from next_gen_ui_agent.renderer.table import TableRenderStrategy
from next_gen_ui_agent.renderer.video import VideoRenderStrategy
from typing_extensions import override

templates_env = Environment(
    loader=PackageLoader("next_gen_ui_rhds_renderer", "templates"),
    trim_blocks=True,
)


class RhdsStrategyBase(RenderStrategyBase):
    @override
    def generate_output(self, component, additional_context):
        template = templates_env.get_template(f"/{component.component}.jinja")
        return template.render(component.model_dump() | additional_context)


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
    def get_component_system_name(self) -> str:
        return "rhds"

    def get_output_mime_type(self) -> str:
        return "text/html"

    def get_render_strategy(self, component: ComponentDataBase):
        match component.component:
            case RhdsOneCardRenderStrategy.COMPONENT_NAME:
                return RhdsOneCardRenderStrategy()
            case RhdsTableRenderStrategy.COMPONENT_NAME:
                return RhdsTableRenderStrategy()
            case RhdsSetOfCardsRenderStrategy.COMPONENT_NAME:
                return RhdsSetOfCardsRenderStrategy()
            case RhdsImageRenderStrategy.COMPONENT_NAME:
                return RhdsImageRenderStrategy()
            case RhdsVideoRenderStrategy.COMPONENT_NAME:
                return RhdsVideoRenderStrategy()
            case RhdsAudioPlayerRenderStrategy.COMPONENT_NAME:
                return RhdsAudioPlayerRenderStrategy()
            case _:
                # TODO: use pluggable component renderer here for eg. HBC, only throw error if no rendering code is plugged into it
                raise ValueError(
                    f"This component: {component.component} is not supported by Red Hat Design System rendering plugin."
                )
