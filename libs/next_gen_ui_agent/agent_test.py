import os
from unittest.mock import patch

import pytest
from next_gen_ui_agent.agent import NextGenUIAgent
from next_gen_ui_agent.component_selection_llm_onestep import (
    OnestepLLMCallComponentSelectionStrategy,
)
from next_gen_ui_agent.component_selection_llm_twostep import (
    TwostepLLMCallComponentSelectionStrategy,
)
from next_gen_ui_agent.data_transform.data_transformer_utils import sanitize_data_path
from next_gen_ui_agent.types import (
    AgentConfig,
    AgentConfigComponent,
    AgentConfigDataType,
    AgentInput,
    DataField,
    InputData,
    UIBlockComponentMetadata,
    UIBlockConfiguration,
    UIComponentMetadata,
    UIComponentMetadataHandBuildComponent,
)
from next_gen_ui_testing.data_after_transformation import get_transformed_component
from next_gen_ui_testing.model import MockedInference
from pydantic_core import ValidationError, from_json


def test_config_yaml_str() -> None:
    config_yaml = "component_system: json\ninput_data_json_wrapping: false"
    agent = NextGenUIAgent(config=config_yaml)
    assert agent.config.component_system == "json"
    assert agent._component_selection_strategy.input_data_json_wrapping is False


def test_config_input_data_json_wrapping_default() -> None:
    agent = NextGenUIAgent()
    # check that input_data_json_wrapping is True by default
    assert agent._component_selection_strategy.input_data_json_wrapping is True


class TestRenderingStep:
    def test_design_system_handler_wrong_name(self) -> None:
        agent = NextGenUIAgent()
        with pytest.raises(
            Exception,
            match="configured component system 'bad' is not present in extension_manager. Make sure you install appropriate dependency",
        ):
            agent.design_system_handler(list(), "bad")

    def test_design_system_handler_json(self) -> None:
        agent = NextGenUIAgent()
        c = get_transformed_component()
        result = agent.design_system_handler([c], "json")

        assert result[0].mime_type == "application/json"
        assert result[0].component_system == "json"
        assert result[0].id == c.id

        r = from_json(result[0].content)
        assert r["component"] == "one-card"

    def test_renderers(self) -> None:
        agent = NextGenUIAgent()
        assert len(agent.renderers) > 0
        assert agent.renderers.index("json") == 0


class TestComponentSelection:
    @pytest.mark.asyncio
    async def test_component_selection_hbc_mixed(self) -> None:
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
    async def test_component_selection_hbc_only(self) -> None:
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
    async def test_component_selection_llm_only(self) -> None:
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
    async def test_component_selection_llm_inference_necessar(self) -> None:
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
        with pytest.raises(
            ValidationError,
            match="1 validation error for AgentConfig\ncomponent_selection_strategy\n  Input should be 'one_llm_call' or 'two_llm_calls'",
        ):
            AgentConfig(component_selection_strategy="unknown_strategy")

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


