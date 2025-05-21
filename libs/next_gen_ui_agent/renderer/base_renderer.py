from abc import ABC, ABCMeta, abstractmethod
from typing import Any, Sized

from next_gen_ui_agent.data_transform.types import (
    ComponentDataBase,
    ComponentDataBaseWithArrayValueFileds,
)
from typing_extensions import override

PLUGGABLE_RENDERERS_NAMESPACE = "next_gen_ui.agent.renderer_factory"


class RenderStrategyBase(ABC):
    """Renderer Base."""

    def render(self, component: ComponentDataBase) -> str:
        """Prepare additional fields for rendering if necessary and finally call generate_output"""
        additional_context = self.get_additional_context(component)
        return self.generate_output(component, additional_context)

    def get_additional_context(self, component: ComponentDataBase) -> dict[str, Any]:
        """Get additional fields for rendering context if necessary."""
        return {}

    def generate_output(
        self, component: ComponentDataBase, additional_context: dict
    ) -> str:
        """Generate output by defined strategy.

        If not overriden then JSON dump is performed
        """
        return component.model_dump_json()


class RendererStrategyBaseWithArrayValueFileds(RenderStrategyBase):
    """
    Render Base for components represented by ComponentDataBaseWithArrayValueFileds.
    Adds additional context info for rendering:
    * data_length - number - number of items in the data array
    * field_names - array of strings - names of the fields
    """

    @override
    def get_additional_context(self, component: ComponentDataBase) -> dict[str, Any]:
        """Get additional fields for rendering context extracted from ComponentDataBaseWithArrayValueFileds."""

        additional_context: dict[str, Any] = {}
        if isinstance(component, ComponentDataBaseWithArrayValueFileds):
            additional_context["data_length"] = max(
                len(field.data if isinstance(field.data, Sized) else [])
                for field in component.fields
            )
            additional_context["field_names"] = [
                field.name for field in component.fields
            ]

        return additional_context


class RendererContext:
    """Render performing rendering based for given strategy."""

    def __init__(self, strategy: RenderStrategyBase):
        self.render_strategy = strategy

    def render(self, component: ComponentDataBase):
        return self.render_strategy.render(component)


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
