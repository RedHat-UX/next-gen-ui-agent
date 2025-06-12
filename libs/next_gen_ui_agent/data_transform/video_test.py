import pytest
from next_gen_ui_agent.data_transform.validation.types import (
    ComponentDataValidationError,
)
from next_gen_ui_agent.data_transform.video import VideoPlayerDataTransformer
from next_gen_ui_agent.types import InputData, UIComponentMetadata


def get_component(data_path="movie.trailerUrl") -> UIComponentMetadata:
    return UIComponentMetadata.model_validate(
        {
            "id": "test_id_1",
            "title": "Toy Story Details",
            "reasonForTheComponentSelection": "One item available in the data",
            "confidenceScore": "100%",
            "component": "image",
            "fields": [
                {"name": "Title", "data_path": "movie.title", "data": ["Toy Story"]},
                {"name": "Authors", "data_path": "NA", "data": ["A1", "A2", "A3"]},
                {"name": "Trailer", "data_path": data_path},
            ],
        }
    )


def get_data(videoUrl: str, video_field_name: str = "trailerUrl") -> InputData:
    data = InputData(
        id="test_id_1",
        data=f'{{ "movie": {{ "title": "Toy Story", "{video_field_name}": "{videoUrl}" }} }}',
    )
    return data


def test_process_not_found() -> None:
    result = VideoPlayerDataTransformer().process(
        get_component("movie.vvv"),
        get_data("https://redhat.com", "vvv"),
    )
    assert result.title == "Toy Story Details"
    assert result.video is None
    assert result.video_img is None


def test_invalid_url() -> None:
    with pytest.raises(ValueError) as excinfo:
        VideoPlayerDataTransformer().process(
            get_component(),
            get_data("httpssssss://www.youtube.com/watch?v=v-PjgYDrg70"),
        )
    assert (
        "Data value `httpssssss://www.youtube.com/watch?v=v-PjgYDrg70` is not valid URL link."
        in str(excinfo.value)
    )


@pytest.mark.parametrize(
    "videoUrl",
    [
        "https://www.youtube.com/watch?v=v-PjgYDrg70",
        "http://www.youtube.com/watch?v=v-PjgYDrg70",
        "https://www.youtube.be/watch?v=v-PjgYDrg70",
    ],
)
def test_process_youtube(videoUrl) -> None:
    # https://github.com/v2fly/domain-list-community/blob/master/data/youtube
    result = VideoPlayerDataTransformer().process(
        get_component(),
        get_data(videoUrl),
    )
    assert result.title == "Toy Story Details"
    assert result.video == "https://www.youtube.com/embed/v-PjgYDrg70"
    assert (
        result.video_img == "https://img.youtube.com/vi/v-PjgYDrg70/maxresdefault.jpg"
    )


@pytest.mark.parametrize(
    "videoUrl",
    [
        "https://youtu.be/v-PjgYDrg70",
        "https://youtu.be/v-PjgYDrg70?sid=1",
    ],
)
def test_process_youtube_shared_url(videoUrl) -> None:
    # https://github.com/v2fly/domain-list-community/blob/master/data/youtube
    result = VideoPlayerDataTransformer().process(
        get_component(),
        get_data(videoUrl),
    )
    assert result.title == "Toy Story Details"
    assert result.video == "https://www.youtube.com/embed/v-PjgYDrg70"
    assert (
        result.video_img == "https://img.youtube.com/vi/v-PjgYDrg70/maxresdefault.jpg"
    )


def test_process_by_field() -> None:
    # https://github.com/v2fly/domain-list-community/blob/master/data/youtube
    result = VideoPlayerDataTransformer().process(
        get_component("movie.videourl"),
        get_data("https://www.youuuuutube.com/watch?v=v-PjgYDrg70", "videourl"),
    )
    assert result.video == "https://www.youuuuutube.com/watch?v=v-PjgYDrg70"
    assert result.video_img is None


def test_validate_OK() -> None:
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_id_1",
            "title": "Toy Story Details",
            "component": "image",
            "fields": [
                {"name": "Title", "data_path": "movie.title"},
                {"name": "Trailer", "data_path": "movie.trailerUrl"},
            ],
        }
    )
    data = InputData(
        id="test_id_1",
        data='{"movie": {"title": "Toy Story", "trailerUrl": "https://www.youtube.com/watch?v=v-PjgYDrg70"}}',
    )
    errors: list[ComponentDataValidationError] = []
    VideoPlayerDataTransformer().validate(c, data, errors)
    assert len(errors) == 0


def test_validate_NO_IMAGE_FILED_FROM_LLM() -> None:
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_id_1",
            "title": "Toy Story Details",
            "component": "image",
            "fields": [
                {"name": "Title", "data_path": "movie.title"},
            ],
        }
    )
    data = InputData(
        id="test_id_1",
        data='{"movie": {"title": "Toy Story", "trailerUrl": "https://www.youtube.com/watch?v=v-PjgYDrg70"}}',
    )
    errors: list[ComponentDataValidationError] = []
    VideoPlayerDataTransformer().validate(c, data, errors)
    assert len(errors) == 1
    assert errors[0].code == "video.missing"
    assert errors[0].message == "Video URL is missing"
