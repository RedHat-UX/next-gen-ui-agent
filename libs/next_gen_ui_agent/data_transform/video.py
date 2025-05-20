from typing import Any

from next_gen_ui_agent.data_transform.data_transformer import DataTransformerBase
from next_gen_ui_agent.data_transform.types import ComponentDataVideo
from next_gen_ui_agent.types import UIComponentMetadata


class VideoPlayerDataTransformer(DataTransformerBase[ComponentDataVideo]):
    COMPONENT_NAME = "video-player"

    def __init__(self):
        self._component_data = ComponentDataVideo.model_construct()

    def main_processing(self, component: UIComponentMetadata, data: Any):
        fields = component.fields

        # TODO: Use super()._find_field
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
            video_img = "https://fakeimg.pl/900x499/282828/eae0d0"
            if video and video.startswith("https://www.youtube.com/watch?v="):
                video_id = video.replace("https://www.youtube.com/watch?v=", "")
                video = f"https://www.youtube.com/embed/{video_id}"
                # https://img.youtube.com/vi/v-PjgYDrg70/maxresdefault.jpg
                video_img = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            if not video:
                raise ValueError("Cannot render video without the link")

            self._component_data.video = video
            self._component_data.video_img = video_img
