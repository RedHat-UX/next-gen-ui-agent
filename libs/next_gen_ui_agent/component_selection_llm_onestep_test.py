import json

import pytest
from langchain_core.language_models import FakeMessagesListChatModel
from next_gen_ui_agent import AgentConfig
from next_gen_ui_agent.component_selection_common import (
    CHART_COMPONENTS,
    COMPONENT_METADATA,
)
from next_gen_ui_agent.component_selection_llm_strategy import (
    MAX_STRING_DATA_LENGTH_FOR_LLM,
)
from next_gen_ui_agent.inference.langchain_inference import LangChainModelInference
from next_gen_ui_agent.json_data_wrapper import wrap_string_as_json
from next_gen_ui_agent.types import AgentConfigComponent, InputDataInternal
from pytest import fail

from .component_selection_llm_onestep import OnestepLLMCallComponentSelectionStrategy

movies_data = """[
{
    "movie":{
        "year":1995,
        "imdbRating":8.3,
        "countries":[
            "USA"
        ],
        "title":"Toy Story",
        "url":"https://themoviedb.org/movie/862"
    }
}
]"""

movies_data_TO_WRAP = """
{
    "year":1995,
    "imdbRating":8.3,
    "countries":[
        "USA"
    ],
    "title":"Toy Story",
    "url":"https://themoviedb.org/movie/862"
}
"""

response = """
    {
        "title": "Toy Story Details",
        "reasonForTheComponentSelection": "One item available in the data",
        "confidenceScore": "100%",
        "component": "one-card",
        "fields" : [
            {"name":"Title","data_path":"movie.title"},
            {"name":"Year","data_path":"movie.year"},
            {"name":"IMDB Rating","data_path":"movie.imdbRating"},
            {"name":"Release Date","data_path":"movie.released"}
        ]
    }
    """


@pytest.mark.asyncio
async def test_select_component_OK() -> None:
    user_input = "Tell me brief details of Toy Story"
    input_data = InputDataInternal(
        {
            "id": "1",
            "data": movies_data,
            "type": "movie.detail",
            "input_data_transformer_name": "json",
        }
    )

    msg = {"type": "assistant", "content": response}
    llm = FakeMessagesListChatModel(responses=[msg])  # type: ignore
    inference = LangChainModelInference(llm)

    component_selection = OnestepLLMCallComponentSelectionStrategy(
        config=AgentConfig(input_data_json_wrapping=False)
    )
    result = await component_selection.select_component(
        inference, user_input, input_data
    )
    assert result.component == "one-card"
    assert result.json_wrapping_field_name is None
    assert result.input_data_transformer_name == "json"
    # assert json_data are not wrapped as it is disabled
    assert result.json_data == json.loads(movies_data)


@pytest.mark.asyncio
async def test_select_component_json_wrapping_OK() -> None:
    user_input = "Tell me brief details of Toy Story"
    input_data = InputDataInternal(
        {"id": "1", "data": movies_data_TO_WRAP, "type": "movie.detail"}
    )

    msg = {"type": "assistant", "content": response}
    llm = FakeMessagesListChatModel(responses=[msg])  # type: ignore
    inference = LangChainModelInference(llm)

    component_selection = OnestepLLMCallComponentSelectionStrategy(config=AgentConfig())
    result = await component_selection.select_component(
        inference, user_input, input_data
    )
    assert result.component == "one-card"
    assert result.json_wrapping_field_name == "movie_detail"
    assert result.input_data_transformer_name is None
    assert result.input_data_type == "movie.detail"
    # assert json_data are wrapped as type is provided
    assert result.json_data == json.loads(
        '{ "movie_detail" :' + movies_data_TO_WRAP + "}"
    )


