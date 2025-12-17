from ai_eval_components.eval import check_result_explicit
from ai_eval_components.types import DatasetRow
from next_gen_ui_agent.data_transform.validation.types import (
    ComponentDataValidationError,
)
from next_gen_ui_agent.types import UIComponentMetadata


def test_check_result_explicit_BASIC_ATTRS_NONE() -> None:
    errors: list[ComponentDataValidationError] = []
    component: UIComponentMetadata = UIComponentMetadata.model_construct()
    dsr: DatasetRow = {}  # type: ignore

    check_result_explicit(component, errors, dsr, False)
    assert len(errors) == 3
    assert errors[0].code == "title.empty"
    assert errors[1].code == "component.empty"
    assert errors[2].code == "fields.empty"


def test_check_result_explicit_BASIC_ATTRS_EMPTY() -> None:
    errors: list[ComponentDataValidationError] = []
    component: UIComponentMetadata = UIComponentMetadata.model_validate(
        {"title": " ", "component": " ", "fields": []}
    )
    dsr: DatasetRow = {}  # type: ignore

    check_result_explicit(component, errors, dsr, False)
    assert len(errors) == 3
    assert errors[0].code == "title.empty"
    assert errors[1].code == "component.empty"
    assert errors[2].code == "fields.empty"


def test_check_result_explicit_COMPONENT_INCORRECT() -> None:
    errors: list[ComponentDataValidationError] = []
    # everything is valid here
    component: UIComponentMetadata = UIComponentMetadata.model_validate(
        {
            "title": "my title",
            "component": "set-of-cards",
            "fields": [{"name": "my name", "data_path": "dp", "data": ["a"]}],
        }
    )
    # but expected component is different
    dsr: DatasetRow = {"expected_component": "data-view"}  # type: ignore

    check_result_explicit(component, errors, dsr, False)
    assert len(errors) == 1
    assert errors[0].code == "component.invalid"


def test_check_result_explicit_COMPONENT_INCORRECT_VAGUE() -> None:
    errors: list[ComponentDataValidationError] = []
    # everything is valid here
    component: UIComponentMetadata = UIComponentMetadata.model_validate(
        {
            "title": "my title",
            "component": "set-of-cards",
            "fields": [{"name": "my name", "data_path": "dp", "data": ["a"]}],
        }
    )
    # expected component is different, but vague check allows it
    dsr: DatasetRow = {"expected_component": "data-view"}  # type: ignore

    check_result_explicit(component, errors, dsr, True)
    assert len(errors) == 0
