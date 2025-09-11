from typing import Optional

from next_gen_ui_agent.data_transform.validation.assertions import (
    assert_array_not_empty,
    assert_str_not_blank,
    is_url_http,
)
from next_gen_ui_agent.data_transform.validation.types import (
    ComponentDataValidationError,
)
from pydantic import BaseModel
from typing_extensions import NotRequired, TypedDict

ERR = "error-test"


def test_is_url_http() -> None:
    assert is_url_http("https://www.google.com")
    assert is_url_http("http://www.google.com")
    assert is_url_http("http://www.google.com/path/and")
    assert is_url_http("http://www.google.com?rt=hg")
    assert is_url_http("https://www.google.com/path/and/other?rt=hg")
    assert is_url_http("https://www.google.com/path/and/other/?rt=hg")
    assert is_url_http(
        "httpS://www.google.com/path/and/other/?rt=hg"
    )  # assert check is case insensitive
    assert not is_url_http("www.google.com")
    assert not is_url_http("google.com")
    assert not is_url_http("http://")
    assert not is_url_http("ftp://www.google.com")  # assert only http/s is allowed


class TestTypeDict(TypedDict):
    array: NotRequired[list[str]]
    string: NotRequired[str]


class TestPydantic(BaseModel):
    array: Optional[list[str]] = None
    string: Optional[str] = None


def test_assert_array_not_empty_TypeDict_None() -> None:
    errors: list[ComponentDataValidationError] = []
    component: TestTypeDict = {}
    assert_array_not_empty(component, "array", ERR, errors, "my msg")
    assert errors[0].code == ERR
    assert errors[0].message == "my msg"


def test_assert_array_not_empty_Pydantic_None() -> None:
    errors: list[ComponentDataValidationError] = []
    component: TestPydantic = TestPydantic()
    assert_array_not_empty(component, "array", ERR, errors, "my msg")
    assert errors[0].code == ERR
    assert errors[0].message == "my msg"


def test_assert_array_not_empty_TypeDict_Empty() -> None:
    errors: list[ComponentDataValidationError] = []
    component: TestTypeDict = {"array": []}
    assert_array_not_empty(component, "array", ERR, errors)
    assert errors[0].code == ERR
    assert errors[0].message == "array is '[]'"


def test_assert_array_not_empty_Pydantic_Empty() -> None:
    errors: list[ComponentDataValidationError] = []
    component: TestPydantic = TestPydantic.model_validate({"array": []})
    assert_array_not_empty(component, "array", ERR, errors)
    assert errors[0].code == ERR
    assert errors[0].message == "array is '[]'"


def test_assert_array_not_empty_TypeDict_OK() -> None:
    errors: list[ComponentDataValidationError] = []
    component: TestTypeDict = {"array": ["a"]}
    assert_array_not_empty(component, "array", ERR, errors)
    assert len(errors) == 0


def test_assert_array_not_empty_Pydantic_OK() -> None:
    errors: list[ComponentDataValidationError] = []
    component: TestPydantic = TestPydantic.model_validate({"array": ["a"]})
    assert_array_not_empty(component, "array", ERR, errors)
    assert len(errors) == 0


def test_assert_str_not_blank_TypeDict_None() -> None:
    errors: list[ComponentDataValidationError] = []
    component: TestTypeDict = {}
    assert_str_not_blank(component, "string", ERR, errors)
    assert errors[0].code == ERR
    assert errors[0].message == "string is missing"


def test_assert_str_not_blank_Pydantic_None() -> None:
    errors: list[ComponentDataValidationError] = []
    component: TestPydantic = TestPydantic()
    assert_str_not_blank(component, "string", ERR, errors)
    assert errors[0].code == ERR
    assert errors[0].message == "string value is 'None'"


def test_assert_str_not_blank_TypeDict_Empty() -> None:
    errors: list[ComponentDataValidationError] = []
    component: TestTypeDict = {"string": ""}
    assert_str_not_blank(component, "string", ERR, errors)
    assert errors[0].code == ERR
    assert errors[0].message == "string value is ''"


def test_assert_str_not_blank_Pydantic_Empty() -> None:
    errors: list[ComponentDataValidationError] = []
    component: TestPydantic = TestPydantic.model_validate({"string": ""})
    assert_str_not_blank(component, "string", ERR, errors)
    assert errors[0].code == ERR
    assert errors[0].message == "string value is ''"


def test_assert_str_not_blank_TypeDict_Blank() -> None:
    errors: list[ComponentDataValidationError] = []
    component: TestTypeDict = {"string": "  "}
    assert_str_not_blank(component, "string", ERR, errors, "my msg")
    assert errors[0].code == ERR
    assert errors[0].message == "my msg"


def test_assert_str_not_blank_Pydantic_Blank() -> None:
    errors: list[ComponentDataValidationError] = []
    component: TestPydantic = TestPydantic.model_validate({"string": "  "})
    assert_str_not_blank(component, "string", ERR, errors, "my msg")
    assert errors[0].code == ERR
    assert errors[0].message == "my msg"


def test_assert_str_not_blank_TypeDict_OK() -> None:
    errors: list[ComponentDataValidationError] = []
    component: TestTypeDict = {"string": "a"}
    assert_str_not_blank(component, "string", ERR, errors)
    assert len(errors) == 0


def test_assert_str_not_blank_Pydantic_OK() -> None:
    errors: list[ComponentDataValidationError] = []
    component: TestPydantic = TestPydantic.model_validate({"string": "a"})
    assert_str_not_blank(component, "string", ERR, errors)
    assert len(errors) == 0
