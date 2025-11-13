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


class RhdsStrategyBase(RenderStrategyBase):
    templates_env: Environment

    def __init_subclass__(cls, template_subdir="templates", **kwargs):
        super().__init_subclass__(**kwargs)
        cls.templates_env = cls.create_templates_env(template_subdir)

    @classmethod
    def create_templates_env(cls, template_subdir="templates"):
        """
        Create a Jinja2 Environment using PackageLoader for the subclass's module.

        This allows subclasses to easily load templates from their own module
        without having to manually set up their own templates_env.

        Usage:
            class MyStrategy(RhdsStrategyBase):
                def __init__(self):
                    self.templates_env = RhdsStrategyBase.create_templates_env("my_templates")

        Note:
            If you extend RhdsStrategyBase from a different package without overriding
            the constructor, templates will be loaded from your new package's directory,
            not from next_gen_ui_rhds_renderer. This is because cls.__module__ resolves
            to the subclass's module name. Make sure your package contains the required
            templates directory.

        Args:
            template_subdir: The subdirectory name in the module where templates are stored.
                           Defaults to "templates".

        Returns:
            A Jinja2 Environment configured for the calling class's module.
        """
        # Get the module name from the class
        module = cls.__module__
        return Environment(
            loader=PackageLoader(module, template_subdir),
            trim_blocks=True,
        )

    @override
    def generate_output(self, component, additional_context):
        template = self.templates_env.get_template(f"/{component.component}.jinja")
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
                return self.default_render_strategy_handler(component)

    def default_render_strategy_handler(self, component: ComponentDataBase):
        """Handle default case by checking against defined hand build components or throw error if not supported."""

        # If no hand build component matches, throw ValueError
        raise ValueError(
            f"This component: {component.component} is not supported by Red Hat Design System rendering plugin."
        )
