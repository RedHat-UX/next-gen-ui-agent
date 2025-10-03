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
from next_gen_ui_agent.types import (
    AgentConfig,
    AgentConfigComponent,
    AgentConfigDataType,
    AgentInput,
    DataField,
    InputData,
    UIComponentMetadata,
    UIComponentMetadataHandBuildComponent,
)
from next_gen_ui_testing.data_after_transformation import get_transformed_component
from next_gen_ui_testing.model import MockedInference
from pydantic_core import from_json


def test_config_yaml_str() -> None:
    config_yaml = "component_system: json\ninput_data_json_wrapping: false"
    agent = NextGenUIAgent(config=config_yaml)
    assert agent.config.component_system == "json"
    assert agent._component_selection_strategy.input_data_json_wrapping is False


def test_config_input_data_json_wrapping_default() -> None:
    agent = NextGenUIAgent()
    # check that input_data_json_wrapping is True by default
    assert agent._component_selection_strategy.input_data_json_wrapping is True


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
    assert len(agent.renderers) > 0
    assert agent.renderers.index("json") == 0


@pytest.mark.asyncio
async def test_component_selection_hbc_mixed() -> None:
    """Test that hand-build components and LLM inferenced components are processed correctly in the same run."""
    mocked_llm_component = UIComponentMetadata(
        component="one-card",
        id="1",
        title="Toy Story",
        fields=[DataField(name="Title", data_path="movie.title")],
    )
    agent = NextGenUIAgent(
        config=AgentConfig(
            data_types={
                "my.type": AgentConfigDataType(
                    components=[AgentConfigComponent(component="one-card-special")]
                ),
                "other.type": AgentConfigDataType(
                    components=[AgentConfigComponent(component="table-special")]
                ),
            }
        )
    )
    input = AgentInput(
        user_prompt="Test prompt",
        input_data=[
            InputData(id="2", data='{"title": "Toy Story"}'),
            InputData(id="1", data='{"title": "HBC data"}', type="my.type"),
            InputData(id="3", data='{"title": "Toy Story"}'),
            InputData(id="4", data='{"title": "Toy Story"}', type="other.type"),
            InputData(id="5", data='{"title": "Toy Story"}', type="unmaped.type"),
        ],
    )
    components = await agent.component_selection(
        input=input, inference=MockedInference(mocked_llm_component)
    )
    assert len(components) == 5
    # order of components in result is implementation detail of the `agent.component_selection` method!
    assert isinstance(components[0], UIComponentMetadataHandBuildComponent)
    assert components[0].component == "hand-build-component"
    assert components[0].id == "1"
    assert components[0].component_type == "one-card-special"
    assert isinstance(components[1], UIComponentMetadataHandBuildComponent)
    assert components[1].component == "hand-build-component"
    assert components[1].id == "4"
    assert components[1].component_type == "table-special"
    # other components come from the inference
    assert components[2].component == "one-card"
    assert components[2].id == "2"
    assert components[2].title == "Toy Story"
    # inference result is the same, but id differs
    assert components[3].component == "one-card"
    assert components[3].id == "3"
    assert components[3].title == "Toy Story"
    # inference result is the same, but id differs - unmaped type goes through LLM inference
    assert components[4].component == "one-card"
    assert components[4].id == "5"
    assert components[4].title == "Toy Story"


