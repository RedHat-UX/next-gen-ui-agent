from abc import ABC, ABCMeta, abstractmethod
from typing import Callable, Generic, Sized, TypeVar

from next_gen_ui_agent.renderer.types import (
    IMAGE_SUFFIXES,
    RenderContexSetOfCard,
    RenderContextAudio,
    RenderContextBase,
    RenderContextImage,
    RenderContextOneCard,
    RenderContextVideo,
)
from next_gen_ui_agent.types import DataField, DataFieldDataType, UIComponentMetadata

PLUGGABLE_RENDERERS_NAMESPACE = "next_gen_ui.agent.renderer_factory"


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
        self._rendering_context.title = component.title
        self._rendering_context.id = component.id  # type: ignore
        if isinstance(self._rendering_context, RenderContextBase):
            self._rendering_context.fields = fields.copy()
            self._rendering_context.data_length = max(
                len(field.data if isinstance(field.data, Sized) else [])
                for field in fields
            )
            self._rendering_context.field_names = [field.name for field in fields]

    def main_processing(self, component: UIComponentMetadata):
        pass

    def post_processing(self, component: UIComponentMetadata):
        if isinstance(self._rendering_context, RenderContextBase):
            fields = self._rendering_context.fields
            self._rendering_context.field_names = [field.name for field in fields]

    def process(self, component: UIComponentMetadata) -> T:
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
    def find_field_by_data_value(
        fields: list[DataField],
        field_data_predicate: Callable[[DataFieldDataType], bool],
    ) -> DataField | None:
        """Helper methods for to find field based on predicate."""
        return next(
            (field for field in fields for d in field.data if field_data_predicate(d)),
            None,
        )

    @staticmethod
    def find_field_by_data_path(
        fields: list[DataField],
        data_path_predicate: Callable[[str], bool],
    ) -> DataField | None:
        """Helper methods for to find field based on its data_path predicate. Predicate's argument is lowered field `data_path`"""
        return next(
            (
                field
                for field in fields
                if field.data_path and data_path_predicate(field.data_path.lower())
            ),
            None,
        )

    @staticmethod
    def find_data_value_in_field(
        items: list[DataFieldDataType],
        data_value_predicate: Callable[[DataFieldDataType], bool],
    ) -> DataFieldDataType | None:
        """Helper methods for to find field data value based on predicate."""
        return next(
            (value for value in items if data_value_predicate(value)),
            None,
        )

    @staticmethod
    def find_image(
        component: UIComponentMetadata,
    ) -> tuple[str, DataField] | tuple[None, None]:
        """Find image field with image. Return tuple with data value and DataField"""
        fields = component.fields
        field_with_image_suffix = RenderStrategyBase.find_field_by_data_value(
            fields,
            lambda data: isinstance(data, str) and data.endswith(IMAGE_SUFFIXES),
        )
        if field_with_image_suffix:
            image = RenderStrategyBase.find_data_value_in_field(
                field_with_image_suffix.data,
                lambda value: isinstance(value, str) and value.endswith(IMAGE_SUFFIXES),
            )
            if image:
                return str(image), field_with_image_suffix
        else:
            field_name_like_url = RenderStrategyBase.find_field_by_data_path(
                fields,
                lambda name: name.endswith("link") or name.endswith("url"),
            )
            if field_name_like_url and len(field_name_like_url.data) > 0:
                return str(field_name_like_url.data[0]), field_name_like_url

        return None, None


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
