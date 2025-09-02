import asyncio
import json

import pytest
from langchain_core.language_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, ToolMessage
from next_gen_ui_agent import UIComponentMetadata
from next_gen_ui_agent.data_transform.types import (
    ComponentDataHandBuildComponent,
    ComponentDataOneCard,
)
from next_gen_ui_agent.types import (
    AgentConfig,
    InputData,
    Rendition,
    UIComponentMetadataHandBuildComponent,
)
from next_gen_ui_langgraph.agent import GraphConfig, NextGenUILangGraphAgent
from next_gen_ui_testing.data_set_movies import find_movie
from pytest import fail


def test_is_next_gen_ui_message() -> None:
    tm = ToolMessage(content="", tool_call_id="1")
    assert NextGenUILangGraphAgent.is_next_gen_ui_message(tm) is False
    tm.name = "some_name"
    assert NextGenUILangGraphAgent.is_next_gen_ui_message(tm) is False
    tm.name = "ngui_rhds"
    assert NextGenUILangGraphAgent.is_next_gen_ui_message(tm) is True


USER_PROMPT = "Tell me brief details of Toy Story"
movies_data_obj = find_movie("Toy Story")
MOVIES_DATA = json.dumps(movies_data_obj, default=str)
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
async def test_agent_MESSAGESIN_WITHOUT_COMPONENT_SYSTEM_HBC() -> None:
    msg = AIMessage(content=LLM_RESPONSE)
    llm = FakeMessagesListChatModel(responses=[msg])

    # HBC selection is configured here based on tool call name
    agent = NextGenUILangGraphAgent(
        model=llm,
        config=AgentConfig(hand_build_components_mapping={"movies": "my-ui-component"}),
    )
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
    c: UIComponentMetadataHandBuildComponent = components[0]
    print("\n--RESULT---")
    print(c.component)
    assert "hand-build-component" == c.component
    assert "my-ui-component" == c.component_type
    assert c.id == "call_Jja7J89XsjrOLA5r!MEOW!SL"

    components_data = result["components_data"]
    assert len(components_data) == 1
    c_data: ComponentDataHandBuildComponent = components_data[0]
    assert c_data.component == "hand-build-component"
    assert c_data.id == "call_Jja7J89XsjrOLA5r!MEOW!SL"
    assert c_data.component_type == "my-ui-component"
    assert c_data.data == json.loads(MOVIES_DATA)

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