class TestComponentSelectionDataTransformation:
    """Test suite for input data transformation in component selection step."""

    @pytest.mark.asyncio
    async def test_component_selection_DATA_TRANSFORMATION_CONFIGURED_PER_TYPE_YAML(
        self,
    ) -> None:
        # HBC used here so we do not need inference and we also see that selection per type works correctly
        agent = NextGenUIAgent(
            config=AgentConfig(
                data_types={
                    "my.type": AgentConfigDataType(
                        data_transformer="yaml",
                        components=[AgentConfigComponent(component="one-card-special")],
                    )
                }
            )
        )
        input_data = InputData(id="1", data="- name: MYNAME", type="my.type")

        input = AgentInput(user_prompt="Test prompt", input_data=[input_data])
        result = await agent.component_selection(input=input)
        assert result is not None
        r = result[0]
        assert r.component == "hand-build-component"
        assert r.json_data is not None
        assert r.json_data == [{"name": "MYNAME"}]

    @pytest.mark.asyncio
    async def test_component_selection_DATA_TRANSFORMATION_PER_TYPE_NOT_CONFIGURED_DATA_JSON(
        self,
    ) -> None:
        # HBC used here so we do not need inference and we also see that selection per type works correctly
        agent = NextGenUIAgent(
            config=AgentConfig(
                data_types={
                    "my.type": AgentConfigDataType(
                        components=[AgentConfigComponent(component="one-card-special")]
                    )
                }
            )
        )
        input_data = InputData(id="1", data='{"name": "MYNAME"}', type="my.type")

        input = AgentInput(user_prompt="Test prompt", input_data=[input_data])
        result = await agent.component_selection(input=input)
        assert result is not None
        r = result[0]
        assert r.component == "hand-build-component"
        assert r.json_data is not None
        assert r.json_data == {"name": "MYNAME"}

    @pytest.mark.asyncio
    async def test_component_selection_DATA_TRANSFORMATION_NOT_CONFIGURED_DATA_INVALID(
        self,
    ) -> None:
        # HBC used here so we do not need inference and we also see that selection per type works correctly
        agent = NextGenUIAgent(
            config=AgentConfig(
                data_types={
                    "my.type": AgentConfigDataType(
                        components=[AgentConfigComponent(component="one-card-special")]
                    )
                }
            )
        )
        input_data = InputData(id="1", data="- name: MYNAME", type="my.type")

        input = AgentInput(user_prompt="Test prompt", input_data=[input_data])
        with pytest.raises(ValueError, match="Invalid JSON format of the Input Data: "):
            await agent.component_selection(input=input)

    @pytest.mark.asyncio
    async def test_component_selection_DATA_TRANSFORMATION_CONFIGURED_YAML(
        self,
    ) -> None:
        # HBC used here so we do not need inference and we also see that selection per type works correctly
        agent = NextGenUIAgent(
            config=AgentConfig(
                data_transformer="yaml",
                data_types={
                    "my.type": AgentConfigDataType(
                        components=[AgentConfigComponent(component="one-card-special")],
                    )
                },
            )
        )
        input_data = InputData(id="1", data="- name: MYNAME", type="my.type")

        input = AgentInput(user_prompt="Test prompt", input_data=[input_data])
        result = await agent.component_selection(input=input)
        assert result is not None
        r = result[0]
        assert r.component == "hand-build-component"
        assert r.json_data is not None
        assert r.json_data == [{"name": "MYNAME"}]


class TestComponentSelectionWrapping:
    """Test suite for input data transformation in component selection step - wrapping."""

    @pytest.mark.asyncio
    async def test_component_selection_WRAPPING(self) -> None:
        agent = NextGenUIAgent(config=AgentConfig(input_data_json_wrapping=True))

        input_data = InputData(id="1", data='[{"title": "Toy Story"}]', type="my_type")

        input = AgentInput(user_prompt="Test prompt", input_data=[input_data])
        mocked_llm_component = UIComponentMetadata(
            component="one-card",
            id="1",
            title="Toy Story",
            fields=[DataField(name="Title", data_path="movie.title")],
        )

        result = await agent.component_selection(
            input=input, inference=MockedInference(mocked_llm_component)
        )
        assert result is not None
        r = result[0]
        assert r.component == "one-card"
        assert r.json_data is not None
        assert r.json_data == {"my_type": [{"title": "Toy Story"}]}


