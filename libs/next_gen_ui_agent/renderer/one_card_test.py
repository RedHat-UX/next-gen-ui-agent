import json

from next_gen_ui_agent.renderer.one_card import OneCardRenderStrategy
from next_gen_ui_agent.renderer.types import RenderContextOneCard
from next_gen_ui_agent.types import UIComponentMetadata


def test_process():
    strategy = OneCardRenderStrategy()
    c = UIComponentMetadata(
        {
            "id": "test_id_1",
            "title": "Toy Story Details",
            "reasonForTheComponentSelection": "One item available in the data",
            "confidenceScore": "100%",
            "component": "one-card",
            "fields": [
                {"name": "Title", "data_path": "movie.title", "data": ["Toy Story"]},
                {
                    "name": "Poster",
                    "data_path": "movie.posterUrl",
                    "data": [
                        "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg"
                    ],
                },
            ],
        }
    )
    result = strategy.process(c)
    assert result["title"] == "Toy Story Details"
    assert (
        result["image"]
        == "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg"
    )
    assert len(result["fields"]) == 1
    assert result["fields"][0]["name"] == "Title"


def test_process_no_image():
    strategy = OneCardRenderStrategy()
    c = UIComponentMetadata(
        {
            "id": "test_id_1",
            "title": "Toy Story Details",
            "reasonForTheComponentSelection": "One item available in the data",
            "confidenceScore": "100%",
            "component": "one-card",
            "fields": [
                {"name": "Title", "data_path": "movie.title", "data": ["Toy Story"]},
            ],
        }
    )
    result = strategy.process(c)
    assert result["title"] == "Toy Story Details"
    assert "image" not in result
    assert len(result["fields"]) == 1
    assert result["fields"][0]["name"] == "Title"


def test_render_json():
    strategy = OneCardRenderStrategy()
    c = UIComponentMetadata(
        {
            "id": "test_id_1",
            "title": "Toy Story Details",
            "reasonForTheComponentSelection": "One item available in the data",
            "confidenceScore": "100%",
            "component": "one-card",
            "fields": [
                {"name": "Title", "data_path": "movie.title", "data": ["Toy Story"]},
                {
                    "name": "Poster",
                    "data_path": "movie.posterUrl",
                    "data": [
                        "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg"
                    ],
                },
            ],
        }
    )
    resultStr = strategy.render(c)
    result: RenderContextOneCard = json.loads(resultStr)
    assert (
        result["image"]
        == "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg"
    )
    assert len(result["fields"]) == 1
    assert len(result["field_names"]) == 1
