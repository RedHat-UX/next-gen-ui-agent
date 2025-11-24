from jinja2 import Environment, PackageLoader  # pants: no-infer-dep
from next_gen_ui_agent.data_transform.types import ComponentDataBase
from next_gen_ui_agent.renderer.base_renderer import RenderStrategyBase, StrategyFactory
from next_gen_ui_agent.renderer.one_card import OneCardRenderStrategy
from typing_extensions import override


class WebComponentsStrategyBase(RenderStrategyBase):
    templates_env: Environment

    def __init_subclass__(cls, template_subdir="templates", **kwargs):
        super().__init_subclass__(**kwargs)
        cls.templates_env = cls.create_templates_env(template_subdir)

    @classmethod
    def create_templates_env(cls, template_subdir="templates"):
        """Create a Jinja2 Environment using PackageLoader for the subclass's module."""
        module = cls.__module__
        return Environment(
            loader=PackageLoader(module, template_subdir),
            trim_blocks=True,
        )

    @override
    def generate_output(self, component, additional_context):
        template = self.templates_env.get_template(f"/{component.component}.jinja")
        return template.render(component.model_dump() | additional_context)


class WebComponentsOneCardRenderStrategy(OneCardRenderStrategy, WebComponentsStrategyBase):
    pass


class ImageRenderStrategy(RenderStrategyBase):
    COMPONENT_NAME = "image"


class WebComponentsImageRenderStrategy(ImageRenderStrategy, WebComponentsStrategyBase):
    pass


class WebComponentsStrategyFactory(StrategyFactory):
    def get_component_system_name(self) -> str:
        return "web-components"

    def get_output_mime_type(self) -> str:
        return "text/html"

    def get_render_strategy(self, component: ComponentDataBase):
        match component.component:
            case WebComponentsOneCardRenderStrategy.COMPONENT_NAME:
                return WebComponentsOneCardRenderStrategy()
            case WebComponentsImageRenderStrategy.COMPONENT_NAME:
                return WebComponentsImageRenderStrategy()
            case _:
                raise ValueError(
                    f"This component: {component.component} is not supported by Web Components rendering plugin."
                )
