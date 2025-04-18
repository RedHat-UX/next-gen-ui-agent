from jinja2 import Environment, PackageLoader  # pants: no-infer-dep
from next_gen_ui_agent.base_renderer.image import ImageRenderStrategy
from next_gen_ui_agent.base_renderer.one_card import OneCardRenderStrategy
from next_gen_ui_agent.base_renderer.base_renderer import RenderStrategyBase, StrategyFactory
from next_gen_ui_agent.base_renderer.set_of_cards import SetOfCardsRenderStrategy
from next_gen_ui_agent.base_renderer.video import VideoRenderStrategy
from next_gen_ui_agent.types import UIComponentMetadata

templates_env = Environment(
    loader=PackageLoader("next_gen_ui_patternfly_renderer", "templates"),
    trim_blocks=True,
)


class PatternflyStrategyBase(RenderStrategyBase):
    def generate_output(self, component):
        template = templates_env.get_template(f'/{component["component"]}.jinja')
        return template.render(self._rendering_context)


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
    def get_render_strategy(self, component: UIComponentMetadata):
        match component["component"]:
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
                    f"This component: {component['component']} is not supported by Patternfly rendering plugin."
                )
