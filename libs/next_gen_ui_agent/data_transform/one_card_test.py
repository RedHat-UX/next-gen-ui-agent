from next_gen_ui_agent.data_transform.one_card import OneCardDataTransformer
from next_gen_ui_agent.types import InputData, UIComponentMetadata


def test_process() -> None:
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_id_1",
            "title": "Toy Story Details",
            "component": "one-card",
            "fields": [
                {"name": "Title", "data_path": "movie.title", "data": ["Toy Story"]},
                {
                    "name": "Authors",
                    "data_path": "movie.authors",
                    "data": ["A1", "A2", "A3"],
                },
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
    data = InputData(
        id="test_id_1",
        data="""[
            {
                "movie": {
                    "title": "Toy Story",
                    "posterUrl": "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
                    "authors": ["A1", "A2", "A3"]
                }
            }
        ]""",
    )
    result = OneCardDataTransformer().process(c, data)
    assert result.title == "Toy Story Details"
    assert len(result.fields) == 2
    assert result.fields[0].name == "Title"
    assert result.fields[0].data == ["Toy Story"]
    assert result.fields[1].name == "Authors"
    assert result.fields[1].data == ["A1", "A2", "A3"]
    assert (
        result.image
        == "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg"
    )


def test_process_no_image() -> None:
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_id_1",
            "title": "Toy Story Details",
            "component": "one-card",
            "fields": [
                {"name": "Title", "data_path": "movie.title", "data": ["Toy Story"]},
            ],
        }
    )
    data = InputData(
        id="test_id_1",
        data="""[{"movie": {"title": "Toy Story"}}]""",
    )

    result = OneCardDataTransformer().process(c, data)
    assert result.id == "test_id_1"
    assert result.title == "Toy Story Details"
    assert result.image is None
    assert len(result.fields) == 1
    assert result.fields[0].name == "Title"
    assert result.fields[0].data == ["Toy Story"]