@pytest.mark.asyncio
async def test_select_component_json_wrapping_no_OK() -> None:
    user_input = "Tell me brief details of Toy Story"
    input_data = InputDataInternal({"id": "1", "data": movies_data_TO_WRAP})

    msg = {"type": "assistant", "content": response}
    llm = FakeMessagesListChatModel(responses=[msg])  # type: ignore
    inference = LangChainModelInference(llm)

    component_selection = OnestepLLMCallComponentSelectionStrategy(
        config=AgentConfig(input_data_json_wrapping=False)
    )
    result = await component_selection.select_component(
        inference, user_input, input_data
    )
    assert result.component == "one-card"
    assert result.json_wrapping_field_name is None
    assert result.input_data_transformer_name is None
    assert result.input_data_type is None
    # assert json_data are not wrapped as type is not provided
    assert result.json_data == json.loads(movies_data_TO_WRAP)


@pytest.mark.asyncio
async def test_select_component_stringinput_notype_OK() -> None:
    user_input = "Tell me brief details of Toy Story"
    input_data = InputDataInternal(
        {
            "id": "1",
            "data": "",
            "json_data": "large string data",
            "input_data_transformer_name": "json",
        }
    )

    msg = {"type": "assistant", "content": response}
    llm = FakeMessagesListChatModel(responses=[msg])  # type: ignore
    inference = LangChainModelInference(llm)

    component_selection = OnestepLLMCallComponentSelectionStrategy(
        config=AgentConfig(input_data_json_wrapping=False)
    )
    result = await component_selection.select_component(
        inference, user_input, input_data
    )
    assert result.component == "one-card"
    assert result.json_wrapping_field_name == "data"
    assert result.input_data_transformer_name == "json"
    # assert json_data are wrapped string from input data
    assert (
        result.json_data
        == wrap_string_as_json(
            "large string data", None, MAX_STRING_DATA_LENGTH_FOR_LLM
        )[0]
    )


@pytest.mark.asyncio
async def test_select_component_stringinput_with_type_OK() -> None:
    user_input = "Tell me brief details of Toy Story"
    input_data = InputDataInternal(
        {"id": "1", "data": "", "json_data": "large string data", "type": "test.type"}
    )

    msg = {"type": "assistant", "content": response}
    llm = FakeMessagesListChatModel(responses=[msg])  # type: ignore
    inference = LangChainModelInference(llm)

    component_selection = OnestepLLMCallComponentSelectionStrategy(
        config=AgentConfig(input_data_json_wrapping=False)
    )
    result = await component_selection.select_component(
        inference, user_input, input_data
    )
    assert result.component == "one-card"
    assert result.json_wrapping_field_name == "test_type"
    assert result.input_data_transformer_name is None
    # assert json_data are wrapped string from input data
    assert (
        result.json_data
        == wrap_string_as_json(
            "large string data", "test_type", MAX_STRING_DATA_LENGTH_FOR_LLM
        )[0]
    )


@pytest.mark.asyncio
async def test_select_component_INVALID_LLM_RESPONSE() -> None:
    user_input = "Tell me brief details of Toy Story"
    input_data = InputDataInternal({"id": "1", "data": movies_data})

    msg = {"type": "assistant", "content": "invalid json"}
    llm = FakeMessagesListChatModel(responses=[msg])  # type: ignore
    inference = LangChainModelInference(llm)

    try:
        component_selection = OnestepLLMCallComponentSelectionStrategy(
            config=AgentConfig(input_data_json_wrapping=False)
        )
        await component_selection.select_component(inference, user_input, input_data)
        fail("Exception expected")
    except Exception as e:
        assert e.__class__.__name__ == "ValueError"
        pass


