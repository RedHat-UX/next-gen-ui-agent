from jinja2 import Environment, PackageLoader  # pants: no-infer-dep
from next_gen_ui_agent.data_transform.types import ComponentDataBase
from next_gen_ui_agent.renderer.base_renderer import RenderStrategyBase, StrategyFactory
from next_gen_ui_agent.renderer.image import ImageRenderStrategy
from next_gen_ui_agent.renderer.one_card import OneCardRenderStrategy
from next_gen_ui_agent.renderer.set_of_cards import SetOfCardsRenderStrategy
from next_gen_ui_agent.renderer.video import VideoRenderStrategy
from typing_extensions import override

templates_env = Environment(
    loader=PackageLoader("next_gen_ui_patternfly_renderer", "templates"),
    trim_blocks=True,
)


class PatternflyStrategyBase(RenderStrategyBase):
    @override
    def generate_output(self, component, additional_context):
        template = templates_env.get_template(f"/{component.component}.jinja")
        return template.render(component.model_dump() | additional_context)


class PatternflyOneCardRenderStrategy(OneCardRenderStrategy, PatternflyStrategyBase):
    pass


class PatternflySetOfCardsRenderStrategy(
    SetOfCardsRenderStrategy, PatternflyStrategyBase
):
    pass


class PatternflyImageRenderStrategy(ImageRenderStrategy, PatternflyStrategyBase):
    pass


class PatternflyVideoRenderStrategy(VideoRenderStrategy, PatternflyStrategyBase):
    pass


class PatternflyStrategyFactory(StrategyFactory):
    def get_component_system_name(self) -> str:
        return "patternfly"

    def get_output_mime_type(self) -> str:
        return "text/html"

    def get_render_strategy(self, component: ComponentDataBase):
        match component.component:
            case PatternflyOneCardRenderStrategy.COMPONENT_NAME:
                return PatternflyOneCardRenderStrategy()
            case PatternflySetOfCardsRenderStrategy.COMPONENT_NAME:
                return PatternflySetOfCardsRenderStrategy()
            case PatternflyImageRenderStrategy.COMPONENT_NAME:
                return PatternflyImageRenderStrategy()
            case PatternflyVideoRenderStrategy.COMPONENT_NAME:
                return PatternflyVideoRenderStrategy()
            case _:
                raise ValueError(
                    f"This component: {component.component} is not supported by Patternfly rendering plugin."
                )
