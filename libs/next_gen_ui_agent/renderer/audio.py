from next_gen_ui_agent.renderer.base_renderer import RenderStrategyBase
from next_gen_ui_agent.renderer.types import IMAGE_SUFFIXES, RenderContextAudio
from next_gen_ui_agent.types import UIComponentMetadata


class AudioPlayerRenderStrategy(RenderStrategyBase[RenderContextAudio]):
    COMPONENT_NAME = "audio-player"

    def __init__(self):
        self._rendering_context = RenderContextAudio.model_construct()

    def main_processing(self, component: UIComponentMetadata):
        fields = component.fields

        # TODO: Use super()._find_field
        field_with_image_suffix = next(
            (
                field
                for field in fields
                for d in field.data
                if type(d) is str and d.endswith(IMAGE_SUFFIXES)
            ),
            None,
        )
        if field_with_image_suffix:
            image = next(
                (
                    data
                    for data in field_with_image_suffix.data
                    if type(data) is str and data.endswith(IMAGE_SUFFIXES)
                ),
                None,
            )
            if image:
                self._rendering_context.image = image

        field_with_audio_suffix = next(
            (
                field
                for field in fields
                for d in field.data
                if type(d) is str and d.endswith(".mp3")
            ),
            None,
        )
        if field_with_audio_suffix:
            audio = next(
                (
                    data
                    for data in field_with_audio_suffix.data
                    if type(data) is str and data.endswith(".mp3")
                ),
                None,
            )
            if audio:
                self._rendering_context.audio = audio

        if not audio:
            # We cannot render video without the link
            raise ValueError("Cannot render video without the link")
