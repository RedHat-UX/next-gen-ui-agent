from next_gen_ui_agent.data_transform.hand_build_component import (
    HandBuildComponentDataTransformer,
)
from next_gen_ui_agent.data_transform.validation.types import (
    ComponentDataValidationError,
)
from next_gen_ui_agent.types import InputData, UIComponentMetadataHandBuildComponent


def test_process() -> None:
    c = UIComponentMetadataHandBuildComponent.model_validate(
        {
            "id": "test_id_1",
            "title": "",
            "component": "hand-build-component",
            "component_type": "one-card-special",
            "fields": [],
        }
    )
    data = InputData(
        id="test_id_1",
        data="""{
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
        }""",
    )
    result = HandBuildComponentDataTransformer().process(c, data)
    assert result.id == "test_id_1"
    assert result.component_type == "one-card-special"
    assert result.data == {
        "movies": [
            {"title": "Toy Story", "authors": ["A1", "A2"]},
            {"title": "Toy Story 2", "authors": ["A3"]},
        ]
    }


def test_validate_OK() -> None:
    c = UIComponentMetadataHandBuildComponent.model_validate(
        {
            "id": "test_id_1",
            "title": "Toy Story Details",
            "component": "set-of-cards",
            "component_type": "one-card-special",
            "fields": [],
        }
    )
    data = InputData(
        id="test_id_1",
        data="""{"movies": [{"title": "Toy Story"}, {"title": "Toy Story 2"}]}""",
    )
    errors: list[ComponentDataValidationError] = []
    HandBuildComponentDataTransformer().validate(c, data, errors)
    assert len(errors) == 0
