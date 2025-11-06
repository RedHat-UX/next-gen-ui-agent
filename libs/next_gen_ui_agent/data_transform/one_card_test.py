from next_gen_ui_agent.data_transform.one_card import OneCardDataTransformer
from next_gen_ui_agent.data_transform.validation.types import (
    ComponentDataValidationError,
)
from next_gen_ui_agent.types import InputData, UIComponentMetadata


def test_process() -> None:
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_id_1",
            "title": "Toy Story Details",
            "component": "one-card",
            "fields": [
                {"name": "Title", "data_path": "movie.title"},
                {"name": "Authors", "data_path": "movie.authors[*]"},
                {"name": "Authors 2", "data_path": "movie.authors"},
                {"name": "Poster", "data_path": "movie.posterUrl"},
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
    assert len(result.fields) == 3
    assert result.fields[0].id == "title"
    assert result.fields[0].name == "Title"
    assert result.fields[0].data == ["Toy Story"]
    assert result.fields[1].id == "movie_authors"
    assert result.fields[1].name == "Authors"
    assert result.fields[1].data == ["A1", "A2", "A3"]
    assert result.fields[2].id == "authors"
    assert result.fields[2].name == "Authors 2"
    assert result.fields[2].data == ["A1", "A2", "A3"]
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
                {"name": "Title", "data_path": "movie.title"},
            ],
        }
    )
    data = InputData(
        id="test_id_1",
        data="""[{"movie": {"title": "Toy Story", "posterUrl": "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg"}}]""",
    )

    result = OneCardDataTransformer().process(c, data)
    assert result.id == "test_id_1"
    assert result.title == "Toy Story Details"
    assert result.image is None
    assert len(result.fields) == 1
    assert result.fields[0].name == "Title"
    assert result.fields[0].data == ["Toy Story"]


def test_validate_OK() -> None:
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_id_1",
            "title": "Toy Story Details",
            "component": "one-card",
            "fields": [
                {"name": "Title", "data_path": "movie.title"},
            ],
        }
    )
    data = InputData(
        id="test_id_1",
        data="""{"movie": {"title": "Toy Story"}}""",
    )
    errors: list[ComponentDataValidationError] = []
    OneCardDataTransformer().validate(c, data, errors)
    assert len(errors) == 0


def test_validate_INVALID() -> None:
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_id_1",
            "title": "Toy Story Details",
            "component": "one-card",
            "fields": [
                {"name": "Title", "data_path": "movie.title"},
                {"name": "Empty path", "data_path": ""},
                {"name": "Invalid path", "data_path": "$"},
                {"name": "Empty path", "data_path": "movie.unknown"},
                {"name": "Invalid image URL", "data_path": "movie.posterUrl"},
            ],
        }
    )
    data = InputData(
        id="test_id_1",
        data="""{"movie": {"title": "Toy Story", "posterUrl": "aasdfsd"}}""",
    )
    errors: list[ComponentDataValidationError] = []
    OneCardDataTransformer().validate(c, data, errors)
    assert len(errors) == 3
    assert errors[0].code == "fields[1].data_path.invalid_format"
    assert errors[0].message == "Generated data_path='' is not valid"
    assert errors[1].code == "fields[2].data_path.invalid_format"
    assert errors[1].message == "Generated data_path='' is not valid"
    assert errors[2].code == "fields[3].data_path.invalid"
    assert (
        errors[2].message
        == "No value found in input data for data_path='$..movie.unknown'"
    )
