import asyncio
import json
from unittest.mock import patch

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
    AgentConfigComponent,
    AgentConfigDataType,
    InputData,
    UIBlock,
    UIBlockRendering,
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
    tm.name = "ngui_error_rhds"
    assert NextGenUILangGraphAgent.is_next_gen_ui_message(tm) is False


def test_is_next_gen_ui_error_message() -> None:
    tm = ToolMessage(content="", tool_call_id="1")
    assert NextGenUILangGraphAgent.is_next_gen_ui_error_message(tm) is False
    tm.name = "some_name"
    assert NextGenUILangGraphAgent.is_next_gen_ui_error_message(tm) is False
    tm.name = "ngui_error_rhds"
    assert NextGenUILangGraphAgent.is_next_gen_ui_error_message(tm) is True
    tm.name = "ngui_rhds"
    assert NextGenUILangGraphAgent.is_next_gen_ui_error_message(tm) is False


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

    assert len(result["errors"]) == 0
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
    r: UIBlockRendering = renditions[0]
    assert r.id != ""
    assert r.content == c_data.model_dump_json()

    retmsgs: list[AnyMessage] = result["messages"]
    assert len(retmsgs) == 4
    # first two messages are input one, we have to assert next two which are output

    tool_message: ToolMessage = retmsgs[2]  # type: ignore
    assert tool_message.status == "success"
    assert tool_message.tool_call_id is not None
    assert tool_message.type == "tool"
    assert tool_message.name == "ngui_json"
    assert tool_message.content == c_data.model_dump_json()

    ai_message: AIMessage = retmsgs[3]  # type: ignore
    assert ai_message.type == "ai"
    assert ai_message.name == "ngui_json"
    assert ai_message.content == "Successfully generated 1 UI components. Failed: 0"
    assert len(ai_message.tool_calls) == 1


