from next_gen_ui_agent.data_transform.types import ComponentDataImage
from next_gen_ui_agent.renderer.image import ImageRenderStrategy


def test_render_json_output() -> None:
    strategy = ImageRenderStrategy()
    c = ComponentDataImage.model_validate(
        {
            "id": "test_id_1",
            "image": "https://image.tmdb.org/test_path.jpg",
            "title": "Toy Story Poster",
            "component": "image",
        }
    )
    resultStr = strategy.generate_output(c)
    # print(resultStr)
    assert resultStr == c.model_dump_json()
