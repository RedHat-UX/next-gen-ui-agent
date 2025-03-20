import asyncio

import pytest
from langchain_core.language_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from next_gen_ui_agent import UIComponentMetadata
from next_gen_ui_langgraph.agent import NextGenUILangGraphAgent


@pytest.mark.asyncio
async def test_agent() -> None:
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
    msg = AIMessage(content=response)
    llm = FakeMessagesListChatModel(responses=[msg])

    agent = NextGenUILangGraphAgent(model=llm)
    graph = agent.build_graph()

    tool_message = ToolMessage(
        content=movies_data,
        name="movies",
        tool_call_id="call_Jja7J89XsjrOLA5r!MEOW!SL",
    )
    # tm_actor1 = ToolMessage(content=actor1, name="actor_detail", tool_call_id="call_5")
    # tm_actor2 = ToolMessage(content=actor2, name="actor_detail", tool_call_id="call_6")

    human_message = HumanMessage(content=user_input)
    # async for msg, metadata in graph.astream(
    #     {"messages": [human_message, tool_message]},
    #     # {"messages": [human_message, tm_actor1, tm_actor2]},
    #     # {"configurable": configurable},
    #     stream_mode="messages",
    # ):
    #     print("MMMMSG" + msg.content, end="", flush=True)
    result = await graph.ainvoke(
        input={"messages": [human_message, tool_message]},
        # config={"configurable": configurable},
    )
    components = result["components"]
    c: UIComponentMetadata = components[0]
    result["messages"] = ["removed"]
    print("\n--RESULT---")
    print(c["component"])
    assert "one-card" == c["component"]
    assert c["fields"]
    field = c["fields"][0]
    assert field["name"] == "Title"
    assert field["data"] == ["Toy Story"]


if __name__ == "__main__":
    asyncio.run(test_agent())
