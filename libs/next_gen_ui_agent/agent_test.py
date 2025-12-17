from typing import cast

import pytest
from next_gen_ui_agent.agent import NextGenUIAgent
from next_gen_ui_agent.component_selection_llm_onestep import (
    OnestepLLMCallComponentSelectionStrategy,
)
from next_gen_ui_agent.component_selection_llm_twostep import (
    TwostepLLMCallComponentSelectionStrategy,
)
from next_gen_ui_agent.data_transform.data_transformer_utils import (
    generate_field_id,
    sanitize_data_path,
)
from next_gen_ui_agent.data_transform.types import (
    ComponentDataBase,
    ComponentDataOneCard,
)
from next_gen_ui_agent.types import (
    AgentConfig,
    AgentConfigComponent,
    AgentConfigDataType,
    DataField,
    InputData,
    UIBlockComponentMetadata,
    UIBlockConfiguration,
    UIComponentMetadata,
    UIComponentMetadataHandBuildComponent,
)
from next_gen_ui_testing.data_after_transformation import get_transformed_component
from next_gen_ui_testing.model import MockedExceptionInference, MockedInference
from pydantic_core import ValidationError, from_json


class TestAgentConfiguration:
    def test_config_yaml_str(self) -> None:
        config_yaml = "component_system: json\ninput_data_json_wrapping: false"
        agent = NextGenUIAgent(config=config_yaml)
        assert agent.config.component_system == "json"
        assert agent._component_selection_strategy.input_data_json_wrapping is False

    def test_config_input_data_json_wrapping_default(self) -> None:
        agent = NextGenUIAgent()
        # check that input_data_json_wrapping is True by default
        assert agent._component_selection_strategy.input_data_json_wrapping is True

    def test_config_component_system_not_configured(self) -> None:
        agent = NextGenUIAgent()
        assert agent.config.component_system == "json"

    def test_config_component_system_configured(self) -> None:
        agent = NextGenUIAgent(config=AgentConfig(component_system="json"))
        assert agent.config.component_system == "json"

    def test_config_component_system_unknown(self) -> None:
        with pytest.raises(
            ValueError,
            match="Configured component system 'unknown' is not found. Make sure you install appropriate dependency.",
        ):
            NextGenUIAgent(config=AgentConfig(component_system="unknown"))


class TestSelectComponent:
    @pytest.mark.asyncio
    async def test_select_component_hbc_mapped(self) -> None:
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
        input_data = InputData(id="1", data='{"title": "HBC data"}', type="my.type")

        # inference is not necessary!
        component = await agent.select_component(
            user_prompt="Test prompt", input_data=input_data
        )
        # order of components in result is implementation detail of the `agent.component_selection` method!
        assert isinstance(component, UIComponentMetadataHandBuildComponent)
        assert component.component == "hand-build-component"
        assert component.id == "1"
        assert component.component_type == "one-card-special"

    @pytest.mark.asyncio
    async def test_select_component_hbc_requested(self) -> None:
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
        input_data = InputData(
            id="3",
            data='{"title": "Toy Story"}',
            type="other.type",
            hand_build_component_type="provided-special",
        )

        # inference is not necessary!
        component = await agent.select_component(
            user_prompt="Test prompt", input_data=input_data
        )
        # order of components in result is implementation detail of the `agent.component_selection` method!
        assert isinstance(component, UIComponentMetadataHandBuildComponent)
        assert component.component == "hand-build-component"
        assert component.id == "3"
        assert component.component_type == "provided-special"

    @pytest.mark.asyncio
    async def test_select_component_dynamic(self) -> None:
        """Test that LLM inference components are processed correctly, without HBC even configured."""
        mocked_llm_component = UIComponentMetadata(
            component="one-card",
            id="1",
            title="Toy Story",
            fields=[DataField(name="Title", data_path="movie.title")],
        )
        agent = NextGenUIAgent(config=AgentConfig())
        input_data = InputData(id="1", data='{"title": "Toy Story"}')

        component = await agent.select_component(
            user_prompt="Test prompt",
            input_data=input_data,
            inference=MockedInference(mocked_llm_component),
        )
        # order of components in result is implementation detail of the `agent.component_selection` method!
        assert component.component == "one-card"
        assert component.id == "1"
        assert component.title == "Toy Story"

    @pytest.mark.asyncio
    async def test_component_selection_llm_inference_necessar(self) -> None:
        """Test that LLM inference object is required when inference is necessary."""
        agent = NextGenUIAgent(config=AgentConfig())
        input_data = InputData(id="2", data='{"title": "Toy Story"}')
        with pytest.raises(
            ValueError,
            match="Inference is not defined neither as an input parameter nor as an agent's config",
        ):
            await agent.select_component(
                user_prompt="Test prompt", input_data=input_data
            )

    @pytest.mark.asyncio
    async def test_select_component_llm_inference_error(self) -> None:
        """Test that LLM inference error is propagated when LLM inference fails."""

        agent = NextGenUIAgent(config=AgentConfig())
        input_data = InputData(id="1", data='{"title": "Toy Story"}')

        with pytest.raises(RuntimeError, match="LLM inference error"):
            await agent.select_component(
                user_prompt="Test prompt",
                input_data=input_data,
                inference=MockedExceptionInference(RuntimeError("LLM inference error")),
            )


