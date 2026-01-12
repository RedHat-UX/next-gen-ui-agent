from next_gen_ui_agent.data_transform.set_of_cards import SetOfCardsDataTransformer
from next_gen_ui_agent.data_transform.validation.types import (
    ComponentDataValidationError,
)
from next_gen_ui_agent.types import InputData, UIComponentMetadata


def test_process() -> None:
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_id_1",
            "title": "Toy Story Details",
            "component": "set-of-cards",
            "fields": [
                {"name": "Title", "data_path": "movies[*].title"},
                {"name": "Authors", "data_path": "movies[*].authors[*]"},
                {"name": "Authors 2", "data_path": "movies[*].authors"},
            ],
        }
    )
    data = InputData(
        id="test_id_1",
        data="""[
            {
                "movies":[
                {
                    "title": "Toy Story",
                    "authors": ["A1", "A2"]
                },
                {
                    "title": "Toy Story 2",
                    "authors": ["A3"]
                }
                ]
            }
        ]""",
    )
    result = SetOfCardsDataTransformer().process(c, data)
    assert result.title == "Toy Story Details"
    assert len(result.fields) == 3
    assert result.fields[0].id == "movies-title"
    assert result.fields[0].name == "Title"
    assert result.fields[0].data == ["Toy Story", "Toy Story 2"]
    assert result.fields[1].name == "Authors"
    assert result.fields[1].data == [["A1", "A2"], ["A3"]]
    assert result.fields[2].name == "Authors 2"
    assert result.fields[2].data == [["A1", "A2"], ["A3"]]


def test_validate_OK() -> None:
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_id_1",
            "title": "Toy Story Details",
            "component": "set-of-cards",
            "fields": [
                {"name": "Title", "data_path": "movies[*].title"},
            ],
        }
    )
    data = InputData(
        id="test_id_1",
        data="""{"movies": [{"title": "Toy Story"}, {"title": "Toy Story 2"}]}""",
    )
    errors: list[ComponentDataValidationError] = []
    SetOfCardsDataTransformer().validate(c, data, errors)
    assert len(errors) == 0


def test_validate_INVALID() -> None:
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_id_1",
            "title": "Toy Story Details",
            "component": "set-of-cards",
            "fields": [
                {"name": "Title", "data_path": "movies[*].title"},
                {"name": "Empty path", "data_path": ""},
                {"name": "Invalid path", "data_path": "$"},
                {"name": "Empty path", "data_path": "movies[*].unknown"},
            ],
        }
    )
    data = InputData(
        id="test_id_1",
        data="""{"movies": [{"title": "Toy Story"}]}""",
    )
    errors: list[ComponentDataValidationError] = []
    SetOfCardsDataTransformer().validate(c, data, errors)
    assert len(errors) == 4
    assert errors[0].code == "fields[0].data_path.not_enough_values"
    assert (
        errors[0].message
        == "Not enough values for array component found in the input data for data_path='$..movies[*].title'"
    )
    assert errors[1].code == "fields[1].data_path.invalid_format"
    assert errors[1].message == "Generated data_path='' is not valid"
    assert errors[2].code == "fields[2].data_path.invalid_format"
    assert errors[2].message == "Generated data_path='' is not valid"
    assert errors[3].code == "fields[3].data_path.invalid"
    assert (
        errors[3].message
        == "No value found in input data for data_path='$..movies[*].unknown'"
    )


def test_process_with_images() -> None:
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_id_2",
            "title": "Movies",
            "component": "set-of-cards",
            "fields": [
                {"name": "Title", "data_path": "movies[*].title"},
                {"name": "Poster", "data_path": "movies[*].posterUrl"},
                {"name": "Year", "data_path": "movies[*].year"},
            ],
        }
    )
    data = InputData(
        id="test_id_2",
        data="""[
            {
                "movies":[
                {
                    "title": "Toy Story",
                    "posterUrl": "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
                    "year": 1995
                },
                {
                    "title": "Toy Story 2",
                    "posterUrl": "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxac.jpg",
                    "year": 1999
                }
                ]
            }
        ]""",
    )
    result = SetOfCardsDataTransformer().process(c, data)
    # image field should be extracted and removed from fields
    assert result.images == [
        "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
        "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxac.jpg",
    ]
    # Only 'Title' and 'Year' remain
    assert [f.name for f in result.fields] == ["Title", "Year"]
    assert result.fields[0].data == ["Toy Story", "Toy Story 2"]
    assert result.fields[1].data == [1995, 1999]


def test_process_no_images() -> None:
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_id_3",
            "title": "Movies",
            "component": "set-of-cards",
            "fields": [
                {"name": "Title", "data_path": "movies[*].title"},
                {"name": "Year", "data_path": "movies[*].year"},
            ],
        }
    )
    data = InputData(
        id="test_id_3",
        data='{"movies": [{"title": "Toy Story", "year": 1995}, {"title": "Toy Story 2", "year": 1999}]}',
    )
    result = SetOfCardsDataTransformer().process(c, data)
    assert result.images is None
    assert [f.name for f in result.fields] == ["Title", "Year"]
