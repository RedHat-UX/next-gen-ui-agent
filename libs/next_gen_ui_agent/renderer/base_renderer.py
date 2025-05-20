from abc import ABC, ABCMeta, abstractmethod

from next_gen_ui_agent.data_transform.types import ComponentDataBase

PLUGGABLE_RENDERERS_NAMESPACE = "next_gen_ui.agent.renderer_factory"


class RenderStrategyBase(ABC):
    """Renderer Base."""

    def generate_output(self, component: ComponentDataBase) -> str:
        """Generate output by defined strategy.

        If not overriden then JSON dump is performed
        """
        return component.model_dump_json()


class RendererContext:
    """Render performing rendering based for given strategy."""

    def __init__(self, strategy: RenderStrategyBase):
        self.render_strategy = strategy

    def render(self, component: ComponentDataBase):
        return self.render_strategy.generate_output(component)


class StrategyFactory(metaclass=ABCMeta):
    """Abstract Strategy Factory Base."""

    @abstractmethod
    def get_component_system_name(self) -> str:
        raise NotImplementedError(
            "Renderer Strategy has to implement get_component_system method"
        )

    @abstractmethod
    def get_output_mime_type(self) -> str:
        raise NotImplementedError(
            "Renderer Strategy has to implement get_output_mime_type method"
        )

    @abstractmethod
    def get_render_strategy(self, component: ComponentDataBase) -> RenderStrategyBase:
        raise NotImplementedError(
            "Renderer Strategy has to implement get_render_strategy method"
        )
