import json
import logging

from next_gen_ui_agent import NextGenUIAgent, UIComponentMetadata
from next_gen_ui_testing import data_after_transformation

test_component: UIComponentMetadata = data_after_transformation.get_transformed_component()


def test_design_system_handler_default_json() -> None:
    agent = NextGenUIAgent()
    agent.design_system_handler([test_component])
    json_str = test_component["rendition"]
    result: UIComponentMetadata = json.loads(json_str)
    assert result["title"] == "Toy Story Details"
    assert result["fields"][0]["data"] == ["Toy Story"]
    assert result["fields"][1]["data"] == ["1995"]


def test_design_system_handler_rhds() -> None:
    agent = NextGenUIAgent()
    agent.design_system_handler([test_component], "rhds")
    rendition = test_component["rendition"]
    assert "<rh-card" in rendition


def test_design_system_handler_patternfly() -> None:
    agent = NextGenUIAgent()
    agent.design_system_handler([test_component], "patternfly")
    rendition = test_component["rendition"]
    assert "<Card>" in rendition


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    test_design_system_handler_default_json()
    test_design_system_handler_rhds()
    test_design_system_handler_patternfly()
