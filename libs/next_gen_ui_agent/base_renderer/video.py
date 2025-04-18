from next_gen_ui_agent.base_renderer.base_renderer import RenderStrategyBase
from next_gen_ui_agent.base_renderer.types import RenderContextVideo
from next_gen_ui_agent.types import UIComponentMetadata


class VideoRenderStrategy(RenderStrategyBase[RenderContextVideo]):
    COMPONENT_NAME = "video-player"

    def main_processing(self, component: UIComponentMetadata):
        fields = component["fields"]

        # TODO: Use super()._find_field
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
