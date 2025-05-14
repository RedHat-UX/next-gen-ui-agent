from next_gen_ui_agent.renderer.image import ImageRenderStrategy
from next_gen_ui_agent.types import UIComponentMetadata


def test_render_json_output() -> None:
    strategy = ImageRenderStrategy()
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_id_1",
            "title": "Toy Story Poster",
            "reasonForTheComponentSelection": "One item available in the data",
            "confidenceScore": "100%",
            "component": "image",
            "fields": [
                {"name": "Title", "data_path": "movie.title", "data": ["Toy Story"]},
                {"name": "Authors", "data_path": "NA", "data": ["A1", "A2", "A3"]},
                {
                    "name": "Poster",
                    "data_path": "movie.posterUrl",
                    "data": ["https://image.tmdb.org/test_path.jpg"],
                },
            ],
        }
    )
    resultStr = strategy.render(c)
    # print(resultStr)
    assert (
        resultStr
        == """{"component":"image","image":"https://image.tmdb.org/test_path.jpg","title":"Toy Story Poster"}"""
    )
