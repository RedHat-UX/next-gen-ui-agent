from next_gen_ui_agent.data_transform.table import TableDataTransformer
from next_gen_ui_agent.data_transform.validation.types import (
    ComponentDataValidationError,
)
from next_gen_ui_agent.types import InputData, UIComponentMetadata


def test_process() -> None:
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_id_1",
            "title": "Toy Story Details",
            "component": "table",
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
    result = TableDataTransformer().process(c, data)
    assert result.title == "Toy Story Details"
    assert len(result.fields) == 3
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
            "component": "table",
            "fields": [
                {"name": "Title", "data_path": "movies[*].title"},
            ],
        }
    )
    data = InputData(
        id="test_id_1",
        data="""{"movies": [{"title": "Toy Story"}]}""",
    )
    errors: list[ComponentDataValidationError] = []
    TableDataTransformer().validate(c, data, errors)
    assert len(errors) == 0


def test_validate_INVALID() -> None:
    c = UIComponentMetadata.model_validate(
        {
            "id": "test_id_1",
            "title": "Toy Story Details",
            "component": "table",
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
    TableDataTransformer().validate(c, data, errors)
    assert len(errors) == 3
    assert errors[0].code == "fields[1].data_path.invalid_format"
    assert errors[0].message == "Generated data_path='' is not valid"
    assert errors[1].code == "fields[2].data_path.invalid_format"
    assert errors[1].message == "Generated data_path='' is not valid"
    assert errors[2].code == "fields[3].data_path.invalid"
    assert (
        errors[2].message
        == "No value found in input data for data_path='$..movies[*].unknown'"
    )
