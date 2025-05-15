from typing import Any

from next_gen_ui_agent.data_transform.data_transformer import DataTransformerBase
from next_gen_ui_agent.data_transform.types import IMAGE_SUFFIXES, ComponentDataAudio
from next_gen_ui_agent.types import UIComponentMetadata


class AudioPlayerDataTransformer(DataTransformerBase[ComponentDataAudio]):
    COMPONENT_NAME = "audio-player"

    def __init__(self):
        self._component_data = ComponentDataAudio.model_construct()

    def main_processing(self, component: UIComponentMetadata, data: Any):
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
                self._component_data.image = image

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
                self._component_data.audio = audio

        if not audio:
            # We cannot render video without the link
            raise ValueError("Cannot render video without the link")
