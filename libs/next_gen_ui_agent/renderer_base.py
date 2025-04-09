import json
from abc import ABC, ABCMeta, abstractmethod
from typing import Generic, Sized, TypeVar

from .types import (
    RenderContexSetOfCard,
    RenderContextAudio,
    RenderContextBase,
    RenderContextImage,
    RenderContextOneCard,
    RenderContextVideo,
    UIComponentMetadata,
)

IMAGE_SUFFIXES = ("jpg", "png", "gif", "jpeg", "bmp")
PLUGGABLE_RENDERERS_NAMESPACE = "next_gen_ui.agent.renderer_factory"


T = TypeVar(
    "T",
    RenderContextBase,
    RenderContextOneCard,
    RenderContexSetOfCard,
    RenderContextImage,
    RenderContextVideo,
    RenderContextAudio,
)


class GenericRenderStrategy(ABC, Generic[T]):
    """Base class for rendering with Generic Type of the context."""


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


class OneCardRenderStrategy(RenderStrategyBase[RenderContextOneCard]):
    def main_processing(self, component: UIComponentMetadata):
        # Trying to find field that would contain an image link
        fields = component["fields"]

        field_with_image_suffix = next(
            (
                field
                for field in fields
                for d in field["data"]
                if type(d) is str and d.endswith(IMAGE_SUFFIXES)
            ),
            None,
        )
        if field_with_image_suffix:
            image = next(
                (
                    data
                    for data in field_with_image_suffix["data"]
                    if type(data) is str and data.endswith(IMAGE_SUFFIXES)
                ),
                None,
            )
            if image:
                self._rendering_context["image"] = image
                self._rendering_context["fields"].remove(field_with_image_suffix)


class TableRenderStrategy(RenderStrategyBase):
    pass


# TODO: Not yet implemented
class PieChartRenderStrategy(RenderStrategyBase):
    pass


# TODO: Not yet implemented
class LineChartRenderStrategy(RenderStrategyBase):
    pass


class SetOfCardsRenderStrategy(RenderStrategyBase[RenderContexSetOfCard]):
    def main_processing(self, component: UIComponentMetadata):
        subtitle_field = next(
            (
                field
                for field in component["fields"]
                if field["name"].lower() in ["title", "name", "header"]
            ),
            None,
        )
        if subtitle_field:
            self._rendering_context["subtitle_field"] = subtitle_field
            self._rendering_context["fields"].remove(subtitle_field)

        image_field = next(
            (
                field
                for field in component["fields"]
                for d in field["data"]
                if type(d) is str and d.endswith(IMAGE_SUFFIXES)
            ),
            None,
        )
        if image_field:
            self._rendering_context["image_field"] = image_field
            self._rendering_context["fields"].remove(image_field)


class ImageRenderStrategy(RenderStrategyBase[RenderContextImage]):
    def main_processing(self, component: UIComponentMetadata):
        # Trying to find field that would contain an image link
        fields = component["fields"]

        field_with_image_suffix = next(
            (
                field
                for field in fields
                for d in field["data"]
                if type(d) is str and d.endswith(IMAGE_SUFFIXES)
            ),
            None,
        )
        if field_with_image_suffix:
            image = next(
                (
                    data
                    for data in field_with_image_suffix["data"]
                    if type(data) is str and data.endswith(IMAGE_SUFFIXES)
                ),
                None,
            )
            if image:
                self._rendering_context["image"] = image
                self._rendering_context["fields"].remove(field_with_image_suffix)


class VideoRenderStrategy(RenderStrategyBase[RenderContextVideo]):
    def main_processing(self, component: UIComponentMetadata):
        fields = component["fields"]

        field_with_video_suffix = next(
            (
                field
                for field in fields
                for d in field["data"]
                if type(d) is str and "youtube.com" in d
            ),
            None,
        )
        if field_with_video_suffix:
            video = next(
                (
                    data
                    for data in field_with_video_suffix["data"]
                    if type(data) is str and "youtube.com" in data
                ),
                None,
            )
            video_img = "https://fakeimg.pl/900x499/282828/eae0d0"
            if video and video.startswith("https://www.youtube.com/watch?v="):
                video_id = video.replace("https://www.youtube.com/watch?v=", "")
                video = f"https://www.youtube.com/embed/{video_id}"
                # https://img.youtube.com/vi/v-PjgYDrg70/maxresdefault.jpg
                video_img = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            if not video:
                raise ValueError("Cannot render video without the link")

            self._rendering_context["video"] = video
            self._rendering_context["video_img"] = video_img
            self._rendering_context["fields"].remove(field_with_video_suffix)


class AudioPlayerRenderStrategy(RenderStrategyBase[RenderContextAudio]):
    def main_processing(self, component: UIComponentMetadata):
        fields = component["fields"]

        field_with_image_suffix = next(
            (
                field
                for field in fields
                for d in field["data"]
                if type(d) is str and d.endswith(IMAGE_SUFFIXES)
            ),
            None,
        )
        if field_with_image_suffix:
            image = next(
                (
                    data
                    for data in field_with_image_suffix["data"]
                    if type(data) is str and data.endswith(IMAGE_SUFFIXES)
                ),
                None,
            )
            if image:
                self._rendering_context["image"] = image
                self._rendering_context["fields"].remove(field_with_image_suffix)

        field_with_audio_suffix = next(
            (
                field
                for field in fields
                for d in field["data"]
                if type(d) is str and d.endswith(".mp3")
            ),
            None,
        )
        if field_with_audio_suffix:
            audio = next(
                (
                    data
                    for data in field_with_audio_suffix["data"]
                    if type(data) is str and data.endswith(".mp3")
                ),
                None,
            )
            if audio:
                self._rendering_context["audio"] = audio
                self._rendering_context["fields"].remove(field_with_audio_suffix)

        if not audio:
            # We cannot render video without the link
            raise ValueError("Cannot render video without the link")


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
