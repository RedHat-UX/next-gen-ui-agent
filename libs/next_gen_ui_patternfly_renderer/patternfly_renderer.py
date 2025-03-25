from jinja2 import Environment, PackageLoader
from next_gen_ui_agent.base_renderer import (
    ImageRenderStrategy,
    OneCardRenderStrategy,
    RenderStrategy,
    SetOfCardsRenderStrategy,
    StrategyFactory,
    VideoRenderStrategy,
)
from next_gen_ui_agent.types import UIComponentMetadata

templates_env = Environment(
    loader=PackageLoader("next_gen_ui_patternfly_renderer", "templates"),
    trim_blocks=True,
)


class PatternflyStrategyBase(RenderStrategy):
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
            case "one-card":
                return PatternflyOneCardRenderStrategy()
            case "set-of-cards":
                return PatternflySetOfCardsRenderStrategy()
            case "image":
                return PatternflyImageRenderStrategy()
            case "video-player":
                return PatternflyVideoRenderStrategy()
            case _:
                raise ValueError(
                    f"This component: {component['component']} is not supported by Patternfly rendering plugin."
                )
