from next_gen_ui_agent.renderer.one_card import OneCardRenderStrategy
from next_gen_ui_agent.types import UIComponentMetadata


def test_image():
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
    strategy.preprocess_rendering_context(c)
    strategy.main_processing(c)
    assert (
        strategy._rendering_context["image"]
        == "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg"
    )
    # TODO: Check that fields does not contain image
