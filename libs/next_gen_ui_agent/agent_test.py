import os
from unittest.mock import patch

import pytest
from next_gen_ui_agent.agent import NextGenUIAgent
from next_gen_ui_agent.component_selection import (
    OnestepLLMCallComponentSelectionStrategy,
)
from next_gen_ui_agent.component_selection_twostep import (
    TwostepLLMCallComponentSelectionStrategy,
)
from next_gen_ui_agent.types import AgentConfig, InputData
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

    assert result[0].mime_type == "application/json"
    assert result[0].component_system == "json"
    assert result[0].id == c.id

    r = from_json(result[0].content)
    assert r["component"] == "one-card"


def test_renderers() -> None:
    agent = NextGenUIAgent()
    assert agent.renderers == ["json"]


class TestCreateComponentSelectionStrategy:
    """Test suite for _create_component_selection_strategy method."""

    def setup_method(self):
        """Setup method to reset environment variables."""
        # Clear environment variable before each test
        if "NEXT_GEN_UI_AGENT_USE_ALL_COMPONENTS" in os.environ:
            del os.environ["NEXT_GEN_UI_AGENT_USE_ALL_COMPONENTS"]

    def teardown_method(self):
        """Teardown method to clean up environment variables."""
        # Clear environment variable after each test
        if "NEXT_GEN_UI_AGENT_USE_ALL_COMPONENTS" in os.environ:
            del os.environ["NEXT_GEN_UI_AGENT_USE_ALL_COMPONENTS"]

    def test_default_strategy(self):
        """Test that default strategy returns OnestepLLMCallComponentSelectionStrategy."""
        config = AgentConfig()
        agent = NextGenUIAgent(config)
        strategy = agent._create_component_selection_strategy()

        assert isinstance(strategy, OnestepLLMCallComponentSelectionStrategy)
        assert strategy.unsupported_components is False

    def test_one_llm_call_strategy(self):
        """Test that one_llm_call strategy returns OnestepLLMCallComponentSelectionStrategy."""
        config = AgentConfig(component_selection_strategy="one_llm_call")
        agent = NextGenUIAgent(config)
        strategy = agent._create_component_selection_strategy()

        assert isinstance(strategy, OnestepLLMCallComponentSelectionStrategy)
        assert strategy.unsupported_components is False

    def test_two_llm_calls_strategy(self):
        """Test that two_llm_calls strategy returns TwostepLLMCallComponentSelectionStrategy."""
        config = AgentConfig(component_selection_strategy="two_llm_calls")
        agent = NextGenUIAgent(config)
        strategy = agent._create_component_selection_strategy()

        assert isinstance(strategy, TwostepLLMCallComponentSelectionStrategy)
        assert strategy.unsupported_components is False

    def test_unknown_strategy_raises_value_error(self):
        """Test that unknown strategy raises ValueError."""
        config = AgentConfig(component_selection_strategy="unknown_strategy")
        agent = NextGenUIAgent()  # Use default config to avoid error in __init__
        agent.config = config  # Set the invalid config after initialization

        with pytest.raises(
            ValueError, match="Unknown component_selection_strategy: unknown_strategy"
        ):
            agent._create_component_selection_strategy()

    def test_unsupported_components_from_config_true(self):
        """Test unsupported_components=True from config."""
        config = AgentConfig(unsupported_components=True)
        agent = NextGenUIAgent(config)
        strategy = agent._create_component_selection_strategy()

        assert strategy.unsupported_components is True

    def test_unsupported_components_from_config_false(self):
        """Test unsupported_components=False from config."""
        config = AgentConfig(unsupported_components=False)
        agent = NextGenUIAgent(config)
        strategy = agent._create_component_selection_strategy()

        assert strategy.unsupported_components is False

    @patch.dict(os.environ, {"NEXT_GEN_UI_AGENT_USE_ALL_COMPONENTS": "true"})
    def test_unsupported_components_from_env_true(self):
        """Test unsupported_components=True from environment variable."""
        config = AgentConfig()
        agent = NextGenUIAgent(config)
        strategy = agent._create_component_selection_strategy()

        assert strategy.unsupported_components is True

    @patch.dict(os.environ, {"NEXT_GEN_UI_AGENT_USE_ALL_COMPONENTS": "false"})
    def test_unsupported_components_from_env_false(self):
        """Test unsupported_components=False from environment variable."""
        config = AgentConfig()
        agent = NextGenUIAgent(config)
        strategy = agent._create_component_selection_strategy()

        assert strategy.unsupported_components is False

    def test_unsupported_components_env_case_insensitive(self):
        """Test environment variable case insensitivity."""
        # Test uppercase TRUE
        with patch.dict(os.environ, {"NEXT_GEN_UI_AGENT_USE_ALL_COMPONENTS": "TRUE"}):
            config = AgentConfig()
            agent = NextGenUIAgent(config)
            strategy = agent._create_component_selection_strategy()
            assert strategy.unsupported_components is True

        # Test mixed case True
        with patch.dict(os.environ, {"NEXT_GEN_UI_AGENT_USE_ALL_COMPONENTS": "True"}):
            config = AgentConfig()
            agent = NextGenUIAgent(config)
            strategy = agent._create_component_selection_strategy()
            assert strategy.unsupported_components is True

    def test_config_precedence_over_env(self):
        """Test that config takes precedence over environment variable."""
        with patch.dict(os.environ, {"NEXT_GEN_UI_AGENT_USE_ALL_COMPONENTS": "true"}):
            config = AgentConfig(unsupported_components=False)
            agent = NextGenUIAgent(config)
            strategy = agent._create_component_selection_strategy()

            # Config should take precedence over environment variable
            assert strategy.unsupported_components is False

    def test_empty_config(self):
        """Test behavior with empty config."""
        config = AgentConfig()
        agent = NextGenUIAgent(config)
        strategy = agent._create_component_selection_strategy()

        # Should default to "default" strategy and unsupported_components=False
        assert isinstance(strategy, OnestepLLMCallComponentSelectionStrategy)
        assert strategy.unsupported_components is False

    def test_combined_config_and_env(self):
        """Test combination of config strategy and environment unsupported_components."""
        with patch.dict(os.environ, {"NEXT_GEN_UI_AGENT_USE_ALL_COMPONENTS": "true"}):
            config = AgentConfig(component_selection_strategy="two_llm_calls")
            agent = NextGenUIAgent(config)
            strategy = agent._create_component_selection_strategy()

            # Should use config strategy and environment unsupported_components
            assert isinstance(strategy, TwostepLLMCallComponentSelectionStrategy)
            assert strategy.unsupported_components is True


def test_method__select_hand_build_component_EXISTING() -> None:
    agent = NextGenUIAgent(
        config=AgentConfig(
            hand_build_components_mapping={"my.type": "one-card-special"}
        )
    )
    input_data = InputData(id="1", data="{}", type="my.type")
    result = agent._select_hand_build_component(input_data)
    assert result is not None
    assert result.component == "hand-build-component"
    assert result.id == "1"
    assert result.title == ""
    assert result.component_type == "one-card-special"


def test_method__select_hand_build_component_NON_EXISTING() -> None:
    agent = NextGenUIAgent(
        config=AgentConfig(
            hand_build_components_mapping={"my.type": "one-card-special"}
        )
    )
    input_data = InputData(id="1", data="{}", type="my.type2")
    result = agent._select_hand_build_component(input_data)
    assert result is None


def test_method__select_hand_build_component_NOT_CONFIGURED() -> None:
    agent = NextGenUIAgent(config=AgentConfig())
    input_data = InputData(id="1", data="{}", type="my.type2")
    result = agent._select_hand_build_component(input_data)
    assert result is None


if __name__ == "__main__":
    test_design_system_handler_json()
