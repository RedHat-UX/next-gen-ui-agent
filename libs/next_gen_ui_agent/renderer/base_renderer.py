from abc import ABC, ABCMeta, abstractmethod
from typing import Callable, Generic, Sized, TypeVar

from next_gen_ui_agent.renderer.types import (
    RenderContexSetOfCard,
    RenderContextAudio,
    RenderContextBase,
    RenderContextImage,
    RenderContextOneCard,
    RenderContextVideo,
)
from next_gen_ui_agent.types import DataField, DataFieldDataType, UIComponentMetadata

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
        self._rendering_context: T = None

    def preprocess_rendering_context(self, component: UIComponentMetadata):
        fields = component.fields
        self._rendering_context.fields = fields.copy()
        self._rendering_context.title = component.title
        self._rendering_context.data_length = max(
            len(field.data if isinstance(field.data, Sized) else []) for field in fields
        )
        self._rendering_context.field_names = [field.name for field in fields]

    def main_processing(self, component: UIComponentMetadata):
        pass

    def post_processing(self, component: UIComponentMetadata):
        fields = self._rendering_context.fields
        self._rendering_context.field_names = [field.name for field in fields]

    def process(self, component) -> T:
        """Transform the component into strategy component via running pre-
        main-post processing flow."""
        self.preprocess_rendering_context(component)
        self.main_processing(component)
        self.post_processing(component)
        return self._rendering_context

    def generate_output(self, component: UIComponentMetadata) -> str:
        """Generate output by defined strategy.

        If not overriden then JSON dump is performed
        """
        return self._rendering_context.model_dump_json()

    def render(self, component: UIComponentMetadata) -> str:
        self.process(component)
        return self.generate_output(component)

    @staticmethod
    def find_field(
        fields: list[DataField],
        fieldFieldPredicate: Callable[[DataFieldDataType], bool],
    ) -> DataField | None:
        """Helper methods for to find field based on predicate."""
        return next(
            (field for field in fields for d in field.data if fieldFieldPredicate(d)),
            None,
        )

    @staticmethod
    def find_field_data_value(
        items: list[DataFieldDataType],
        fieldDataPredicate: Callable[[DataFieldDataType], bool],
    ) -> DataFieldDataType | None:
        """Helper methods for to find field data value based on predicate."""
        return next(
            (data for data in items if fieldDataPredicate(data)),
            None,
        )


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
