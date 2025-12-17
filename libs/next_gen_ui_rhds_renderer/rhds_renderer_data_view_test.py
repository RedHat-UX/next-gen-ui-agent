from next_gen_ui_agent import design_system_handler
from next_gen_ui_agent.agent import NextGenUIAgent
from next_gen_ui_agent.data_transform.types import ComponentDataDataView
from next_gen_ui_agent.renderer.base_renderer import StrategyFactory
from next_gen_ui_agent.renderer.data_view_shareable_tests import (
    BaseDataViewRendererTests,
)
from next_gen_ui_rhds_renderer import RhdsStrategyFactory
from next_gen_ui_testing.agent_testing import extension_manager_for_testing
from next_gen_ui_testing.data_after_transformation import get_transformed_component

component_system = "rhds"


class TestDataViewRHDSRendererWithShareableTests(BaseDataViewRendererTests):
    """Test class for RHDS renderer using shared test cases for data-view component."""

    def get_strategy_factory(self) -> StrategyFactory:
        return RhdsStrategyFactory()


def test_renderer_data_view_full() -> None:
    """Test full RHDS rendering of data-view component with table structure."""
    agent = NextGenUIAgent()
    design_system_handler.EXTENSION_MANAGER = extension_manager_for_testing(
        "rhds", RhdsStrategyFactory()
    )
    component = get_transformed_component("data-view")
    rendition = agent.generate_rendering(component, component_system).content
    assert rendition
    # Verify title
    assert "Movies" in rendition
    # Verify field names in header
    assert "Titles" in rendition
    assert "Years" in rendition
    # Verify data values in table body
    assert "Toy Story" in rendition
    assert "Toy Story 2" in rendition
    assert "1995" in rendition
    assert "1999" in rendition
    # Verify table structure
    assert "<rh-table>" in rendition
    assert "<table>" in rendition
    assert "<caption>Movies</caption>" in rendition
    assert "<colgroup>" in rendition
    assert "<col>" in rendition
    assert "<thead>" in rendition
    assert "<tbody>" in rendition
    assert '<th scope="col">' in rendition
    assert "<td>" in rendition
    # Verify sort buttons in header
    assert "<rh-sort-button>" in rendition
    # Verify script imports
    assert "@rhds/elements/rh-table/rh-table.js" in rendition
    # Verify CSS link
    assert "rh-table-lightdom.css" in rendition
    # Verify correct number of columns (2 fields = 2 cols)
    assert rendition.count("<col>") == 2
    # Verify correct number of header cells (2 fields = 2 opening th tags)
    # Note: template has a closing </th> after the loop, so we count opening tags
    assert rendition.count('<th scope="col">') == 2


def test_renderer_data_view_single_row() -> None:
    """Test RHDS rendering with a single data row."""
    agent = NextGenUIAgent()
    design_system_handler.EXTENSION_MANAGER = extension_manager_for_testing(
        "rhds", RhdsStrategyFactory()
    )
    component = ComponentDataDataView.model_validate(
        {
            "id": "test_id_single",
            "title": "Single Item",
            "component": "data-view",
            "fields": [
                {
                    "name": "Name",
                    "data_path": "item.name",
                    "data": ["Item 1"],
                },
                {
                    "name": "Value",
                    "data_path": "item.value",
                    "data": ["100"],
                },
            ],
        }
    )
    rendition = agent.generate_rendering(component, component_system).content
    assert rendition
    assert "Single Item" in rendition
    assert "Name" in rendition
    assert "Value" in rendition
    assert "Item 1" in rendition
    assert "100" in rendition
    assert "<tbody>" in rendition
    # Should have exactly one row
    assert rendition.count("<tr>") == 2  # One in thead, one in tbody


def test_renderer_data_view_mismatched_lengths() -> None:
    """Test RHDS rendering when field arrays have different lengths."""
    agent = NextGenUIAgent()
    design_system_handler.EXTENSION_MANAGER = extension_manager_for_testing(
        "rhds", RhdsStrategyFactory()
    )
    component = ComponentDataDataView.model_validate(
        {
            "id": "test_id_mismatch",
            "title": "Mismatched Data",
            "component": "data-view",
            "fields": [
                {
                    "name": "Name",
                    "data_path": "items[*].name",
                    "data": ["Item 1", "Item 2", "Item 3"],
                },
                {
                    "name": "Value",
                    "data_path": "items[*].value",
                    "data": ["100", "200"],  # Shorter array
                },
            ],
        }
    )
    rendition = agent.generate_rendering(component, component_system).content
    assert rendition
    assert "Mismatched Data" in rendition
    assert "Item 1" in rendition
    assert "Item 2" in rendition
    assert "Item 3" in rendition
    assert "100" in rendition
    assert "200" in rendition
    # Should handle missing values with "-" placeholder (3 rows total, last row has "-" for Value)
    assert "-" in rendition
    # Should have 3 data rows (max length is 3)
    assert rendition.count("<tr>") == 4  # 1 header row + 3 data rows


def test_renderer_data_view_with_array_values() -> None:
    """Test RHDS rendering with array values in field data."""
    agent = NextGenUIAgent()
    design_system_handler.EXTENSION_MANAGER = extension_manager_for_testing(
        "rhds", RhdsStrategyFactory()
    )
    component = ComponentDataDataView.model_validate(
        {
            "id": "test_id_arrays",
            "title": "Movies with Tags",
            "component": "data-view",
            "fields": [
                {
                    "name": "Title",
                    "data_path": "movies[*].title",
                    "data": ["Movie A", "Movie B"],
                },
                {
                    "name": "Tags",
                    "data_path": "movies[*].tags",
                    "data": [["action", "sci-fi"], ["drama", "comedy"]],
                },
            ],
        }
    )
    rendition = agent.generate_rendering(component, component_system).content
    assert rendition
    assert "Movies with Tags" in rendition
    assert "Title" in rendition
    assert "Tags" in rendition
    assert "Movie A" in rendition
    assert "Movie B" in rendition
    # Array values should be rendered (as string representation when converted)
    # The template renders field.get("data")[i] which will convert lists to strings
    assert "action" in rendition or "sci-fi" in rendition or "drama" in rendition


def test_renderer_data_view_empty_data() -> None:
    """Test RHDS rendering with empty data arrays."""
    agent = NextGenUIAgent()
    design_system_handler.EXTENSION_MANAGER = extension_manager_for_testing(
        "rhds", RhdsStrategyFactory()
    )
    component = ComponentDataDataView.model_validate(
        {
            "id": "test_id_empty",
            "title": "Empty Table",
            "component": "data-view",
            "fields": [
                {
                    "name": "Name",
                    "data_path": "items[*].name",
                    "data": [],
                },
                {
                    "name": "Value",
                    "data_path": "items[*].value",
                    "data": [],
                },
            ],
        }
    )
    rendition = agent.generate_rendering(component, component_system).content
    assert rendition
    assert "Empty Table" in rendition
    assert "<rh-table>" in rendition
    assert "<thead>" in rendition
    assert "Name" in rendition
    assert "Value" in rendition
    # Should have header but no data rows (data_length is 0)
    assert rendition.count("<tr>") == 1  # Only header row
    assert "<tbody>" in rendition
