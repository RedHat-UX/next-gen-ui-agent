from next_gen_ui_agent.renderer.one_card import OneCardRenderStrategy
from next_gen_ui_agent.types import UIComponentMetadata


def test_process() -> None:
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_id_1",
            "title": "Toy Story Details",
            "reasonForTheComponentSelection": "One item available in the data",
            "confidenceScore": "100%",
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
    result = OneCardRenderStrategy().process(c)
    assert result.title == "Toy Story Details"
    assert (
        result.image
        == "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg"
    )
    assert len(result.fields) == 2
    assert result.field_names == ["Title", "Authors"]
    assert result.fields[0].name == "Title"
    assert result.fields[0].data == ["Toy Story"]
    assert result.fields[1].name == "Authors"
    assert result.fields[1].data == ["A1", "A2", "A3"]


def test_process_data_lenght() -> None:
    c = UIComponentMetadata.model_validate(
        {
            "title": "Toy Story Details",
            "component": "one-card",
            "fields": [
                {"name": "Title", "data_path": "movie.title", "data": ["Toy Story"]},
                {"name": "Authors", "data_path": "NA", "data": ["A1", "A2", "A3"]},
            ],
        }
    )
    result = OneCardRenderStrategy().process(c)
    assert result.data_length == 3


def test_process_no_image() -> None:
    c = UIComponentMetadata.model_validate(
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
    result = OneCardRenderStrategy().process(c)
    assert result.title == "Toy Story Details"
    assert result.image is None
    assert len(result.fields) == 1
    assert result.data_length == 1
    assert result.field_names == ["Title"]
    assert result.fields[0].name == "Title"
    assert result.fields[0].data == ["Toy Story"]
