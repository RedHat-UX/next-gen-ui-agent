from next_gen_ui_agent.data_transform.types import ComponentDataOneCard
from next_gen_ui_agent.renderer.one_card import OneCardRenderStrategy


def test_process() -> None:
    c = ComponentDataOneCard.model_validate(
        {
            "id": "test_id_1",
            "title": "Toy Story Details",
            "component": "one-card",
            "fields": [
                {"name": "Title", "data_path": "movie.title", "data": ["Toy Story"]},
                {"name": "Authors", "data_path": "NA", "data": ["A1", "A2", "A3"]},
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
    result = OneCardRenderStrategy().generate_output(c)
    assert result == c.model_dump_json()
