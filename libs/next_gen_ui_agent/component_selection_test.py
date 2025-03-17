import asyncio

import pytest
from langchain_core.language_models import FakeMessagesListChatModel

from . import InputData
from .component_selection import component_selection_run
from .model import LangChainModelInference

# from langchain_openai import ChatOpenAI


@pytest.mark.asyncio
async def test_component_selection_run():
    user_input = "Tell me brief details of Toy Story"
    movies_data = """
    [
    {
        "movie":{
        "languages":[
            "English"
        ],
        "year":1995,
        "imdbId":"0114709",
        "runtime":81,
        "imdbRating":8.3,
        "movieId":"1",
        "countries":[
            "USA"
        ],
        "imdbVotes":591836,
        "title":"Toy Story",
        "url":"https://themoviedb.org/movie/862",
        "revenue":373554033,
        "tmdbId":"862",
        "plot":"A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room.",
        "posterUrl":"https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
        "released":"1995-11-22",
        "trailerUrl": "https://www.youtube.com/watch?v=v-PjgYDrg70",
        "budget":30000000
        },
        "actors":[
        "Jim Varney",
        "Tim Allen",
        "Tom Hanks",
        "Don Rickles"
        ]
    }
    ]
    """
    input_data = InputData({"id": "1", "data": movies_data})

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
    # llm_settings = {
    #     "model": "llama3.2",
    #     "base_url": "http://localhost:11434/v1",
    #     "api_key": "ollama",
    #     "temperature": 0,
    # }
    # llm = ChatOpenAI(**llm_settings, disable_streaming=True)
    msg = {"type": "assistant", "content": response}
    llm = FakeMessagesListChatModel(responses=[msg])
    iference = LangChainModelInference(llm)

    result = await component_selection_run(user_input, iference, input_data)
    assert result["component"] == "one-card"


if __name__ == "__main__":
    asyncio.run(test_component_selection_run())