class TestBuildSystemPrompt:
    """Test _build_system_prompt method."""

    def test_all_components_when_none(self):
        """Test that all components are included when selectable_components is None."""
        config = AgentConfig(selectable_components=None)
        strategy = OnestepLLMCallComponentSelectionStrategy(config)
        prompt = strategy._build_system_prompt(None, strategy._base_metadata)

        # Should include all components
        for component in COMPONENT_METADATA.keys():
            assert component in prompt

        # Should include chart instructions
        assert "CHART TYPES" in prompt

        # Should include examples
        assert "Response example" in prompt

    def test_basic_components_only(self):
        """Test with only basic (non-chart) components."""
        basic_components = {"one-card", "table", "set-of-cards"}
        config = AgentConfig(selectable_components=basic_components)
        strategy = OnestepLLMCallComponentSelectionStrategy(config)
        prompt = strategy._build_system_prompt(
            basic_components, strategy._base_metadata
        )

        # Should include selected basic components
        assert "one-card" in prompt
        assert "table" in prompt
        assert "set-of-cards" in prompt

        # Should NOT include chart components
        for chart_comp in CHART_COMPONENTS:
            assert chart_comp not in prompt

        # Should NOT include chart instructions
        assert "CHART TYPES" not in prompt

        # Should include examples for basic components
        assert "Response example" in prompt

    def test_with_chart_components(self):
        """Test with chart components included."""
        components_with_charts = {"table", "chart-bar", "chart-line"}
        config = AgentConfig(selectable_components=components_with_charts)
        strategy = OnestepLLMCallComponentSelectionStrategy(config)
        prompt = strategy._build_system_prompt(
            components_with_charts, strategy._base_metadata
        )

        # Should include selected components
        assert "table" in prompt
        assert "chart-bar" in prompt
        assert "chart-line" in prompt

        # Should include chart instructions
        assert "CHART TYPES" in prompt
        assert "FIELDS BY CHART TYPE" in prompt

        # Should NOT include chart components that weren't selected
        assert "chart-pie" not in prompt
        assert "chart-donut" not in prompt

        # Should include examples
        assert "Response example" in prompt


def test_onestep_with_component_metadata_overrides() -> None:
    """Test that component metadata overrides are applied to system prompt."""
    from next_gen_ui_agent.types import AgentConfigPrompt, AgentConfigPromptComponent

    # Create config with overrides
    config = AgentConfig(
        prompt=AgentConfigPrompt(
            components={
                "table": AgentConfigPromptComponent(
                    description="CUSTOM_TABLE_DESCRIPTION for testing"
                ),
                "chart-bar": AgentConfigPromptComponent(
                    chart_description="CUSTOM_BAR_CHART_DESCRIPTION for testing"
                ),
            }
        )
    )

    # Create strategy with overrides
    strategy = OnestepLLMCallComponentSelectionStrategy(config=config)

    # Get the system prompt
    prompt = strategy.get_system_prompt()

    # Verify custom descriptions are in the prompt
    assert "CUSTOM_TABLE_DESCRIPTION for testing" in prompt
    assert "CUSTOM_BAR_CHART_DESCRIPTION for testing" in prompt

    # Verify original descriptions are NOT in the prompt
    assert COMPONENT_METADATA["table"]["description"] not in prompt
    assert COMPONENT_METADATA["chart-bar"]["chart_description"] not in prompt


