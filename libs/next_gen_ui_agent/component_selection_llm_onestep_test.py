import asyncio
import json
import logging

import pytest
from langchain_core.language_models import FakeMessagesListChatModel
from next_gen_ui_agent.component_selection_llm_strategy import (
    MAX_STRING_DATA_LENGTH_FOR_LLM,
)
from next_gen_ui_agent.json_data_wrapper import wrap_string_as_json
from next_gen_ui_agent.types import AgentInput, InputDataInternal
from pytest import fail

from . import InputData
from .component_selection_llm_onestep import OnestepLLMCallComponentSelectionStrategy
from .model import LangChainModelInference

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
async def test_component_selection_run_OK() -> None:
    user_input = "Tell me brief details of Toy Story"
    input_data = InputData({"id": "1", "data": movies_data, "type": "movie.detail"})

    msg = {"type": "assistant", "content": response}
    llm = FakeMessagesListChatModel(responses=[msg])  # type: ignore
    inference = LangChainModelInference(llm)

    component_selection = OnestepLLMCallComponentSelectionStrategy(
        input_data_json_wrapping=False
    )
    result = await component_selection.component_selection_run(
        inference, user_input, input_data
    )
    assert result.component == "one-card"
    # assert json_data are not wrapped as it is disabled
    assert result.json_data == json.loads(movies_data)


@pytest.mark.asyncio
async def test_component_selection_run_json_wrapping_OK() -> None:
    user_input = "Tell me brief details of Toy Story"
    input_data = InputData(
        {"id": "1", "data": movies_data_TO_WRAP, "type": "movie.detail"}
    )

    msg = {"type": "assistant", "content": response}
    llm = FakeMessagesListChatModel(responses=[msg])  # type: ignore
    inference = LangChainModelInference(llm)

    component_selection = OnestepLLMCallComponentSelectionStrategy(False)
    result = await component_selection.component_selection_run(
        inference, user_input, input_data
    )
    assert result.component == "one-card"
    # assert json_data are wrapped as type is provided
    assert result.json_data == json.loads(
        '{ "movie_detail" :' + movies_data_TO_WRAP + "}"
    )


@pytest.mark.asyncio
async def test_component_selection_run_json_wrapping_no_OK() -> None:
    user_input = "Tell me brief details of Toy Story"
    input_data = InputData({"id": "1", "data": movies_data_TO_WRAP})

    msg = {"type": "assistant", "content": response}
    llm = FakeMessagesListChatModel(responses=[msg])  # type: ignore
    inference = LangChainModelInference(llm)

    component_selection = OnestepLLMCallComponentSelectionStrategy(False)
    result = await component_selection.component_selection_run(
        inference, user_input, input_data
    )
    assert result.component == "one-card"
    # assert json_data are not wrapped as type is not provided
    assert result.json_data == json.loads(movies_data_TO_WRAP)


@pytest.mark.asyncio
async def test_component_selection_run_stringinput_notype_OK() -> None:
    user_input = "Tell me brief details of Toy Story"
    input_data = InputDataInternal(
        {"id": "1", "data": "", "json_data": "large string data"}
    )

    msg = {"type": "assistant", "content": response}
    llm = FakeMessagesListChatModel(responses=[msg])  # type: ignore
    inference = LangChainModelInference(llm)

    component_selection = OnestepLLMCallComponentSelectionStrategy(False)
    result = await component_selection.component_selection_run(
        inference, user_input, input_data
    )
    assert result.component == "one-card"
    # assert json_data are wrapped string from input data
    assert result.json_data == wrap_string_as_json(
        "large string data", None, MAX_STRING_DATA_LENGTH_FOR_LLM
    )


@pytest.mark.asyncio
async def test_component_selection_run_stringinput_withype_OK() -> None:
    user_input = "Tell me brief details of Toy Story"
    input_data = InputDataInternal(
        {"id": "1", "data": "", "json_data": "large string data", "type": "test.type"}
    )

    msg = {"type": "assistant", "content": response}
    llm = FakeMessagesListChatModel(responses=[msg])  # type: ignore
    inference = LangChainModelInference(llm)

    component_selection = OnestepLLMCallComponentSelectionStrategy(False)
    result = await component_selection.component_selection_run(
        inference, user_input, input_data
    )
    assert result.component == "one-card"
    # assert json_data are wrapped string from input data
    assert result.json_data == wrap_string_as_json(
        "large string data", "test_type", MAX_STRING_DATA_LENGTH_FOR_LLM
    )


@pytest.mark.asyncio
async def test_component_selection_run_INVALID_LLM_RESPONSE() -> None:
    user_input = "Tell me brief details of Toy Story"
    input_data = InputData({"id": "1", "data": movies_data})

    msg = {"type": "assistant", "content": "invalid json"}
    llm = FakeMessagesListChatModel(responses=[msg])  # type: ignore
    inference = LangChainModelInference(llm)

    try:
        component_selection = OnestepLLMCallComponentSelectionStrategy(False)
        await component_selection.component_selection_run(
            inference, user_input, input_data
        )
        fail("Exception expected")
    except Exception as e:
        assert e.__class__.__name__ == "ValueError"
        pass


@pytest.mark.asyncio
async def test_component_selection() -> None:
    input_data_1 = InputData({"id": "1", "data": movies_data})
    input_data_2 = InputData({"id": "2", "data": movies_data})

    input = AgentInput(
        {
            "user_prompt": "Tell me brief details of Toy Story",
            "input_data": [input_data_1, input_data_2],
        }
    )

    msg = {"type": "assistant", "content": response}
    llm = FakeMessagesListChatModel(responses=[msg])  # type: ignore
    inference = LangChainModelInference(llm)

    component_selection = OnestepLLMCallComponentSelectionStrategy(False)
    result = await component_selection.select_components(inference, input)

    assert len(result) == 2
    ids = []
    for r in result:
        ids.append(r.id)
    assert "1" in ids
    assert "2" in ids


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    asyncio.run(test_component_selection_run_OK())
