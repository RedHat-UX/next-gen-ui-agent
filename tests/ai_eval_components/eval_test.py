from typing import NotRequired, Optional, TypedDict

from ai_eval_components.eval import check_result_explicit
from ai_eval_components.eval_utils import assert_array_not_empty, assert_str_not_blank
from ai_eval_components.types import DatasetRow, EvalError
from next_gen_ui_agent.types import DataField, UIComponentMetadata
from pydantic import BaseModel

ERR = "error-test"


class TestTypeDict(TypedDict):
    array: NotRequired[list[str]]
    string: NotRequired[str]


class TestPydantic(BaseModel):
    array: Optional[list[str]] = None
    string: Optional[str] = None


def test_assert_array_not_empty_TypeDict_None() -> None:
    errors: list[EvalError] = []
    component: TestTypeDict = {}
    assert_array_not_empty(component, "array", ERR, errors, "my msg")
    assert errors[0].code == ERR
    assert errors[0].message == "my msg"


def test_assert_array_not_empty_Pydantic_None() -> None:
    errors: list[EvalError] = []
    component: TestPydantic = TestPydantic()
    assert_array_not_empty(component, "array", ERR, errors, "my msg")
    assert errors[0].code == ERR
    assert errors[0].message == "my msg"


def test_assert_array_not_empty_TypeDict_Empty() -> None:
    errors: list[EvalError] = []
    component: TestTypeDict = {"array": []}
    assert_array_not_empty(component, "array", ERR, errors)
    assert errors[0].code == ERR
    assert errors[0].message == "array is '[]'"


def test_assert_array_not_empty_Pydantic_Empty() -> None:
    errors: list[EvalError] = []
    component: TestPydantic = TestPydantic.model_validate({"array": []})
    assert_array_not_empty(component, "array", ERR, errors)
    assert errors[0].code == ERR
    assert errors[0].message == "array is '[]'"


def test_assert_array_not_empty_TypeDict_OK() -> None:
    errors: list[EvalError] = []
    component: TestTypeDict = {"array": ["a"]}
    assert_array_not_empty(component, "array", ERR, errors)
    assert len(errors) == 0


def test_assert_array_not_empty_Pydantic_OK() -> None:
    errors: list[EvalError] = []
    component: TestPydantic = TestPydantic.model_validate({"array": ["a"]})
    assert_array_not_empty(component, "array", ERR, errors)
    assert len(errors) == 0


def test_assert_str_not_blank_TypeDict_None() -> None:
    errors: list[EvalError] = []
    component: TestTypeDict = {}
    assert_str_not_blank(component, "string", ERR, errors)
    assert errors[0].code == ERR
    assert errors[0].message == "string is missing"


def test_assert_str_not_blank_Pydantic_None() -> None:
    errors: list[EvalError] = []
    component: TestPydantic = TestPydantic()
    assert_str_not_blank(component, "string", ERR, errors)
    assert errors[0].code == ERR
    assert errors[0].message == "string value is 'None'"


def test_assert_str_not_blank_TypeDict_Empty() -> None:
    errors: list[EvalError] = []
    component: TestTypeDict = {"string": ""}
    assert_str_not_blank(component, "string", ERR, errors)
    assert errors[0].code == ERR
    assert errors[0].message == "string value is ''"


def test_assert_str_not_blank_Pydantic_Empty() -> None:
    errors: list[EvalError] = []
    component: TestPydantic = TestPydantic.model_validate({"string": ""})
    assert_str_not_blank(component, "string", ERR, errors)
    assert errors[0].code == ERR
    assert errors[0].message == "string value is ''"


def test_assert_str_not_blank_TypeDict_Blank() -> None:
    errors: list[EvalError] = []
    component: TestTypeDict = {"string": "  "}
    assert_str_not_blank(component, "string", ERR, errors, "my msg")
    assert errors[0].code == ERR
    assert errors[0].message == "my msg"


def test_assert_str_not_blank_Pydantic_Blank() -> None:
    errors: list[EvalError] = []
    component: TestPydantic = TestPydantic.model_validate({"string": "  "})
    assert_str_not_blank(component, "string", ERR, errors, "my msg")
    assert errors[0].code == ERR
    assert errors[0].message == "my msg"


