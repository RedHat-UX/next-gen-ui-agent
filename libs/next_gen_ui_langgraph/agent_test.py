import asyncio

import pytest
from langchain_core.language_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, ToolMessage
from next_gen_ui_agent import UIComponentMetadata
from next_gen_ui_agent.data_transform.types import ComponentDataOneCard
from next_gen_ui_agent.types import InputData, Rendition
from next_gen_ui_langgraph.agent import GraphConfig, NextGenUILangGraphAgent
from pytest import fail


def test_is_next_gen_ui_message() -> None:
    tm = ToolMessage(content="", tool_call_id="1")
    assert NextGenUILangGraphAgent.is_next_gen_ui_message(tm) is False
    tm.name = "some_name"
    assert NextGenUILangGraphAgent.is_next_gen_ui_message(tm) is False
    tm.name = "ngui_rhds"
    assert NextGenUILangGraphAgent.is_next_gen_ui_message(tm) is True


USER_PROMPT = "Tell me brief details of Toy Story"
MOVIES_DATA = """
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
LLM_RESPONSE = """
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
async def test_agent_MESSAGESIN_WITH_COMPONENT_SYSTEM() -> None:
    msg = AIMessage(content=LLM_RESPONSE)
    llm = FakeMessagesListChatModel(responses=[msg])

    agent = NextGenUILangGraphAgent(model=llm)
    graph = agent.build_graph()

    tool_message = ToolMessage(
        content=MOVIES_DATA,
        name="movies",
        tool_call_id="call_Jja7J89XsjrOLA5r!MEOW!SL",
    )

    human_message = HumanMessage(content=USER_PROMPT)

    configurable: GraphConfig = {"component_system": "json"}  # type: ignore
    result = await graph.ainvoke(
        input={"messages": [human_message, tool_message]},
        config={"configurable": configurable},
    )
    components = result["components"]
    c: UIComponentMetadata = components[0]
    print("\n--RESULT---")
    print(c.component)
    assert "one-card" == c.component
    assert c.fields
    field = c.fields[0]
    assert field.name == "Title"

    components_data = result["components_data"]
    assert len(components_data) == 1
    c_data: ComponentDataOneCard = components_data[0]
    assert c_data.component == "one-card"
    assert c_data.fields
    c_field = c_data.fields[0]
    assert c_field.name == "Title"
    assert c_field.data == ["Toy Story"]

    # renditions for configured component system are present
    renditions = result["renditions"]
    assert len(renditions) == 1
    r: Rendition = renditions[0]
    assert r.id != ""
    assert r.content == c_data.model_dump_json()

    retmsgs: list[AnyMessage] = result["messages"]
    assert len(retmsgs) == 4
    # first two messages are input one, we have to assert next two which are output
    assert retmsgs[2].type == "ai"
    assert retmsgs[2].name == "ngui_json"
    assert retmsgs[2].content == ""

    assert retmsgs[3].type == "tool"
    assert retmsgs[3].name == "ngui_json"
    assert retmsgs[3].content == c_data.model_dump_json()


@pytest.mark.asyncio
async def test_agent_MESSAGESIN_WITHOUT_COMPONENT_SYSTEM() -> None:
    msg = AIMessage(content=LLM_RESPONSE)
    llm = FakeMessagesListChatModel(responses=[msg])

    agent = NextGenUILangGraphAgent(model=llm)
    graph = agent.build_graph()

    tool_message = ToolMessage(
        content=MOVIES_DATA,
        name="movies",
        tool_call_id="call_Jja7J89XsjrOLA5r!MEOW!SL",
    )

    human_message = HumanMessage(content=USER_PROMPT)

    # no component system defined here
    configurable: GraphConfig = {}  # type: ignore
    result = await graph.ainvoke(
        input={"messages": [human_message, tool_message]},
        config={"configurable": configurable},
    )
    components = result["components"]
    c: UIComponentMetadata = components[0]
    print("\n--RESULT---")
    print(c.component)
    assert "one-card" == c.component
    assert c.fields
    field = c.fields[0]
    assert field.name == "Title"

    components_data = result["components_data"]
    assert len(components_data) == 1
    c_data: ComponentDataOneCard = components_data[0]
    assert c_data.component == "one-card"
    assert c_data.fields
    c_field = c_data.fields[0]
    assert c_field.name == "Title"
    assert c_field.data == ["Toy Story"]

    try:
        result["renditions"]
        fail("renditions should not be present")
    except KeyError:
        pass

    retmsgs = result["messages"]
    assert len(retmsgs) == 2
    # first two messages are input one, no one produced as component system is not configured


@pytest.mark.asyncio
async def test_agent_STATEIN_WITH_COMPONENT_SYSTEM() -> None:
    msg = AIMessage(content=LLM_RESPONSE)
    llm = FakeMessagesListChatModel(responses=[msg])

    agent = NextGenUILangGraphAgent(model=llm)
    graph = agent.build_graph()

    configurable: GraphConfig = {"component_system": "json"}  # type: ignore
    result = await graph.ainvoke(
        input={
            "user_prompt": USER_PROMPT,
            "backend_data": [InputData(data=MOVIES_DATA, id="movies-011")],
        },
        config={"configurable": configurable},
    )
    components = result["components"]
    c: UIComponentMetadata = components[0]
    print("\n--RESULT---")
    print(c.component)
    assert "one-card" == c.component
    assert c.fields
    field = c.fields[0]
    assert field.name == "Title"

    components_data = result["components_data"]
    assert len(components_data) == 1
    c_data: ComponentDataOneCard = components_data[0]
    assert c_data.component == "one-card"
    assert c_data.fields
    c_field = c_data.fields[0]
    assert c_field.name == "Title"
    assert c_field.data == ["Toy Story"]

    # renditions for configured component system are present
    renditions = result["renditions"]
    assert len(renditions) == 1
    r: Rendition = renditions[0]
    assert r.id != ""
    assert r.content == c_data.model_dump_json()

    retmsgs: list[AnyMessage] = result["messages"]
    assert len(retmsgs) == 2
    # no input messages, two are output
    assert retmsgs[0].type == "ai"
    assert retmsgs[0].name == "ngui_json"
    assert retmsgs[0].content == ""

    assert retmsgs[1].type == "tool"
    assert retmsgs[1].name == "ngui_json"
    assert retmsgs[1].content == c_data.model_dump_json()


if __name__ == "__main__":
    asyncio.run(test_agent_MESSAGESIN_WITH_COMPONENT_SYSTEM())
