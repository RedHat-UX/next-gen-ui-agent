import pytest
from next_gen_ui_agent.renderer.image import ImageRenderStrategy
from next_gen_ui_agent.types import UIComponentMetadata


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


@pytest.mark.parametrize("extension", testdata)
def test_process(extension) -> None:
    result = ImageRenderStrategy().process(get_component(extension))
    assert result.title == "Toy Story Details"
    assert result.image == "https://image.tmdb.org/test_path" + extension


def test_image_extension_invalid() -> None:
    result = ImageRenderStrategy().process(
        get_component("txt", data_path="movie.title")
    )
    assert result.title == "Toy Story Details"
    assert result.image is None


@pytest.mark.parametrize("data_path", [("UrL"), ("LinK")])
def test_field_path_url_like(data_path) -> None:
    result = ImageRenderStrategy().process(
        get_component("_no_extension", data_path=data_path)
    )
    assert result.title == "Toy Story Details"
    assert result.image == "https://image.tmdb.org/test_path_no_extension"
