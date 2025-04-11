import json
from abc import ABC, ABCMeta, abstractmethod
from typing import Generic, Sized, TypeVar

from next_gen_ui_agent.renderer.types import (
    RenderContexSetOfCard,
    RenderContextAudio,
    RenderContextBase,
    RenderContextImage,
    RenderContextOneCard,
    RenderContextVideo,
)
from next_gen_ui_agent.types import UIComponentMetadata

PLUGGABLE_RENDERERS_NAMESPACE = "next_gen_ui.agent.renderer_factory"
IMAGE_SUFFIXES = ("jpg", "png", "gif", "jpeg", "bmp")


T = TypeVar(
    "T",
    RenderContextBase,
    RenderContextAudio,
    RenderContextImage,
    RenderContextOneCard,
    RenderContexSetOfCard,
    RenderContextVideo,
)


class RenderStrategyBase(ABC, Generic[T]):
    """Renderer Base."""

    def __init__(self):
        self._rendering_context: T = RenderContextBase()

    def preprocess_rendering_context(self, component: UIComponentMetadata):
        fields = component["fields"]
        self._rendering_context["fields"] = fields.copy()
        self._rendering_context["title"] = component["title"]
        self._rendering_context["data_length"] = max(
            len(field["data"] if isinstance(field["data"], Sized) else [])
            for field in fields
        )
        self._rendering_context["field_names"] = [field["name"] for field in fields]

    def main_processing(self, component: UIComponentMetadata):
        pass

    def generate_output(self, component: UIComponentMetadata) -> str:
        return json.dumps(component)

    def render(self, component: UIComponentMetadata) -> str:
        self.preprocess_rendering_context(component)
        self.main_processing(component)
        return self.generate_output(component)


class RendererContext:
    """Render performing rendering based for given strategy."""

    def __init__(self, strategy: RenderStrategyBase):
        self.render_strategy = strategy

    def render(self, component: UIComponentMetadata):
        return self.render_strategy.render(component)


class StrategyFactory(metaclass=ABCMeta):
    """Abstract Strategy Factory Base."""

    @abstractmethod
    def get_render_strategy(self, component: UIComponentMetadata) -> RenderStrategyBase:
        raise NotImplementedError(
            "Renderer Strategy has to implement get_render_strategy method"
        )