class TestSystemPromptCaching:
    """Tests for system prompt caching mechanism."""

    def test_cache_hit_for_same_data_type(self):
        """Test that cache is used for repeated calls with same data_type."""
        from unittest.mock import patch

        from next_gen_ui_agent.types import (
            AgentConfigDataType,
            AgentConfigPromptComponent,
        )

        config = AgentConfig(
            data_types={
                "movies": AgentConfigDataType(
                    components=[
                        AgentConfigComponent(
                            component="table",
                            prompt=AgentConfigPromptComponent(
                                description="Movies table"
                            ),
                        )
                    ]
                )
            }
        )

        strategy = OnestepLLMCallComponentSelectionStrategy(config=config)

        # Cache starts with one entry (None) from __init__
        initial_cache_size = len(strategy._system_prompt_cache)
        assert None in strategy._system_prompt_cache

        # Spy on _build_system_prompt
        with patch.object(
            strategy, "_build_system_prompt", wraps=strategy._build_system_prompt
        ) as mock_build:
            # Call twice with same data_type
            prompt1 = strategy._get_or_build_system_prompt("movies")
            prompt2 = strategy._get_or_build_system_prompt("movies")

            # Build should only be called once (for "movies")
            assert mock_build.call_count == 1

            # Should return same object (not just equal)
            assert prompt1 is prompt2

            # Cache should have "movies" entry plus initial None
            assert "movies" in strategy._system_prompt_cache
            assert len(strategy._system_prompt_cache) == initial_cache_size + 1

    def test_different_cache_entries_per_data_type(self):
        """Test that different data_types get different cache entries."""
        from next_gen_ui_agent.types import (
            AgentConfigDataType,
            AgentConfigPromptComponent,
        )

        config = AgentConfig(
            data_types={
                "movies": AgentConfigDataType(
                    components=[
                        AgentConfigComponent(
                            component="table",
                            prompt=AgentConfigPromptComponent(
                                description="MOVIES_TABLE_DESC"
                            ),
                        )
                    ]
                ),
                "products": AgentConfigDataType(
                    components=[
                        AgentConfigComponent(
                            component="table",
                            prompt=AgentConfigPromptComponent(
                                description="PRODUCTS_TABLE_DESC"
                            ),
                        )
                    ]
                ),
            }
        )

        strategy = OnestepLLMCallComponentSelectionStrategy(config=config)

        # Cache starts with one entry (None) from __init__
        initial_cache_size = len(strategy._system_prompt_cache)

        # Call with different data_types
        prompt_movies = strategy._get_or_build_system_prompt("movies")
        prompt_products = strategy._get_or_build_system_prompt("products")

        # Cache should have 2 new entries plus initial None
        assert "movies" in strategy._system_prompt_cache
        assert "products" in strategy._system_prompt_cache
        assert len(strategy._system_prompt_cache) == initial_cache_size + 2

        # Prompts should be different
        assert prompt_movies != prompt_products

        # Verify prompts contain respective custom descriptions
        assert "MOVIES_TABLE_DESC" in prompt_movies
        assert "MOVIES_TABLE_DESC" not in prompt_products
        assert "PRODUCTS_TABLE_DESC" in prompt_products
        assert "PRODUCTS_TABLE_DESC" not in prompt_movies

    def test_global_selection_uses_none_key(self):
        """Test that global selection uses None as cache key."""
        config = AgentConfig(selectable_components={"table", "chart-bar"})

        strategy = OnestepLLMCallComponentSelectionStrategy(config=config)

        # Call with None (global selection)
        prompt1 = strategy._get_or_build_system_prompt(None)
        prompt2 = strategy._get_or_build_system_prompt(None)

        # Should use None as cache key
        assert None in strategy._system_prompt_cache

        # Should return same object
        assert prompt1 is prompt2

    def test_cache_isolation_data_type_vs_global(self):
        """Test that data_type-specific and global caches are separate."""
        from next_gen_ui_agent.types import (
            AgentConfigDataType,
            AgentConfigPromptComponent,
        )

        config = AgentConfig(
            data_types={
                "movies": AgentConfigDataType(
                    components=[
                        AgentConfigComponent(
                            component="table",
                            prompt=AgentConfigPromptComponent(
                                description="CUSTOM_MOVIES_TABLE"
                            ),
                        )
                    ]
                )
            }
        )

        strategy = OnestepLLMCallComponentSelectionStrategy(config=config)

        # Cache already has None entry from __init__
        assert None in strategy._system_prompt_cache
        initial_global_prompt = strategy._system_prompt_cache[None]

        # Call with data_type
        prompt_movies = strategy._get_or_build_system_prompt("movies")

        # Call without data_type (global) - should return cached
        prompt_global = strategy._get_or_build_system_prompt(None)

        # Cache should have 2 entries: None and "movies"
        assert "movies" in strategy._system_prompt_cache
        assert None in strategy._system_prompt_cache
        assert len(strategy._system_prompt_cache) == 2

        # Global prompt should be the same object as initial
        assert prompt_global is initial_global_prompt

        # Prompts should be different
        assert prompt_movies != prompt_global

        # Movies prompt has custom description, global doesn't
        assert "CUSTOM_MOVIES_TABLE" in prompt_movies
        assert "CUSTOM_MOVIES_TABLE" not in prompt_global