@pytest.mark.asyncio
async def test_component_selection_hbc_only() -> None:
    """Test that hand-build components alone are selected correctly."""
    agent = NextGenUIAgent(
        config=AgentConfig(
            data_types={
                "my.type": AgentConfigDataType(
                    components=[AgentConfigComponent(component="one-card-special")]
                ),
                "other.type": AgentConfigDataType(
                    components=[AgentConfigComponent(component="table-special")]
                ),
            }
        )
    )
    input = AgentInput(
        user_prompt="Test prompt",
        input_data=[
            # mapped HBC
            InputData(id="1", data='{"title": "HBC data"}', type="my.type"),
            # HBC directly requested by component type, it has precedence over type mapping (tested here also)!
            InputData(
                id="3",
                data='{"title": "Toy Story"}',
                type="other.type",
                hand_build_component_type="provided-special",
            ),
            # mapped HBC
            InputData(id="4", data='{"title": "Toy Story"}', type="other.type"),
        ],
    )
    # inference is not necessary!
    components = await agent.component_selection(input=input)
    assert len(components) == 3
    # order of components in result is implementation detail of the `agent.component_selection` method!
    assert isinstance(components[0], UIComponentMetadataHandBuildComponent)
    assert components[0].component == "hand-build-component"
    assert components[0].id == "1"
    assert components[0].component_type == "one-card-special"
    assert isinstance(components[1], UIComponentMetadataHandBuildComponent)
    assert components[1].component == "hand-build-component"
    assert components[1].id == "3"
    assert components[1].component_type == "provided-special"
    assert isinstance(components[2], UIComponentMetadataHandBuildComponent)
    assert components[2].component == "hand-build-component"
    assert components[2].id == "4"
    assert components[2].component_type == "table-special"


@pytest.mark.asyncio
async def test_component_selection_llm_only() -> None:
    """Test that LLM inference components are processed correctly, without HBC even configured."""
    mocked_llm_component = UIComponentMetadata(
        component="one-card",
        id="1",
        title="Toy Story",
        fields=[DataField(name="Title", data_path="movie.title")],
    )
    agent = NextGenUIAgent(config=AgentConfig())
    input = AgentInput(
        user_prompt="Test prompt",
        input_data=[
            InputData(id="2", data='{"title": "Toy Story"}'),
            InputData(id="3", data='{"title": "Toy Story"}'),
            InputData(id="5", data='{"title": "Toy Story"}', type="unmaped.type"),
        ],
    )
    components = await agent.component_selection(
        input=input, inference=MockedInference(mocked_llm_component)
    )
    assert len(components) == 3
    # order of components in result is implementation detail of the `agent.component_selection` method!
    assert components[0].component == "one-card"
    assert components[0].id == "2"
    assert components[0].title == "Toy Story"
    # inference result is the same, but id differs
    assert components[1].component == "one-card"
    assert components[1].id == "3"
    assert components[1].title == "Toy Story"
    # inference result is the same, but id differs - unmaped type goes through LLM inference
    assert components[2].component == "one-card"
    assert components[2].id == "5"
    assert components[2].title == "Toy Story"


