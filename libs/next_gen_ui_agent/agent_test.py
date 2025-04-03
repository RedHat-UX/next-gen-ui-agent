import pytest
from next_gen_ui_agent.agent import NextGenUIAgent
from next_gen_ui_testing.data_after_transformation import get_transformed_component


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
    assert result[0]["component"] == "one-card"


def test_renderers() -> None:
    agent = NextGenUIAgent()
    assert agent.renderers == ["json"]
