from next_gen_ui_agent.agent import NextGenUIAgent
from next_gen_ui_agent.data_transform.types import (
    ComponentDataHandBuildComponent,
    ComponentDataOneCard,
)
from next_gen_ui_agent.renderer.base_renderer import StrategyFactory
from next_gen_ui_agent.renderer.hand_build_component_shareable_tests import (
    BaseHandBuildComponentRendererTests,
)
from next_gen_ui_rhds_hbc_example_renderer.hbc_renderer import (
    HbcExampleRhdsStrategy,
    HbcExampleRhdsStrategyFactory,
)
from next_gen_ui_testing.agent_testing import extension_manager_for_testing


class TestHbcExampleRhdsRendererWithShareableTests(BaseHandBuildComponentRendererTests):
    """Test class for HBC Example RHDS renderer using shared test cases for hand-build component."""

    def get_strategy_factory(self) -> StrategyFactory:
        return HbcExampleRhdsStrategyFactory()


def test_renderer_hbc_example_component() -> None:
    """Test rendering of the hbc-example-component."""
    agent = NextGenUIAgent()
    agent._extension_manager = extension_manager_for_testing(
        "hbc-example-rhds", HbcExampleRhdsStrategyFactory()
    )

    component = ComponentDataHandBuildComponent.model_validate(
        {
            "id": "test_id_1",
            "component": "hbc-example-component",
            "data": {
                "title": "Hello World",
            },
        }
    )

    rendition = agent.design_system_handler([component], "hbc-example-rhds")[0].content
    print(rendition)

    # Verify the rendered output contains expected elements
    assert "Hello World" in rendition
    assert "simple hand-build component example" in rendition


def test_renderer_one_card_standard_component() -> None:
    """Test that the HBC Example renderer correctly delegates standard dynamic components to RHDS renderer."""
    agent = NextGenUIAgent()
    agent._extension_manager = extension_manager_for_testing(
        "hbc-example-rhds", HbcExampleRhdsStrategyFactory()
    )

    component = ComponentDataOneCard.model_validate(
        {
            "id": "test_id_2",
            "title": "Toy Story Details",
            "component": "one-card",
            "fields": [
                {"name": "Title", "data_path": "movie.title", "data": ["Toy Story"]},
                {"name": "Year", "data_path": "movie.year", "data": ["1995"]},
                {
                    "name": "IMDB Rating",
                    "data_path": "movie.imdbRating",
                    "data": ["8.3"],
                },
            ],
        }
    )

    rendition = agent.design_system_handler([component], "hbc-example-rhds")[0].content
    print(rendition)

    # Verify the rendered output contains expected RHDS elements for one-card
    assert "Toy Story Details" in rendition
    assert '<rh-card class="ngui-one-card">' in rendition
    assert "<dt>Title</dt>" in rendition
    assert "<dd>Toy Story</dd>" in rendition
    assert "<dt>Year</dt>" in rendition
    assert "<dd>1995</dd>" in rendition
    assert "<dt>IMDB Rating</dt>" in rendition
    assert "<dd>8.3</dd>" in rendition
    assert "@rhds/elements/rh-card/rh-card.js" in rendition


def test_factory_get_component_system_name() -> None:
    """Test that the factory returns the correct component system name."""
    factory = HbcExampleRhdsStrategyFactory()
    assert factory.get_component_system_name() == "hbc-example-rhds"


def test_factory_get_output_mime_type() -> None:
    """Test that the factory returns the correct output MIME type."""
    factory = HbcExampleRhdsStrategyFactory()
    assert factory.get_output_mime_type() == "text/html"


def test_factory_custom_hbc_component() -> None:
    """Test that the factory correctly handles custom HBC components."""
    factory = HbcExampleRhdsStrategyFactory()

    component = ComponentDataHandBuildComponent.model_validate(
        {
            "id": "test_id",
            "component": "hbc-example-component",
            "data": {"title": "Test"},
        }
    )

    strategy = factory.get_render_strategy(component)
    assert isinstance(strategy, HbcExampleRhdsStrategy)


def test_factory_unsupported_component() -> None:
    """Test that the factory raises ValueError for unsupported components."""
    factory = HbcExampleRhdsStrategyFactory()

    component = ComponentDataHandBuildComponent.model_validate(
        {
            "id": "test_id",
            "component": "unsupported-component",
            "data": {"title": "Test"},
        }
    )

    try:
        factory.get_render_strategy(component)
        assert False, "Expected ValueError for unsupported component"
    except ValueError as e:
        assert "is not supported by Red Hat Design System rendering plugin" in str(e)
