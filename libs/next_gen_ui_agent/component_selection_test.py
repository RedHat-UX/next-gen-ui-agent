import asyncio
import logging

import pytest
from langchain_core.language_models import FakeMessagesListChatModel
from next_gen_ui_agent.types import AgentInput
from pytest import fail

from . import InputData
from .component_selection import OnestepLLMCallComponentSelectionStrategy, trim_to_json
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
    input_data = InputData({"id": "1", "data": movies_data})

    msg = {"type": "assistant", "content": response}
    llm = FakeMessagesListChatModel(responses=[msg])  # type: ignore
    inference = LangChainModelInference(llm)

    component_selection = OnestepLLMCallComponentSelectionStrategy(False)
    result = await component_selection.component_selection_run(
        user_input, inference, input_data
    )
    assert result.component == "one-card"


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
            user_input, inference, input_data
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


def test_trim_to_json_basic_object():
    text = '{"name": "John", "age": 30}'
    result = trim_to_json(text)
    assert result == '{"name": "John", "age": 30}'


def test_trim_to_json_basic_array():
    text = '["item1", "item2", "item3"]'
    result = trim_to_json(text)
    assert result == '["item1", "item2", "item3"]'


def test_trim_to_json_around_object():
    text = 'Prefix {"user": {"name": "John", "details": {"age": 30, "city": "NYC"}}} suffix'
    result = trim_to_json(text)
    assert result == '{"user": {"name": "John", "details": {"age": 30, "city": "NYC"}}}'


def test_trim_to_json_around_array():
    text = 'Prefix [ {"user": {"name": "John", "details": {"age": 30, "city": "NYC"}}} ] suffix'
    result = trim_to_json(text)
    assert (
        result
        == '[ {"user": {"name": "John", "details": {"age": 30, "city": "NYC"}}} ]'
    )


def test_trim_to_json_textonly():
    text = "Prefix suffix"
    result = trim_to_json(text)
    assert result == "Prefix suffix"


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    asyncio.run(test_component_selection_run_OK())