class TestCreateComponentSelectionStrategy:
    """Test suite for _create_component_selection_strategy method."""

    def test_default_strategy(self):
        """Test that default strategy returns OnestepLLMCallComponentSelectionStrategy."""
        config = AgentConfig()
        agent = NextGenUIAgent(config)
        strategy = agent._create_component_selection_strategy()

        assert isinstance(strategy, OnestepLLMCallComponentSelectionStrategy)

    def test_one_llm_call_strategy(self):
        """Test that one_llm_call strategy returns OnestepLLMCallComponentSelectionStrategy."""
        config = AgentConfig(component_selection_strategy="one_llm_call")
        agent = NextGenUIAgent(config)
        strategy = agent._create_component_selection_strategy()

        assert isinstance(strategy, OnestepLLMCallComponentSelectionStrategy)

    def test_two_llm_calls_strategy(self):
        """Test that two_llm_calls strategy returns TwostepLLMCallComponentSelectionStrategy."""
        config = AgentConfig(component_selection_strategy="two_llm_calls")
        agent = NextGenUIAgent(config=config)
        strategy = agent._create_component_selection_strategy()

        assert isinstance(strategy, TwostepLLMCallComponentSelectionStrategy)

    def test_unknown_strategy_raises_value_error(self):
        """Test that unknown strategy raises ValueError."""
        with pytest.raises(
            ValidationError,
            match="1 validation error for AgentConfig\ncomponent_selection_strategy\n  Input should be 'one_llm_call' or 'two_llm_calls'",
        ):
            AgentConfig(component_selection_strategy="unknown_strategy")

    def test_empty_config(self):
        """Test behavior with empty config."""
        config = AgentConfig()
        agent = NextGenUIAgent(config=config)
        strategy = agent._create_component_selection_strategy()

        # Should default to "default" strategy
        assert isinstance(strategy, OnestepLLMCallComponentSelectionStrategy)


