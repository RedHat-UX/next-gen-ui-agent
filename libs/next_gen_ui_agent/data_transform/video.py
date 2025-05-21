from typing import Any

from next_gen_ui_agent.data_transform import data_transformer_utils
from next_gen_ui_agent.data_transform.data_transformer import DataTransformerBase
from next_gen_ui_agent.data_transform.types import (
    ComponentDataVideo,
    DataFieldSimpleValue,
)
from next_gen_ui_agent.types import UIComponentMetadata
from typing_extensions import override


class VideoPlayerDataTransformer(DataTransformerBase[ComponentDataVideo]):
    COMPONENT_NAME = "video-player"

    def __init__(self):
        self._component_data = ComponentDataVideo.model_construct()

    @override
    def main_processing(self, data: Any, component: UIComponentMetadata):
        fields: list[
            DataFieldSimpleValue
        ] = data_transformer_utils.copy_simple_fields_from_ui_component_metadata(
            component.fields
        )

        data_transformer_utils.fill_fields_with_simple_data(fields, data)

        # TODO: Use data_transformer_utils._find_field
        # TODO also search by video link suffixes, and by field names
        field_with_video_suffix = next(
            (
                field
                for field in fields
                for d in field.data
                if type(d) is str and "youtube.com" in d
            ),
            None,
        )
        if field_with_video_suffix:
            video = next(
                (
                    data
                    for data in field_with_video_suffix.data
                    if type(data) is str and "youtube.com" in data
                ),
                None,
            )
            video_img = ""
            if video and video.startswith("https://www.youtube.com/watch?v="):
                video_id = video.replace("https://www.youtube.com/watch?v=", "")
                video = f"https://www.youtube.com/embed/{video_id}"
                # https://img.youtube.com/vi/v-PjgYDrg70/maxresdefault.jpg
                video_img = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            if not video:
                raise ValueError("Cannot render video without the link")

            self._component_data.video = video
            self._component_data.video_img = video_img