def test_assert_str_not_blank_TypeDict_OK() -> None:
    errors: list[EvalError] = []
    component: TestTypeDict = {"string": "a"}
    assert_str_not_blank(component, "string", ERR, errors)
    assert len(errors) == 0


def test_assert_str_not_blank_Pydantic_OK() -> None:
    errors: list[EvalError] = []
    component: TestPydantic = TestPydantic.model_validate({"string": "a"})
    assert_str_not_blank(component, "string", ERR, errors)
    assert len(errors) == 0


def test_check_result_explicit_BASIC_ATTRS_NONE() -> None:
    errors: list[EvalError] = []
    component: UIComponentMetadata = UIComponentMetadata.model_construct()
    dsr: DatasetRow = {}  # type: ignore

    check_result_explicit(component, errors, dsr)
    assert len(errors) == 3
    assert errors[0].code == "title.empty"
    assert errors[1].code == "component.empty"
    assert errors[2].code == "fields.empty"


def test_check_result_explicit_BASIC_ATTRS_EMPTY() -> None:
    errors: list[EvalError] = []
    component: UIComponentMetadata = UIComponentMetadata.model_validate(
        {"title": " ", "component": " ", "fields": []}
    )
    dsr: DatasetRow = {}  # type: ignore

    check_result_explicit(component, errors, dsr)
    assert len(errors) == 3
    assert errors[0].code == "title.empty"
    assert errors[1].code == "component.empty"
    assert errors[2].code == "fields.empty"


def test_check_result_explicit_COMPONENT_INCORRECT() -> None:
    errors: list[EvalError] = []
    # everything is valid here
    component: UIComponentMetadata = UIComponentMetadata.model_validate(
        {
            "title": "my title",
            "component": "one-card",
            "fields": [{"name": "my name", "data_path": "dp", "data": ["a"]}],
        }
    )
    # but expected component is different
    dsr: DatasetRow = {"expected_component": "table"}  # type: ignore

    check_result_explicit(component, errors, dsr)
    assert len(errors) == 1
    assert errors[0].code == "component.invalid"


def test_check_result_explicit_FIELDS_ATTRS_EMPTY() -> None:
    errors: list[EvalError] = []
    component: UIComponentMetadata = UIComponentMetadata(
        title="my title",
        component="one-card",
        fields=[DataField.model_construct(), DataField.model_construct()],
    )
    dsr: DatasetRow = {"expected_component": "one-card"}  # type: ignore

    check_result_explicit(component, errors, dsr)
    # two attributes are checked in each object
    assert len(errors) == 4
    assert errors[0].code == "fields[0].name.empty"
    assert errors[1].code == "fields[0].data_path.empty"
    assert errors[2].code == "fields[1].name.empty"
    assert errors[3].code == "fields[1].data_path.empty"


def test_check_result_explicit_FIELDS_DATA_MISSING() -> None:
    errors: list[EvalError] = []
    component: UIComponentMetadata = UIComponentMetadata.model_validate(
        {
            "title": "my title",
            "component": "one-card",
            "fields": [
                {"name": "name 1", "data_path": "dp", "data": ["a"]},
                {"name": "name 2", "data_path": "dp2"},
            ],
        }
    )
    dsr: DatasetRow = {"expected_component": "one-card"}  # type: ignore

    check_result_explicit(component, errors, dsr)
    # data are missing in the second field
    assert len(errors) == 1
    assert errors[0].code == "fields[1].data_path.points_no_data"


def test_check_result_explicit_FIELDS_DATA_EMPTY() -> None:
    # this test case may not be valid later, once libs/next_gen_ui_agent/data_transformation.py is improved, if it becomes to use None for missing data (now it uses [])
    errors: list[EvalError] = []
    component: UIComponentMetadata = UIComponentMetadata.model_validate(
        {
            "title": "my title",
            "component": "one-card",
            "fields": [
                {"name": "name 1", "data_path": "dp", "data": ["a"]},
                {"name": "name 2", "data_path": "dp2", "data": []},
            ],
        }
    )
    dsr: DatasetRow = {"expected_component": "one-card"}  # type: ignore

    check_result_explicit(component, errors, dsr)
    # data are missing in the second field
    assert len(errors) == 1
    assert errors[0].code == "fields[1].data_path.points_no_data"
