from unittest.mock import Mock, patch

import pytest
from next_gen_ui_agent.data_transform.types import ComponentDataBase
from next_gen_ui_agent.design_system_handler import (
    get_component_system_factory,
    get_component_system_names,
    render_component,
)
from next_gen_ui_agent.renderer.base_renderer import RenderStrategyBase, StrategyFactory
from next_gen_ui_agent.renderer.json.json_renderer import JsonStrategyFactory
from next_gen_ui_agent.types import UIBlockRendering


class TestGetComponentSystemFactory:
    """Tests for get_component_system_factory function."""

    def test_get_json_factory(self) -> None:
        """Test that 'json' component system returns JsonStrategyFactory."""
        factory = get_component_system_factory("json")
        assert isinstance(factory, JsonStrategyFactory)
        assert factory.get_component_system_name() == "json"
        assert factory.get_output_mime_type() == "application/json"

    def test_get_unknown_component_system_raises_value_error(self) -> None:
        """Test that unknown component system raises ValueError."""
        with patch(
            "next_gen_ui_agent.design_system_handler.EXTENSION_MANAGER"
        ) as mock_manager:
            mock_manager.names.return_value = ["rhds", "patternfly"]
            with pytest.raises(
                ValueError, match="UI component system 'unknown' is not found"
            ):
                get_component_system_factory("unknown")

    def test_get_extension_manager_factory(self) -> None:
        """Test that registered extension component system returns factory from extension manager."""
        mock_factory = Mock(spec=StrategyFactory)
        mock_factory.get_component_system_name.return_value = "rhds"
        mock_factory.get_output_mime_type.return_value = "text/html"

        mock_extension = Mock()
        mock_extension.obj = mock_factory

        with patch(
            "next_gen_ui_agent.design_system_handler.EXTENSION_MANAGER"
        ) as mock_manager:
            mock_manager.names.return_value = ["rhds", "patternfly"]
            mock_manager.__getitem__.return_value = mock_extension

            factory = get_component_system_factory("rhds")
            assert factory == mock_factory
            mock_manager.__getitem__.assert_called_once_with("rhds")


class TestGetComponentSystemNames:
    """Tests for get_component_system_names function."""

    def test_get_component_system_names_includes_json(self) -> None:
        """Test that returned list includes 'json'."""
        names = get_component_system_names()
        assert "json" in names

    def test_get_component_system_names_includes_extensions(self) -> None:
        """Test that returned list includes extension manager names."""
        with patch(
            "next_gen_ui_agent.design_system_handler.EXTENSION_MANAGER"
        ) as mock_manager:
            mock_manager.names.return_value = ["rhds", "patternfly"]
            names = get_component_system_names()
            assert "json" in names
            assert "rhds" in names
            assert "patternfly" in names
            assert len(names) == 3

    def test_get_component_system_names_no_extensions(self) -> None:
        """Test that returned list only includes 'json' when no extensions are registered."""
        with patch(
            "next_gen_ui_agent.design_system_handler.EXTENSION_MANAGER"
        ) as mock_manager:
            mock_manager.names.return_value = []
            names = get_component_system_names()
            assert names == ["json"]


class TestRenderComponent:
    """Tests for render_component function."""

    def test_render_component_success(self) -> None:
        """Test successful component rendering."""
        # Create a mock component
        component = ComponentDataBase(component="one-card", id="test-id-123")

        # Create a mock factory and strategy
        mock_strategy = Mock(spec=RenderStrategyBase)
        mock_strategy.render.return_value = '{"rendered": "output"}'

        mock_factory = Mock(spec=StrategyFactory)
        mock_factory.get_render_strategy.return_value = mock_strategy
        mock_factory.get_component_system_name.return_value = "json"
        mock_factory.get_output_mime_type.return_value = "application/json"

        # Render the component
        result = render_component(component, mock_factory)

        # Verify the result
        assert isinstance(result, UIBlockRendering)
        assert result.id == "test-id-123"
        assert result.content == '{"rendered": "output"}'
        assert result.component_system == "json"
        assert result.mime_type == "application/json"

        # Verify the factory and strategy were called correctly
        mock_factory.get_render_strategy.assert_called_once_with(component)
        mock_strategy.render.assert_called_once_with(component)

    def test_render_component_value_error(self) -> None:
        """Test that ValueError from renderer is re-raised."""
        component = ComponentDataBase(component="invalid-component", id="test-id")

        mock_strategy = Mock(spec=RenderStrategyBase)
        mock_strategy.render.side_effect = ValueError("Component not supported")

        mock_factory = Mock(spec=StrategyFactory)
        mock_factory.get_render_strategy.return_value = mock_strategy

        with pytest.raises(ValueError, match="Component not supported"):
            render_component(component, mock_factory)

    def test_render_component_general_exception(self) -> None:
        """Test that general exceptions from renderer are re-raised."""
        component = ComponentDataBase(component="one-card", id="test-id")

        mock_strategy = Mock(spec=RenderStrategyBase)
        mock_strategy.render.side_effect = RuntimeError("Rendering failed")

        mock_factory = Mock(spec=StrategyFactory)
        mock_factory.get_render_strategy.return_value = mock_strategy

        with pytest.raises(RuntimeError, match="Rendering failed"):
            render_component(component, mock_factory)

    def test_render_component_with_json_factory(self) -> None:
        """Test rendering with actual JsonStrategyFactory."""
        component = ComponentDataBase(component="one-card", id="test-id-456")

        factory = JsonStrategyFactory()
        result = render_component(component, factory)

        assert isinstance(result, UIBlockRendering)
        assert result.id == "test-id-456"
        assert result.component_system == "json"
        assert result.mime_type == "application/json"
        # The content should be valid JSON
        assert isinstance(result.content, str)
        assert "test-id-456" in result.content or "one-card" in result.content