class TestSelectComponent_InputDataTransformation:
    """Test suite for input data transformation in select_component step."""

    @pytest.mark.asyncio
    async def test_select_component_DATA_TRANSFORMATION_CONFIGURED_PER_TYPE_YAML(
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

        component = await agent.select_component(
            user_prompt="Test prompt", input_data=input_data
        )
        assert component is not None
        assert component.component == "hand-build-component"
        assert component.json_data is not None
        assert component.json_data == [{"name": "MYNAME"}]

    @pytest.mark.asyncio
    async def test_select_component_DATA_TRANSFORMATION_PER_TYPE_NOT_CONFIGURED_DATA_JSON(
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

        component = await agent.select_component(
            user_prompt="Test prompt", input_data=input_data
        )
        assert component is not None
        assert component.component == "hand-build-component"
        assert component.json_data is not None
        assert component.json_data == {"name": "MYNAME"}

    @pytest.mark.asyncio
    async def test_select_component_DATA_TRANSFORMATION_NOT_CONFIGURED_DATA_INVALID(
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

        with pytest.raises(ValueError, match="Invalid JSON format of the Input Data: "):
            await agent.select_component(
                user_prompt="Test prompt", input_data=input_data
            )

    @pytest.mark.asyncio
    async def test_select_component_DATA_TRANSFORMATION_CONFIGURED_YAML(
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

        component = await agent.select_component(
            user_prompt="Test prompt", input_data=input_data
        )
        assert component is not None
        assert component.component == "hand-build-component"
        assert component.json_data is not None
        assert component.json_data == [{"name": "MYNAME"}]


class TestSelectComponent_InputDataJsonWrapping:
    """Test suite for input data transformation in select_component step - wrapping."""

    @pytest.mark.asyncio
    async def test_select_component_WRAPPING(self) -> None:
        agent = NextGenUIAgent(config=AgentConfig(input_data_json_wrapping=True))

        input_data = InputData(id="1", data='[{"title": "Toy Story"}]', type="my_type")

        mocked_llm_component = UIComponentMetadata(
            component="one-card",
            id="1",
            title="Toy Story",
            fields=[DataField(name="Title", data_path="movie.title")],
        )

        component = await agent.select_component(
            user_prompt="Test prompt",
            input_data=input_data,
            inference=MockedInference(mocked_llm_component),
        )
        assert component is not None
        assert component.component == "one-card"
        assert component.json_data is not None
        assert component.json_data == {"my_type": [{"title": "Toy Story"}]}


class TestRefreshComponent:
    """Test suite for refresh_component method."""

    @pytest.mark.asyncio
    async def test_refresh_component_missing_input_data_transformer_name(self) -> None:
        agent = NextGenUIAgent(config=AgentConfig())
        input_data = InputData(id="1", data='[{"title": "Toy Story"}]', type="my_type")
        block_configuration = UIBlockConfiguration(
            component_metadata=UIBlockComponentMetadata(
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
        assert configuration.component_metadata is not None
        assert (
            configuration.component_metadata.component == component_metadata.component
        )
        assert configuration.component_metadata.id == component_metadata.id
        assert configuration.component_metadata.title == component_metadata.title
        assert configuration.component_metadata.fields[
            0
        ].data_path == sanitize_data_path("movie.title")
        assert configuration.component_metadata.fields[0].id == generate_field_id(
            configuration.component_metadata.fields[0].data_path
        )
        assert configuration.component_metadata.fields[1].data_path == "$..movie.year"
        assert configuration.component_metadata.fields[1].id == generate_field_id(
            configuration.component_metadata.fields[1].data_path
        )
        assert configuration.component_metadata.fields_all is None

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
        assert configuration.component_metadata is not None
        assert (
            configuration.component_metadata.component == component_metadata.component
        )
        assert configuration.component_metadata.id == component_metadata.id
        assert configuration.component_metadata.title == component_metadata.title
        assert configuration.component_metadata.fields[
            0
        ].data_path == sanitize_data_path("movie.title")
        assert configuration.component_metadata.fields[0].id == generate_field_id(
            configuration.component_metadata.fields[0].data_path
        )
        assert configuration.component_metadata.fields_all is None

    def test_construct_UIBlockConfiguration_with_all_fields_not_enabled(self) -> None:
        agent = NextGenUIAgent(config=AgentConfig())
        input_data = InputData(
            id="1", data='[{"title": "Toy Story", "year": 2024}]', type="my_type"
        )
        component_metadata = UIComponentMetadata(
            component="data-view",
            id="1",
            title="Toy Story",
            fields=[DataField(name="Title", data_path="my_type[*].title")],
            json_data={"my_type": [{"title": "Toy Story", "year": 2024}]},
        )
        configuration = agent.construct_UIBlockConfiguration(
            input_data, component_metadata
        )
        assert configuration.data_type == "my_type"
        assert configuration.input_data_transformer_name is None
        assert configuration.json_wrapping_field_name is None
        assert configuration.component_metadata is not None
        assert (
            configuration.component_metadata.component == component_metadata.component
        )
        assert configuration.component_metadata.id == component_metadata.id
        assert configuration.component_metadata.title == component_metadata.title

        assert configuration.component_metadata.fields is not None
        assert len(configuration.component_metadata.fields) == 1
        assert configuration.component_metadata.fields[
            0
        ].data_path == sanitize_data_path("my_type[*].title")
        assert configuration.component_metadata.fields[0].id == generate_field_id(
            configuration.component_metadata.fields[0].data_path
        )

        assert configuration.component_metadata.fields_all is None

    def test_construct_UIBlockConfiguration_with_all_fields_global_enabled(
        self,
    ) -> None:
        agent = NextGenUIAgent(config=AgentConfig(generate_all_fields=True))
        input_data = InputData(
            id="1", data='[{"title": "Toy Story", "year": 2024}]', type="my_type"
        )
        component_metadata = UIComponentMetadata(
            component="data-view",
            id="1",
            title="Toy Story",
            fields=[DataField(name="Title", data_path="my_type[*].title")],
            json_data={"my_type": [{"title": "Toy Story", "year": 2024}]},
        )
        configuration = agent.construct_UIBlockConfiguration(
            input_data, component_metadata
        )
        assert configuration.data_type == "my_type"
        assert configuration.input_data_transformer_name is None
        assert configuration.json_wrapping_field_name is None
        assert configuration.component_metadata is not None
        assert (
            configuration.component_metadata.component == component_metadata.component
        )
        assert configuration.component_metadata.id == component_metadata.id
        assert configuration.component_metadata.title == component_metadata.title

        assert configuration.component_metadata.fields is not None
        assert len(configuration.component_metadata.fields) == 1
        assert configuration.component_metadata.fields[
            0
        ].data_path == sanitize_data_path("my_type[*].title")
        assert configuration.component_metadata.fields[0].id == generate_field_id(
            configuration.component_metadata.fields[0].data_path
        )

        assert configuration.component_metadata.fields_all is not None
        assert len(configuration.component_metadata.fields_all) == 2
        assert configuration.component_metadata.fields_all[0].name == "Title"
        assert configuration.component_metadata.fields_all[1].name == "Year"
        assert (
            configuration.component_metadata.fields_all[0].data_path
            == "$..my_type[*].title"
        )
        assert configuration.component_metadata.fields_all[0].id == generate_field_id(
            configuration.component_metadata.fields_all[0].data_path
        )
        assert (
            configuration.component_metadata.fields_all[1].data_path
            == "$..my_type[*].year"
        )
        assert configuration.component_metadata.fields_all[1].id == generate_field_id(
            configuration.component_metadata.fields_all[1].data_path
        )

    def test_construct_UIBlockConfiguration_with_all_fields_global_enabled_pertype_disabled(
        self,
    ) -> None:
        agent = NextGenUIAgent(
            config=AgentConfig(
                data_types={"my_type": AgentConfigDataType(generate_all_fields=False)}
            )
        )
        input_data = InputData(
            id="1", data='[{"title": "Toy Story", "year": 2024}]', type="my_type"
        )
        component_metadata = UIComponentMetadata(
            component="data-view",
            id="1",
            title="Toy Story",
            fields=[DataField(name="Title", data_path="my_type[*].title")],
            json_data={"my_type": [{"title": "Toy Story", "year": 2024}]},
        )
        configuration = agent.construct_UIBlockConfiguration(
            input_data, component_metadata
        )
        assert configuration.data_type == "my_type"
        assert configuration.input_data_transformer_name is None
        assert configuration.json_wrapping_field_name is None
        assert configuration.component_metadata is not None
        assert (
            configuration.component_metadata.component == component_metadata.component
        )
        assert configuration.component_metadata.id == component_metadata.id
        assert configuration.component_metadata.title == component_metadata.title

        assert configuration.component_metadata.fields is not None
        assert len(configuration.component_metadata.fields) == 1
        assert configuration.component_metadata.fields[
            0
        ].data_path == sanitize_data_path("my_type[*].title")
        assert configuration.component_metadata.fields[0].id == generate_field_id(
            configuration.component_metadata.fields[0].data_path
        )

        assert configuration.component_metadata.fields_all is None

    def test_construct_UIBlockConfiguration_with_all_fields_global_disabled_pertype_enabled(
        self,
    ) -> None:
        agent = NextGenUIAgent(
            config=AgentConfig(
                generate_all_fields=False,
                data_types={"my_type": AgentConfigDataType(generate_all_fields=True)},
            )
        )
        input_data = InputData(
            id="1", data='[{"title": "Toy Story", "year": 2024}]', type="my_type"
        )
        component_metadata = UIComponentMetadata(
            component="data-view",
            id="1",
            title="Toy Story",
            fields=[DataField(name="Title", data_path="my_type[*].title")],
            json_data={"my_type": [{"title": "Toy Story", "year": 2024}]},
        )
        configuration = agent.construct_UIBlockConfiguration(
            input_data, component_metadata
        )
        assert configuration.data_type == "my_type"
        assert configuration.input_data_transformer_name is None
        assert configuration.json_wrapping_field_name is None
        assert configuration.component_metadata is not None
        assert (
            configuration.component_metadata.component == component_metadata.component
        )
        assert configuration.component_metadata.id == component_metadata.id
        assert configuration.component_metadata.title == component_metadata.title

        assert configuration.component_metadata.fields is not None
        assert len(configuration.component_metadata.fields) == 1
        assert configuration.component_metadata.fields[
            0
        ].data_path == sanitize_data_path("my_type[*].title")
        assert configuration.component_metadata.fields[0].id == generate_field_id(
            configuration.component_metadata.fields[0].data_path
        )

        assert configuration.component_metadata.fields_all is not None
        assert len(configuration.component_metadata.fields_all) == 2
        assert configuration.component_metadata.fields_all[0].name == "Title"
        assert configuration.component_metadata.fields_all[1].name == "Year"
        assert (
            configuration.component_metadata.fields_all[0].data_path
            == "$..my_type[*].title"
        )
        assert configuration.component_metadata.fields_all[0].id == generate_field_id(
            configuration.component_metadata.fields_all[0].data_path
        )
        assert (
            configuration.component_metadata.fields_all[1].data_path
            == "$..my_type[*].year"
        )
        assert configuration.component_metadata.fields_all[1].id == generate_field_id(
            configuration.component_metadata.fields_all[1].data_path
        )


class TestTransformData:
    def test_transform_data(self) -> None:
        agent = NextGenUIAgent()
        input_data = InputData(
            id="123",
            data="""{"name": "John Doe"}""",
        )
        component = UIComponentMetadata.model_validate(
            {
                "id": "123",
                "title": "John Doe",
                "component": "one-card",
                "fields": [
                    {"name": "Name", "data_path": "name"},
                ],
            }
        )
        component_data = cast(
            ComponentDataOneCard, agent.transform_data(input_data, component)
        )
        assert component_data.title == "John Doe"
        assert component_data.id == "123"
        assert component_data.component == "one-card"
        assert component_data.fields[0].name == "Name"
        assert component_data.fields[0].data == ["John Doe"]


class TestGenerateRendering:
    def test_generate_rendering_wrong_component_system_name(self) -> None:
        agent = NextGenUIAgent()
        with pytest.raises(
            Exception,
            match="UI component system 'bad' is not found. Make sure you install appropriate dependency.",
        ):
            agent.generate_rendering(
                ComponentDataBase(id="1", component="one-card"), "bad"
            )

    def test_generate_rendering_json(self) -> None:
        agent = NextGenUIAgent()
        c = get_transformed_component()
        result = agent.generate_rendering(c, "json")

        assert result.mime_type == "application/json"
        assert result.component_system == "json"
        assert result.id == c.id

        r = from_json(result.content)
        assert r["component"] == "one-card"

    def test_generate_rendering_configured_default_component_system(self) -> None:
        agent = NextGenUIAgent(config=AgentConfig(component_system="json"))
        c = get_transformed_component()
        result = agent.generate_rendering(c, None)

        assert result.mime_type == "application/json"
        assert result.component_system == "json"
        assert result.id == c.id

        r = from_json(result.content)
        assert r["component"] == "one-card"