@pytest.mark.asyncio
async def test_component_selection_llm_inference_necessar() -> None:
    """Test that LLM inference object is required when inference is necessary."""
    agent = NextGenUIAgent(config=AgentConfig())
    input = AgentInput(
        user_prompt="Test prompt",
        input_data=[
            InputData(id="2", data='{"title": "Toy Story"}'),
        ],
    )
    with pytest.raises(
        ValueError,
        match="config field 'inference' is not defined neither in input parameter nor agent's config",
    ):
        await agent.component_selection(input=input)


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
        agent = NextGenUIAgent(config=config)
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
        agent = NextGenUIAgent(config=config)
        strategy = agent._create_component_selection_strategy()

        assert strategy.unsupported_components is True

    def test_unsupported_components_from_config_false(self):
        """Test unsupported_components=False from config."""
        config = AgentConfig(unsupported_components=False)
        agent = NextGenUIAgent(config=config)
        strategy = agent._create_component_selection_strategy()

        assert strategy.unsupported_components is False

    @patch.dict(os.environ, {"NEXT_GEN_UI_AGENT_USE_ALL_COMPONENTS": "true"})
    def test_unsupported_components_from_env_true(self):
        """Test unsupported_components=True from environment variable."""
        config = AgentConfig()
        agent = NextGenUIAgent(config=config)
        strategy = agent._create_component_selection_strategy()

        assert strategy.unsupported_components is True

    @patch.dict(os.environ, {"NEXT_GEN_UI_AGENT_USE_ALL_COMPONENTS": "false"})
    def test_unsupported_components_from_env_false(self):
        """Test unsupported_components=False from environment variable."""
        config = AgentConfig()
        agent = NextGenUIAgent(config=config)
        strategy = agent._create_component_selection_strategy()

        assert strategy.unsupported_components is False

    def test_unsupported_components_env_case_insensitive(self):
        """Test environment variable case insensitivity."""
        # Test uppercase TRUE
        with patch.dict(os.environ, {"NEXT_GEN_UI_AGENT_USE_ALL_COMPONENTS": "TRUE"}):
            config = AgentConfig()
            agent = NextGenUIAgent(config=config)
            strategy = agent._create_component_selection_strategy()
            assert strategy.unsupported_components is True

        # Test mixed case True
        with patch.dict(os.environ, {"NEXT_GEN_UI_AGENT_USE_ALL_COMPONENTS": "True"}):
            config = AgentConfig()
            agent = NextGenUIAgent(config=config)
            strategy = agent._create_component_selection_strategy()
            assert strategy.unsupported_components is True

    def test_config_precedence_over_env(self):
        """Test that config takes precedence over environment variable."""
        with patch.dict(os.environ, {"NEXT_GEN_UI_AGENT_USE_ALL_COMPONENTS": "true"}):
            config = AgentConfig(unsupported_components=False)
            agent = NextGenUIAgent(config=config)
            strategy = agent._create_component_selection_strategy()

            # Config should take precedence over environment variable
            assert strategy.unsupported_components is False

    def test_empty_config(self):
        """Test behavior with empty config."""
        config = AgentConfig()
        agent = NextGenUIAgent(config=config)
        strategy = agent._create_component_selection_strategy()

        # Should default to "default" strategy and unsupported_components=False
        assert isinstance(strategy, OnestepLLMCallComponentSelectionStrategy)
        assert strategy.unsupported_components is False

    def test_combined_config_and_env(self):
        """Test combination of config strategy and environment unsupported_components."""
        with patch.dict(os.environ, {"NEXT_GEN_UI_AGENT_USE_ALL_COMPONENTS": "true"}):
            config = AgentConfig(component_selection_strategy="two_llm_calls")
            agent = NextGenUIAgent(config=config)
            strategy = agent._create_component_selection_strategy()

            # Should use config strategy and environment unsupported_components
            assert isinstance(strategy, TwostepLLMCallComponentSelectionStrategy)
            assert strategy.unsupported_components is True


def test_method__select_hand_build_component_EXISTING() -> None:
    agent = NextGenUIAgent(
        config=AgentConfig(
            data_types={
                "my.type": AgentConfigDataType(
                    components=[AgentConfigComponent(component="one-card-special")]
                )
            }
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
            data_types={
                "my.type": AgentConfigDataType(
                    components=[AgentConfigComponent(component="one-card-special")]
                )
            }
        )
    )
    input_data = InputData(id="1", data="{}", type="my.type2")
    result = agent._select_hand_build_component(input_data)
    assert result is None


def test_method__select_hand_build_component_NO_TYPE_IN_INPUT_DATA() -> None:
    agent = NextGenUIAgent(
        config=AgentConfig(
            data_types={
                "my.type": AgentConfigDataType(
                    components=[AgentConfigComponent(component="one-card-special")]
                )
            }
        )
    )
    input_data = InputData(id="1", data="{}")
    result = agent._select_hand_build_component(input_data)
    assert result is None


def test_method__select_hand_build_component_NOT_CONFIGURED() -> None:
    agent = NextGenUIAgent(config=AgentConfig())
    input_data = InputData(id="1", data="{}", type="my.type2")
    result = agent._select_hand_build_component(input_data)
    assert result is None


if __name__ == "__main__":
    test_design_system_handler_json()
