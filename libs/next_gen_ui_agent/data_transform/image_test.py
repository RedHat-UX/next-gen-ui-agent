import pytest
from next_gen_ui_agent.data_transform.image import ImageDataTransformer
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
                {"name": "Title", "data_path": "movie.title", "data": ["Toy Story"]},
                {"name": "Authors", "data_path": "NA", "data": ["A1", "A2", "A3"]},
                {
                    "name": "Poster",
                    "data_path": data_path,
                    "data": ["https://image.tmdb.org/test_path" + extension],
                },
            ],
        }
    )


testdata = [(".jpg"), (".jpeg"), (".png"), (".webp"), (".tiff")]


def get_data(extension: str) -> InputData:
    data = InputData(
        id="test_id_1",
        data=f'{{ "movie": {{ "title": "Toy Story", "posterUrl": "https://image.tmdb.org/test_path{extension}" }} }}',
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


@pytest.mark.parametrize("data_path", [("UrL"), ("LinK")])
def test_field_path_url_like(data_path) -> None:
    result = ImageDataTransformer().process(
        get_component("_no_extension", data_path=data_path), get_data("txt")
    )
    assert result.title == "Toy Story Details"
    assert result.image == "https://image.tmdb.org/test_path_no_extension"