@pytest.mark.asyncio
async def test_agent_MESSAGESIN_WITHOUT_COMPONENT_SYSTEM_HBC() -> None:
    msg = AIMessage(content=LLM_RESPONSE)
    llm = FakeMessagesListChatModel(responses=[msg])

    # HBC selection is configured here based on tool call name
    agent = NextGenUILangGraphAgent(
        model=llm,
        config=AgentConfig(
            data_types={
                "movies": AgentConfigDataType(
                    components=[AgentConfigComponent(component="my-ui-component")]
                )
            }
        ),
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
    assert len(result["errors"]) == 0
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
    assert c_data.component == "my-ui-component"
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
    assert len(result["errors"]) == 0
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
    r: UIBlockRendering = renditions[0]
    assert r.id != ""
    assert r.content == c_data.model_dump_json()

    retmsgs: list[AnyMessage] = result["messages"]
    assert len(retmsgs) == 2
    # no input messages, two are output

    assert retmsgs[0].type == "tool"
    assert retmsgs[0].name == "ngui_json"
    assert retmsgs[0].content == c_data.model_dump_json()

    assert retmsgs[1].type == "ai"
    assert retmsgs[1].name == "ngui_json"
    assert retmsgs[1].content == "Successfully generated 1 UI components. Failed: 0"


@pytest.mark.asyncio
async def test_agent_ERROR_HANDLING_AT_DIFFERENT_STAGES() -> None:
    """Test that errors are properly caught and reported at different processing stages.

    This test simulates:
    - One successful component (id=success)
    - One error at component_selection stage (id=error_selection)
    - One error at data_transformation stage (id=error_transformation)
    - One error at design_system_handler stage (id=error_rendering)
    """

    msg = AIMessage(content=LLM_RESPONSE)
    llm = FakeMessagesListChatModel(responses=[msg, msg, msg, msg])

    agent = NextGenUILangGraphAgent(model=llm, output_messages_with_ui_blocks=True)
    graph = agent.build_graph()

    # Prepare input data with 4 items
    input_data = [
        InputData(data=MOVIES_DATA, id="success", type="movies"),
        InputData(data=MOVIES_DATA, id="error_selection", type="movies"),
        InputData(data=MOVIES_DATA, id="error_transformation", type="movies"),
        InputData(data=MOVIES_DATA, id="error_rendering", type="movies"),
    ]

    # Mock select_component to fail for specific id
    original_select_component = agent.ngui_agent.select_component

    async def mock_select_component(user_prompt: str, input_data: InputData):
        if input_data["id"] == "error_selection":
            raise Exception("Component selection failed for testing")
        return await original_select_component(user_prompt, input_data)

    # Mock transform_data to fail for specific id
    original_transform_data = agent.ngui_agent.transform_data

    def mock_transform_data(input_data: InputData, component: UIComponentMetadata):
        if component.id == "error_transformation":
            raise Exception("Data transformation failed for testing")
        return original_transform_data(input_data, component)

    # Mock generate_rendering to fail for specific id
    original_generate_rendering = agent.ngui_agent.generate_rendering

    def mock_generate_rendering(component_data, component_system):
        if component_data.id == "error_rendering":
            raise Exception("Rendering generation failed for testing")
        return original_generate_rendering(component_data, component_system)

    # Apply patches
    with patch.object(
        agent.ngui_agent, "select_component", side_effect=mock_select_component
    ), patch.object(
        agent.ngui_agent, "transform_data", side_effect=mock_transform_data
    ), patch.object(
        agent.ngui_agent, "generate_rendering", side_effect=mock_generate_rendering
    ):
        configurable: GraphConfig = {"component_system": "json"}  # type: ignore
        result = await graph.ainvoke(
            input={
                "user_prompt": USER_PROMPT,
                "backend_data": input_data,
            },
            config={"configurable": configurable},
        )

    # Assert errors are captured
    errors = result["errors"]

    assert len(errors) == 3, f"Expected 3 errors, got {len(errors)}"

    # Verify specific error messages contain expected text
    error_texts = " ".join(errors)
    assert (
        "Error selecting component for data from tool_call_id='error_selection': Component selection failed for testing"
        in error_texts
    ), "Missing error for component selection"
    assert (
        "Error transforming data from tool_call_id='error_transformation': Data transformation failed for testing"
        in error_texts
    ), "Missing error for data transformation"
    assert (
        "Error generating rendering for data from tool_call_id='error_rendering': Rendering generation failed for testing"
        in error_texts
    ), "Missing error for rendering generation"

    # Assert we have one successful component
    components = result["components"]
    assert (
        len(components) == 3
    ), f"Expected 3 components (excluding selection error), got {len(components)}"

    # Assert we have one successful component_data (two failed: one at selection, one at transformation)
    components_data = result["components_data"]
    assert (
        len(components_data) == 2
    ), f"Expected 2 component_data (excluding selection and transformation errors), got {len(components_data)}"

    # Assert we have one successful rendition (three failed: one at each stage)
    renditions = result["renditions"]
    assert (
        len(renditions) == 1
    ), f"Expected 1 rendition (only success case), got {len(renditions)}"
    r: UIBlockRendering = renditions[0]
    assert r.id == "success"

    # Assert messages include both successful and error messages
    retmsgs: list[AnyMessage] = result["messages"]

    # Should have: 2 messages for success (AI + Tool), 6 messages for 3 errors (AI + Tool each)
    assert (
        len(retmsgs) == 5
    ), f"Expected 5 messages (1 success + 4 error), got {len(retmsgs)}"

    # Count successful and error messages
    success_messages = [
        m for m in retmsgs if NextGenUILangGraphAgent.is_next_gen_ui_message(m)
    ]
    error_messages = [
        m for m in retmsgs if NextGenUILangGraphAgent.is_next_gen_ui_error_message(m)
    ]

    assert (
        len(success_messages) == 2
    ), f"Expected 2 success messages (AI + Tool), got {len(success_messages)}"
    assert (
        len(error_messages) == 3
    ), f"Expected 3 error Tool messages, got {len(error_messages)}"

    ai_messages = [m for m in retmsgs if m.type == "ai"]
    assert len(ai_messages) == 1

    tool_messages = [m for m in retmsgs if m.type == "tool"]
    assert len(tool_messages) == 4

    # Verify error message contents
    error_tool_messages = [m for m in error_messages if m.type == "tool"]
    assert len(error_tool_messages) == 3
    error_contents = [m.content for m in error_tool_messages]
    assert any("error_selection" in content for content in error_contents)
    assert any("error_transformation" in content for content in error_contents)
    assert any("error_rendering" in content for content in error_contents)

    # Verify UI blocks are present
    c_data: ComponentDataOneCard = components_data[0]

    ui_blocks = result["ui_blocks"]
    assert len(ui_blocks) == 1
    ui_block: UIBlock = ui_blocks[0]
    assert ui_block.id == "success"
    assert ui_block.configuration is not None
    assert ui_block.rendering is not None
    assert ui_block.rendering.id == "success"
    assert ui_block.rendering.content == c_data.model_dump_json()

    # Verify content of the success_messages, must be UIBlock because of agent configuration
    for message in success_messages:
        if message.type == "tool":
            assert isinstance(message, ToolMessage)
            assert message.type == "tool"
            assert message.name == "ngui_json"
            assert message.content == ui_block.model_dump_json()
            assert UIBlock.model_validate(json.loads(str(message.content)))
        elif message.type == "ai":
            assert isinstance(message, AIMessage)
            assert message.type == "ai"
            assert message.name == "ngui_json"
            assert (
                message.content == "Successfully generated 1 UI components. Failed: 3"
            )
            assert len(message.tool_calls) == 4


if __name__ == "__main__":
    asyncio.run(test_agent_ERROR_HANDLING_AT_DIFFERENT_STAGES())
