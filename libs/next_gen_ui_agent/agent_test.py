import pytest
from next_gen_ui_agent.agent import NextGenUIAgent
from next_gen_ui_testing.data_after_transformation import get_transformed_component
from pydantic_core import from_json


def test_design_system_handler_wrong_name() -> None:
    agent = NextGenUIAgent()
    with pytest.raises(
        Exception,
        match="configured component system 'bad' is not present in extension_manager. Make sure you install appropriate dependency",
    ):
        agent.design_system_handler(list(), "bad")


def test_design_system_handler_json() -> None:
    agent = NextGenUIAgent()
    c = get_transformed_component()
    result = agent.design_system_handler([c], "json")

    r = from_json(result[0].content)
    assert r["component"] == "one-card"


def test_renderers() -> None:
    agent = NextGenUIAgent()
    assert agent.renderers == ["json"]


if __name__ == "__main__":
    test_design_system_handler_json()
