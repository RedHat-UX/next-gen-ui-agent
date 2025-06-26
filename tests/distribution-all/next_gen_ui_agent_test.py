import logging
import pytest

from next_gen_ui_agent import NextGenUIAgent
from next_gen_ui_agent.data_transform.types import ComponentDataOneCard
from next_gen_ui_testing import data_after_transformation

test_component: ComponentDataOneCard = (
    data_after_transformation.get_transformed_component()
)


# Can run without package installation because json is part of the agent and no autodiscovery is needed
def test_design_system_handler_json() -> None:
    agent = NextGenUIAgent()
    res = agent.design_system_handler([test_component], "json")
    json_str = res[0].content
    result = ComponentDataOneCard.model_validate_json(json_str)
    assert result.title == "Toy Story Details"
    assert result.fields[0].data == ["Toy Story"]
    assert result.fields[1].data == ["1995"]


# marking as distribution because of rendering autodiscovery and the distribution package is need to be installed
@pytest.mark.distribution
def test_design_system_handler_rhds() -> None:
    agent = NextGenUIAgent()
    res = agent.design_system_handler([test_component], "rhds")
    rendition = res[0].content
    assert "<rh-card" in rendition


# marking as distribution because of rendering autodiscovery and the distribution package is need to be installed
@pytest.mark.distribution
def test_design_system_handler_patternfly() -> None:
    agent = NextGenUIAgent()
    res = agent.design_system_handler([test_component], "patternfly")
    rendition = res[0].content
    assert "<Card>" in rendition


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    test_design_system_handler_json()
    test_design_system_handler_rhds()
    test_design_system_handler_patternfly()
