from typing import Any

from next_gen_ui_agent.data_transform import data_transformer_utils
from next_gen_ui_agent.data_transform.data_transformer import DataTransformerBase
from next_gen_ui_agent.data_transform.types import (
    ComponentDataAudio,
    DataFieldSimpleValue,
)
from next_gen_ui_agent.types import UIComponentMetadata
from typing_extensions import override


class AudioPlayerDataTransformer(DataTransformerBase[ComponentDataAudio]):
    COMPONENT_NAME = "audio-player"

    def __init__(self):
        self._component_data = ComponentDataAudio.model_construct()

    @override
    def main_processing(self, json_data: Any, component: UIComponentMetadata):
        fields: list[
            DataFieldSimpleValue
        ] = data_transformer_utils.copy_simple_fields_from_ui_component_metadata(
            component.fields
        )
        data_transformer_utils.fill_fields_with_simple_data(fields, json_data)

        image, _f = data_transformer_utils.find_image(fields)
        if image:
            self._component_data.image = str(image)

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
            self._component_data.audio = str(field_with_audio_suffix.data)
        # TODO search by field name and make sure it contains url
        else:
            # We cannot render video without the link
            raise ValueError("Cannot render audio without the link")
