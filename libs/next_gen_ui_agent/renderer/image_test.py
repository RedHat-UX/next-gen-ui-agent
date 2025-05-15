import pytest
from next_gen_ui_agent.data_transform.types import ComponentDataImage
from next_gen_ui_agent.renderer.image import ImageRenderStrategy


def get_component(extension: str, data_path="movie.posterUrl") -> ComponentDataImage:
    return ComponentDataImage.model_validate(
        {
            "id": "test_id_1",
            "title": "Toy Story Details",
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
            "image": "https://image.tmdb.org/test_path" + extension,
        }
    )


testdata = [(".jpg"), (".jpeg"), (".png"), (".webp"), (".tiff")]


@pytest.mark.parametrize("extension", testdata)
def test_generate_output(extension) -> None:
    component = get_component(extension)
    result = ImageRenderStrategy().generate_output(component)
    assert result == component.model_dump_json()
