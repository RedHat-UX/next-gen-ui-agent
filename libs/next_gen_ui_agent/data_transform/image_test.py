import pytest
from next_gen_ui_agent.data_transform.image import ImageDataTransformer
from next_gen_ui_agent.data_transform.validation.types import (
    ComponentDataValidationError,
)
from next_gen_ui_agent.types import InputData, UIComponentMetadata


def get_component(extension: str, data_path="movie.posterUrl") -> UIComponentMetadata:
    return UIComponentMetadata.model_validate(
        {
            "id": "test_id_1",
            "title": "Toy Story Details",
            "reasonForTheComponentSelection": "One item available in the data",
            "confidenceScore": "100%",
            "component": "image",
            "fields": [
                {"name": "Title", "data_path": "movie.title"},
                {"name": "Authors", "data_path": "movie.authors"},
                {"name": "Poster", "data_path": data_path},
            ],
        }
    )


testdata = [(".jpg"), (".jpeg"), (".png"), (".webp"), (".tiff")]


def get_data(extension: str, image_field="posterUrl") -> InputData:
    data = InputData(
        id="test_id_1",
        data=f'{{ "movie": {{ "title": "Toy Story", "authors": ["A1", "A2", "A3"], "{image_field}": "https://image.tmdb.org/test_path{extension}" }} }}',
    )
    return data


@pytest.mark.parametrize("extension", testdata)
def test_process(extension) -> None:
    result = ImageDataTransformer().process(
        get_component(extension), get_data(extension)
    )
    assert result.title == "Toy Story Details"
    assert result.image == "https://image.tmdb.org/test_path" + extension


def test_image_extension_invalid() -> None:
    result = ImageDataTransformer().process(
        get_component("txt", data_path="movie.title"), get_data("txt")
    )
    assert result.title == "Toy Story Details"
    assert result.image is None


@pytest.mark.parametrize("data_path", [("imageUrL"), ("thumbnailLinK")])
def test_field_path_url_like(data_path) -> None:
    result = ImageDataTransformer().process(
        get_component("_no_extension", data_path=data_path),
        get_data("_no_extension", image_field=data_path),
    )
    assert result.title == "Toy Story Details"
    assert result.image is None


def test_validate_OK() -> None:
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_id_1",
            "title": "Toy Story Details",
            "component": "image",
            "fields": [
                {"name": "Title", "data_path": "movie.title"},
                {"name": "Poster", "data_path": "movie.posterUrl"},
            ],
        }
    )
    data = InputData(
        id="test_id_1",
        data='{"movie": {"title": "Toy Story", "posterUrl": "https://image.tmdb.org/test_path.jpg"}}',
    )
    errors: list[ComponentDataValidationError] = []
    ImageDataTransformer().validate(c, data, errors)
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
        data='{"movie": {"title": "Toy Story", "posterUrl": "image.tmdb.org/test_path.jpg"}}',
    )
    errors: list[ComponentDataValidationError] = []
    ImageDataTransformer().validate(c, data, errors)
    assert len(errors) == 1
    assert errors[0].code == "image.missing"
    assert errors[0].message == "Image URL is missing"


def test_validate_NO_IMAGE_VALID_URL() -> None:
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_id_1",
            "title": "Toy Story Details",
            "component": "image",
            "fields": [
                {"name": "Title", "data_path": "movie.title"},
                {"name": "Poster", "data_path": "movie.posterUrl"},
            ],
        }
    )
    data = InputData(
        id="test_id_1",
        data='{"movie": {"title": "Toy Story", "posterUrl": "image.tmdb.org/test_path.jpg"}}',
    )
    errors: list[ComponentDataValidationError] = []
    ImageDataTransformer().validate(c, data, errors)
    assert len(errors) == 1
    assert errors[0].code == "image.missing"
    assert errors[0].message == "Image URL is missing"
