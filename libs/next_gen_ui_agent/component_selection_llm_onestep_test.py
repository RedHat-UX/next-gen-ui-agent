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
from next_gen_ui_agent.types import InputDataInternal
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
        prompt = strategy._build_system_prompt(None)

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
        prompt = strategy._build_system_prompt(basic_components)

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
        prompt = strategy._build_system_prompt(components_with_charts)

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