class TestRefreshComponent:
    """Test suite for refresh_component method."""

    @pytest.mark.asyncio
    async def test_refresh_component_missing_input_data_transformer_name(self) -> None:
        agent = NextGenUIAgent(config=AgentConfig())
        input_data = InputData(id="1", data='[{"title": "Toy Story"}]', type="my_type")
        block_configuration = UIBlockConfiguration(
            component_metadata=UIComponentMetadata(
                component="one-card",
                id="1",
                title="Toy Story",
                fields=[DataField(name="Title", data_path="movie.title")],
            ),
            json_wrapping_field_name="my_type",
        )
        with pytest.raises(
            KeyError,
            match="Input data transformer name missing in the block configuration",
        ):
            await agent.refresh_component(input_data, block_configuration)

    @pytest.mark.asyncio
    async def test_refresh_component_missing_component_metadata(self) -> None:
        agent = NextGenUIAgent(config=AgentConfig())
        input_data = InputData(id="1", data='[{"title": "Toy Story"}]', type="my_type")
        block_configuration = UIBlockConfiguration(
            input_data_transformer_name="json", json_wrapping_field_name="my_type"
        )
        with pytest.raises(
            KeyError, match="Component metadata missing in the block configuration"
        ):
            await agent.refresh_component(input_data, block_configuration)

    @pytest.mark.asyncio
    async def test_refresh_component_OK_without_wrapping(self) -> None:
        agent = NextGenUIAgent(config=AgentConfig())
        input_data = InputData(id="1", data='[{"title": "Toy Story"}]', type="my_type")
        block_configuration = UIBlockConfiguration(
            component_metadata=UIBlockComponentMetadata(
                component="one-card",
                id="1",
                title="Toy Story",
                fields=[DataField(name="Title", data_path="$..title")],
            ),
            input_data_transformer_name="json",
        )
        result = await agent.refresh_component(input_data, block_configuration)
        assert result.component == "one-card"
        assert result.id == "1"
        assert result.title == "Toy Story"
        assert result.fields is not None
        assert len(result.fields) == 1
        assert result.fields[0].data_path == "$..title"
        assert result.fields[0].name == "Title"
        assert result.json_data == [{"title": "Toy Story"}]
        assert result.input_data_transformer_name == "json"
        assert result.json_wrapping_field_name is None

    @pytest.mark.asyncio
    async def test_refresh_component_OK_with_wrapping(self) -> None:
        agent = NextGenUIAgent(config=AgentConfig())
        input_data = InputData(id="1", data='[{"title": "Toy Story"}]', type="my_type")
        block_configuration = UIBlockConfiguration(
            component_metadata=UIBlockComponentMetadata(
                component="one-card",
                id="1",
                title="Toy Story",
                fields=[DataField(name="Title", data_path="$..my_type.title")],
            ),
            input_data_transformer_name="json",
            json_wrapping_field_name="my_type",
        )
        result = await agent.refresh_component(input_data, block_configuration)
        assert result.component == "one-card"
        assert result.id == "1"
        assert result.title == "Toy Story"
        assert result.fields is not None
        assert len(result.fields) == 1
        assert result.fields[0].data_path == "$..my_type.title"
        assert result.fields[0].name == "Title"
        assert result.json_data == {"my_type": [{"title": "Toy Story"}]}
        assert result.input_data_transformer_name == "json"
        assert result.json_wrapping_field_name == "my_type"


class TestConstructUIBlockConfiguration:
    """Test suite for construct_UIBlockConfiguration method."""

    def test_construct_UIBlockConfiguration_all_info(self) -> None:
        agent = NextGenUIAgent(config=AgentConfig())
        input_data = InputData(id="1", data='[{"title": "Toy Story"}]', type="my_type")
        component_metadata = UIComponentMetadata(
            component="one-card",
            id="1",
            title="Toy Story",
            fields=[
                DataField(name="Title", data_path="$..movie.title"),
                DataField(name="Year", data_path="['movie']['year']"),
            ],
            input_data_transformer_name="json",
            json_wrapping_field_name="my_type",
            json_data=[{"title": "Toy Story"}],
            reasonForTheComponentSelection="One item available in the data",
            confidenceScore="100%",
        )
        configuration = agent.construct_UIBlockConfiguration(
            input_data, component_metadata
        )
        assert configuration.data_type == "my_type"
        assert configuration.input_data_transformer_name == "json"
        assert configuration.json_wrapping_field_name == "my_type"
        assert configuration.component_metadata == component_metadata
        assert configuration.component_metadata.fields[
            0
        ].data_path == sanitize_data_path("movie.title")
        assert configuration.component_metadata.fields[1].data_path == "$..movie.year"

    def test_construct_UIBlockConfiguration_min_info(self) -> None:
        agent = NextGenUIAgent(config=AgentConfig())
        input_data = InputData(id="1", data='[{"title": "Toy Story"}]')
        component_metadata = UIComponentMetadata(
            component="one-card",
            id="1",
            title="Toy Story",
            fields=[DataField(name="Title", data_path="movie.title")],
            input_data_transformer_name="yaml",
            json_wrapping_field_name=None,
            json_data=[{"title": "Toy Story"}],
            reasonForTheComponentSelection="One item available in the data",
            confidenceScore="100%",
        )
        configuration = agent.construct_UIBlockConfiguration(
            input_data, component_metadata
        )
        assert configuration.data_type is None
        assert configuration.input_data_transformer_name == "yaml"
        assert configuration.json_wrapping_field_name is None
        assert configuration.component_metadata == component_metadata
        assert configuration.component_metadata.fields[
            0
        ].data_path == sanitize_data_path("movie.title")
