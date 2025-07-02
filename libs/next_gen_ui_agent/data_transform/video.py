import logging
from typing import Any

from next_gen_ui_agent.data_transform import data_transformer_utils
from next_gen_ui_agent.data_transform.data_transformer import DataTransformerBase
from next_gen_ui_agent.data_transform.types import (
    VIDEO_DATA_PATH_SUFFIXES,
    ComponentDataVideo,
    DataFieldSimpleValue,
)
from next_gen_ui_agent.data_transform.validation.assertions import is_url_http
from next_gen_ui_agent.data_transform.validation.types import (
    ComponentDataValidationError,
)
from next_gen_ui_agent.types import InputData, UIComponentMetadata
from typing_extensions import override

logger = logging.getLogger(__name__)


def find_video_value_and_field(
    fields: list[DataFieldSimpleValue],
    value_str: str,
) -> tuple[str, DataFieldSimpleValue] | tuple[None, None]:
    """Find video field with video. Return tuple with data value and DataField"""
    field = data_transformer_utils.find_field_by_simple_data_value(
        fields,
        lambda data: isinstance(data, str) and value_str in data.lower(),
    )
    if field:
        video_value = data_transformer_utils.find_simple_data_value_in_field(
            field.data,
            lambda value: isinstance(value, str) and value_str in value.lower(),
        )
        if video_value and is_url_http(str(video_value)):
            return str(video_value), field
        else:
            raise ValueError(f"Data value `{video_value}` is not valid URL link.")

    return None, None


class VideoPlayerDataTransformer(DataTransformerBase[ComponentDataVideo]):
    COMPONENT_NAME = "video-player"
    YOUTUBE = ".youtube."  # https://github.com/v2fly/domain-list-community/blob/master/data/youtube
    YOUTUBE_SHARE = "youtu.be"  # https://github.com/v2fly/domain-list-community/blob/master/data/youtube

    def __init__(self):
        self._component_data = ComponentDataVideo.model_construct()

    @override
    def main_processing(self, data: Any, component: UIComponentMetadata):
        fields = data_transformer_utils.copy_simple_fields_from_ui_component_metadata(
            component.fields
        )

        data_transformer_utils.fill_fields_with_simple_data(fields, data)

        # YOUTUBE
        video_url, _field = find_video_value_and_field(fields, self.YOUTUBE)
        if video_url:
            video_id = video_url[video_url.find("/watch?v=") + 9 :]
            video_url = f"https://www.youtube.com/embed/{video_id}"
            # https://img.youtube.com/vi/v-PjgYDrg70/maxresdefault.jpg
            self._component_data.video_img = (
                f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            )
        if not video_url:
            # Youtube Share
            video_url, _field = find_video_value_and_field(fields, self.YOUTUBE_SHARE)
            if video_url:
                if "?" in video_url:
                    video_url = video_url[0 : video_url.find("?")]
                video_id = video_url[video_url.find("youtu.be/") + 9 :]
                video_url = f"https://www.youtube.com/embed/{video_id}"
                # https://img.youtube.com/vi/v-PjgYDrg70/maxresdefault.jpg
                self._component_data.video_img = (
                    f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                )

        if not video_url:
            # not found by video url, so try to find by field name suffix
            field_name_like_url = (
                data_transformer_utils.find_simple_value_field_by_data_path(
                    fields,
                    lambda name: name.lower().endswith(VIDEO_DATA_PATH_SUFFIXES),
                )
            )
            if (
                field_name_like_url
                and len(field_name_like_url.data) > 0
                and is_url_http(str(field_name_like_url.data[0]))
            ):
                video_url = str(field_name_like_url.data[0])

        if not video_url:
            logger.warning("No video url found in Video Component")
            self._component_data.video = None
            self._component_data.video_img = None
        else:
            self._component_data.video = str(video_url)

    @override
    def validate(
        self,
        component: UIComponentMetadata,
        data: InputData,
        errors: list[ComponentDataValidationError],
    ) -> ComponentDataVideo:
        ret = super().validate(component, data, errors)

        video_url = self._component_data.video

        if video_url:
            if not is_url_http(video_url):
                errors.append(
                    ComponentDataValidationError(
                        "video.invalidUrl",
                        f"Video URL '{video_url}' is not a valid URL",
                    )
                )
        else:
            errors.append(
                ComponentDataValidationError("video.missing", "Video URL is missing")
            )
        return ret
