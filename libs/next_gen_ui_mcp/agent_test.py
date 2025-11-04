import json
from typing import List
from unittest.mock import AsyncMock, patch

import pytest
from fastmcp import Client, Context
from fastmcp.exceptions import ToolError
from mcp import CreateMessageResult, types
from next_gen_ui_agent.types import AgentConfig, InputData, UIComponentMetadata
from next_gen_ui_mcp import MCPGenerateUIOutput, NextGenUIMCPServer
from next_gen_ui_mcp.__main__ import add_health_routes
from next_gen_ui_testing.data_set_movies import find_movie
from next_gen_ui_testing.model import MockedExceptionInference, MockedInference


@pytest.mark.asyncio
async def test_generate_ui_multiple_components_sampling_inference() -> None:
    """Test the MCP agent's generate_ui tool functionality with mocked sampling."""
    from unittest.mock import patch

    # Setup mocked component
    mocked_llm_response: UIComponentMetadata = UIComponentMetadata.model_validate(
        {
            "title": "Toy Story",
            "reasonForTheComponentSelection": "One item available in the data",
            "confidenceScore": "100%",
            "component": "one-card",
            "fields": [
                {"name": "Title", "data_path": "movie.title"},
                {"name": "Year", "data_path": "movie.year"},
                {"name": "IMDB Rating", "data_path": "movie.imdbRating"},
            ],
            "id": "2ff0f4bd-6b66-4b22-a7eb-8bb0365f52b1",
        }
    )

    # client sampling handler with mocked response
    async def sampling_handler(_messages, _params, _context) -> str:
        return mocked_llm_response.model_dump_json()

    ngui_agent = NextGenUIMCPServer(config=AgentConfig(component_system="json"))

    # Get the FastMCP server
    mcp_server = ngui_agent.get_mcp_server()

    # Create test input data
    movies_data = find_movie("Toy Story")
    input_data: List[InputData] = [
        {"id": "test_id", "data": json.dumps(movies_data, default=str)}
    ]

    # Mock the context methods to avoid the "context not available" error during testing
    with patch.object(Context, "info", new_callable=AsyncMock) as mock_info:
        async with Client(mcp_server, sampling_handler=sampling_handler) as client:
            # Test the generate_ui tool through the MCP server
            result = await client.call_tool(
                "generate_ui_multiple_components",
                {
                    "user_prompt": "Tell me brief details of Toy Story",
                    "structured_data": input_data,
                },
            )

    # Verify the result
    assert result is not None

    # Parse the JSON response
    output = MCPGenerateUIOutput.model_validate(result.structured_content)

    rendering = output.blocks[0].rendering

    # Verify the component structure
    assert rendering is not None
    assert rendering.id == "test_id"

    assert rendering.content is not None
    component = json.loads(rendering.content)
    assert component["component"] == "one-card"
    assert component["title"] == "Toy Story"

    # Verify some field data
    assert len(component["fields"]) == 3
    assert component["fields"][0]["name"] == "Title"
    assert component["fields"][0]["data"] == ["Toy Story"]

    assert component["fields"][1]["name"] == "Year"
    assert component["fields"][1]["data"] == [1995]

    mock_info.assert_any_call("Using MCP sampling to leverage client's LLM...")


@pytest.mark.asyncio
async def test_generate_ui_multiple_components_sampling_inference_bad_return_type() -> (
    None
):
    # client sampling handler with mocked response
    async def sampling_handler_image(_messages, _params, _context):
        image = types.ImageContent(type="image", data="", mimeType="t")
        response = CreateMessageResult(content=image, role="assistant", model="t")
        return response

    ngui_agent = NextGenUIMCPServer(config=AgentConfig(component_system="json"))

    # Get the FastMCP server
    mcp_server = ngui_agent.get_mcp_server()

    # Create test input data
    movies_data = find_movie("Toy Story")
    input_data: List[InputData] = [
        {"id": "test_id", "data": json.dumps(movies_data, default=str)}
    ]

    # Mock the context methods to avoid the "context not available" error during testing
    async with Client(mcp_server, sampling_handler=sampling_handler_image) as client:
        # Test the generate_ui tool through the MCP server
        with pytest.raises(Exception) as excinfo:
            await client.call_tool(
                "generate_ui_multiple_components",
                {
                    "user_prompt": "Tell me brief details of Toy Story",
                    "structured_data": input_data,
                },
            )
        assert (
            str(excinfo.value)
            == "Error calling tool 'generate_ui_multiple_components': Failed to call model via MCP sampling: Sample Response returned unknown type: image"
        )


@pytest.fixture()
def external_inference():
    # Setup mocked LLM response
    mocked_component: UIComponentMetadata = UIComponentMetadata.model_validate(
        {
            "title": "Toy Story External",
            "reasonForTheComponentSelection": "Single movie data item provided via external inference",
            "confidenceScore": "95%",
            "component": "one-card",
            "fields": [
                {"name": "Title", "data_path": "movie.title"},
                {"name": "Year", "data_path": "movie.year"},
                {"name": "IMDB Rating", "data_path": "movie.imdbRating"},
                {"name": "Runtime", "data_path": "movie.runtime"},
            ],
            "id": "external-inference-test-id",
        }
    )

    # Create external inference provider using MockedInference
    return MockedInference(mocked_component)


@pytest.mark.asyncio
async def test_generate_ui_multiple_components_external_inference(
    external_inference,
) -> None:
    """Test the MCP agent's generate_ui tool functionality with external inference provider."""

    # Create agent with external inference (not using MCP sampling)
    ngui_agent = NextGenUIMCPServer(
        config=AgentConfig(component_system="json"),
        name="TestAgentExternal",
        inference=external_inference,
    )

    # Get the FastMCP server
    mcp_server = ngui_agent.get_mcp_server()

    # Create test input data
    movies_data = find_movie("Toy Story")
    input_data: List[InputData] = [
        {"id": "external_test_id", "data": json.dumps(movies_data, default=str)}
    ]

    # Get the FastMCP server
    mcp_server = ngui_agent.get_mcp_server()
    with patch.object(Context, "info", new_callable=AsyncMock) as mock_info:
        async with Client(mcp_server) as client:
            # Test the generate_ui tool through the MCP server
            result = await client.call_tool(
                "generate_ui_multiple_components",
                {
                    "user_prompt": "Tell me brief details of Toy Story",
                    "structured_data": input_data,
                },
            )

    # Verify the result
    assert result is not None

    # Parse the JSON response
    output = MCPGenerateUIOutput.model_validate(result.data)

    rendering = output.blocks[0].rendering
    # Verify the component structure
    assert rendering is not None
    assert rendering.id == "external_test_id"

    # Parse the inner content to verify the UI component structure
    assert rendering.content is not None
    component = json.loads(rendering.content)
    assert component["component"] == "one-card"
    assert component["title"] == "Toy Story External"

    # Verify some field data
    assert len(component["fields"]) == 4
    assert component["fields"][0]["name"] == "Title"
    assert component["fields"][0]["data"] == ["Toy Story"]

    assert component["fields"][1]["name"] == "Year"
    assert component["fields"][1]["data"] == [1995]

    # Verify summary
    expected_summary = "Components are rendered in UI.\nCount: 1\n1. Title: 'Toy Story External', type: one-card"
    assert output.summary == expected_summary

    content = result.content[0].text
    assert content == expected_summary

    # Verify that the mock_info was called with the external inference message
    mock_info.assert_any_call("Using external inference provider...")


@pytest.mark.asyncio
async def test_generate_ui_multiple_components_external_inference_no_structured_output(
    external_inference,
) -> None:
    """Test the MCP agent's generate_ui tool functionality with external inference provider."""

    # Create agent with external inference (not using MCP sampling)
    ngui_agent = NextGenUIMCPServer(
        config=AgentConfig(component_system="json"),
        name="TestAgentExternal",
        inference=external_inference,
        structured_output_enabled=False,
    )

    # Get the FastMCP server
    mcp_server = ngui_agent.get_mcp_server()

    # Create test input data
    movies_data = find_movie("Toy Story")
    input_data: List[InputData] = [
        {"id": "external_test_id", "data": json.dumps(movies_data, default=str)}
    ]

    # Get the FastMCP server
    mcp_server = ngui_agent.get_mcp_server()
    async with Client(mcp_server) as client:
        # Test the generate_ui tool through the MCP server
        result = await client.call_tool(
            "generate_ui_multiple_components",
            {
                "user_prompt": "Tell me brief details of Toy Story",
                "structured_data": input_data,
            },
        )

    # Verify the result
    assert result is not None

    # Verify summary
    assert result.data is None
    assert result.structured_content is None

    # Parse the JSON response
    output = MCPGenerateUIOutput.model_validate_json(result.content[0].text)
    assert output.summary is not None
    assert len(output.blocks) == 1
    assert output.blocks[0].configuration is not None


@pytest.mark.asyncio
async def test_generate_ui_component(
    external_inference,
) -> None:
    ngui_agent = NextGenUIMCPServer(
        config=AgentConfig(component_system="json"),
        name="TestAgentExternal",
        inference=external_inference,
    )

    movies_data = find_movie("Toy Story")

    async with Client(ngui_agent.get_mcp_server()) as client:
        result = await client.call_tool(
            "generate_ui_component",
            {
                "user_prompt": "Tell me brief details of Toy Story",
                "data": json.dumps(movies_data, default=str),
                "data_type": "data_type_ignored",
                "data_id": "external_test_id",
            },
        )

    # Verify the result
    assert result is not None

    # Parse the JSON response
    output = MCPGenerateUIOutput.model_validate(result.data)
    assert (
        output.summary
        == "Component is rendered in UI. Title: 'Toy Story External', type: one-card"
    )

    rendering = output.blocks[0].rendering
    # Verify the component structure
    assert rendering is not None
    assert rendering.id == "external_test_id"

    # Parse the inner content to verify the UI component structure
    assert rendering.content is not None
    component = json.loads(rendering.content)
    assert component["component"] == "one-card"
    assert component["title"] == "Toy Story External"


@pytest.mark.asyncio
async def test_generate_ui_component_sampling_inference_bad_return_type() -> None:
    # client sampling handler with mocked response
    async def sampling_handler_image(_messages, _params, _context):
        image = types.ImageContent(type="image", data="", mimeType="t")
        response = CreateMessageResult(content=image, role="assistant", model="t")
        return response

    ngui_agent = NextGenUIMCPServer(config=AgentConfig(component_system="json"))

    # Get the FastMCP server
    mcp_server = ngui_agent.get_mcp_server()

    # Create test input data
    movies_data = find_movie("Toy Story")

    # Mock the context methods to avoid the "context not available" error during testing
    async with Client(mcp_server, sampling_handler=sampling_handler_image) as client:
        # Test the generate_ui tool through the MCP server
        with pytest.raises(Exception) as excinfo:
            await client.call_tool(
                "generate_ui_component",
                {
                    "user_prompt": "Tell me brief details of Toy Story",
                    "data": json.dumps(movies_data, default=str),
                    "data_type": "data_type_ignored",
                    "data_id": "external_test_id",
                },
            )
        assert (
            str(excinfo.value)
            == "Error calling tool 'generate_ui_component': Failed to call model via MCP sampling: Sample Response returned unknown type: image"
        )


@pytest.mark.asyncio
async def test_generate_ui_component_data_id_gen(
    external_inference,
) -> None:
    ngui_agent = NextGenUIMCPServer(
        config=AgentConfig(component_system="json"),
        name="TestAgentExternal",
        inference=external_inference,
    )

    movies_data = find_movie("Toy Story")

    async with Client(ngui_agent.get_mcp_server()) as client:
        result = await client.call_tool(
            "generate_ui_component",
            {
                "user_prompt": "Tell me brief details of Toy Story",
                "data": json.dumps(movies_data, default=str),
                "data_type": "data_type_ignored",
            },
        )

    # Verify the result
    assert result is not None

    # Parse the JSON response
    output = MCPGenerateUIOutput.model_validate(result.data)
    rendering = output.blocks[0].rendering
    # Verify the component structure
    assert rendering is not None
    assert rendering.id is not None
    assert rendering.id != "external_test_id"


@pytest.mark.asyncio
async def test_generate_ui_component_no_data(external_inference) -> None:
    ngui_agent = NextGenUIMCPServer(
        config=AgentConfig(component_system="json"),
        name="TestAgentExternal",
        inference=external_inference,
    )

    async with Client(ngui_agent.get_mcp_server()) as client:
        with pytest.raises(Exception) as excinfo:
            await client.call_tool(
                "generate_ui_component",
                {
                    "user_prompt": "Tell me brief details of Toy Story",
                    # "data": json.dumps(movies_data, default=str),
                    "data_type": "data_type_ignored",
                },
            )
    # Test standard MCP behaviour
    assert str(excinfo.value) == "Input validation error: 'data' is a required property"


@pytest.mark.asyncio
async def test_generate_ui_component_bad_json(external_inference) -> None:
    """
    Test how bad input (invalid json) is propagated to client.
    Important part of agentic flow where agent can fix the input based on the error message.
    """
    ngui_agent = NextGenUIMCPServer(
        config=AgentConfig(component_system="json"),
        name="TestAgentExternal",
        inference=external_inference,
    )

    movies_data = """{
        "languages": ["English"],
        "year": 1995,
        "imdbId": bad bad bad,
    }
"""

    async with Client(ngui_agent.get_mcp_server()) as client:
        with pytest.raises(ToolError) as excinfo:
            await client.call_tool(
                "generate_ui_component",
                {
                    "user_prompt": "Tell me brief details of Toy Story",
                    "data": movies_data,
                    "data_type": "data_type_ignored",
                },
            )
    # Test standard MCP behaviour
    assert (
        str(excinfo.value)
        == "Error calling tool 'generate_ui_component': Invalid JSON format of the Input Data: Expecting value: line 4 column 19 (char 76)"
    )


@pytest.mark.asyncio
async def test_generate_ui_multiple_components_no_data(external_inference) -> None:
    ngui_agent = NextGenUIMCPServer(
        config=AgentConfig(component_system="json"),
        name="TestAgentExternal",
        inference=external_inference,
    )

    async with Client(ngui_agent.get_mcp_server()) as client:
        with pytest.raises(Exception) as excinfo:
            await client.call_tool(
                "generate_ui_multiple_components",
                {
                    "user_prompt": "Tell me brief details of Toy Story",
                    "structured_data": [],
                },
            )
    assert (
        str(excinfo.value)
        == "Error calling tool 'generate_ui_multiple_components': No data provided! Get data from another tool again and then call this tool again."
    )


@pytest.mark.asyncio
async def test_generate_ui_component_data_configuration(external_inference) -> None:
    ngui_agent = NextGenUIMCPServer(
        config=AgentConfig(component_system="json"),
        name="TestAgentExternal",
        inference=external_inference,
    )

    movies_data = find_movie("Toy Story")

    async with Client(ngui_agent.get_mcp_server()) as client:
        result = await client.call_tool(
            "generate_ui_component",
            {
                "user_prompt": "Tell me brief details of Toy Story",
                "data": json.dumps(movies_data, default=str),
                "data_type": "data_type_ignored",
            },
        )

    # Verify the result
    assert result is not None

    # Parse the JSON response
    output = MCPGenerateUIOutput.model_validate(result.data)
    configuration = output.blocks[0].configuration
    assert configuration is not None
    assert configuration.data_type == "data_type_ignored"
    assert configuration.input_data_transformer_name == "json"
    assert configuration.json_wrapping_field_name == "data_type_ignored"

    component_metadata = configuration.component_metadata
    assert component_metadata is not None
    assert component_metadata.component == "one-card"
    assert component_metadata.title == "Toy Story External"
    assert component_metadata.fields is not None


@pytest.mark.asyncio
async def test_mcp_agent_system_info_resource() -> None:
    """Test the MCP agent's system info resource."""
    # Create agent (no inference parameter needed with new MCP sampling approach)
    ngui_agent = NextGenUIMCPServer(
        config=AgentConfig(component_system="json"), name="TestAgent"
    )

    # Get the FastMCP server
    mcp_server = ngui_agent.get_mcp_server()

    async with Client(mcp_server) as client:
        result = await client.read_resource("system://info")

        # Verify the result
        assert result is not None
        # Convert to list to handle Iterable type
        result_list = list(result)
        assert len(result_list) > 0
        text_content = result_list[0].text
        assert text_content is not None
        system_info = json.loads(text_content)
        assert system_info["agent_name"] == "NextGenUIMCPServer"
        assert system_info["component_system"] == "json"
        assert "capabilities" in system_info


@pytest.mark.asyncio
async def test_mcp_inference_error() -> None:
    from unittest.mock import patch

    inference = MockedExceptionInference(Exception("call model test error"))

    # Create agent with external inference (not using MCP sampling)
    ngui_agent = NextGenUIMCPServer(
        config=AgentConfig(component_system="json"),
        inference=inference,
        name="TestAgentExternal",
    )

    # Get the FastMCP server
    mcp_server = ngui_agent.get_mcp_server()
    input_data: List[InputData] = [{"id": "test_id", "data": '{"a": "b"}'}]
    with patch.object(Context, "info", new_callable=AsyncMock) as mock_info:
        with patch.object(Context, "error", new_callable=AsyncMock) as mock_error:
            async with Client(mcp_server) as client:
                with pytest.raises(Exception, match="call model test error"):
                    await client.call_tool(
                        "generate_ui_multiple_components",
                        {
                            "user_prompt": "Show me details about Toy Story movie with external inference",
                            "structured_data": input_data,
                        },
                    )
    mock_info.assert_any_call("Using external inference provider...")
    mock_error.assert_any_call("UI generation failed: call model test error")


@pytest.mark.asyncio
async def test_tool_generate_ui_description_all() -> None:
    ngui_agent = NextGenUIMCPServer(
        name="TestAgent",
        debug=False,
    )
    mcp_server = ngui_agent.get_mcp_server()

    async with Client(mcp_server) as client:
        tools = await client.list_tools()

    assert len(tools) == 2
    assert tools[0].name == "generate_ui_component"

    tool_generate_ui = tools[1]
    assert tool_generate_ui.name == "generate_ui_multiple_components"
    assert (
        tool_generate_ui.inputSchema["properties"]["user_prompt"]["description"]
        == "Original user query without any changes. Do not generate this."
    )
    assert (
        tool_generate_ui.inputSchema["properties"]["structured_data"]["description"]
        == "Structured Input Data. Array of objects with 'id' and 'data' keys. NEVER generate this."
    )
    assert tool_generate_ui.description == (
        "Generate multiple UI components for given user_prompt. "
        "Always get fresh data from another tool first. "
        "It's adviced to run the tool as last tool call in the chain, to be able process all data from previous tools calls."
    )


@pytest.mark.asyncio
async def test_config_tools() -> None:
    ngui_agent = NextGenUIMCPServer(enabled_tools=["generate_ui_multiple_components"])
    async with Client(ngui_agent.get_mcp_server()) as client:
        tools = await client.list_tools()
        assert len(tools) == 1
        assert tools[0].name == "generate_ui_multiple_components"


def test_config_tools_bad() -> None:
    with pytest.raises(Exception) as excinfo:
        NextGenUIMCPServer(enabled_tools=["bad_tool"])
    assert (
        str(excinfo.value)
        == "tool 'bad_tool' is no valid. Available tools are: ['generate_ui_component', 'generate_ui_multiple_components']"
    )


def test_liveness() -> None:
    ngui_agent = NextGenUIMCPServer(name="TestAgent")

    mcp_server = ngui_agent.get_mcp_server()

    add_health_routes(mcp_server)

    assert len(mcp_server._additional_http_routes) == 2

    from starlette.routing import Route  # pants: no-infer-dep

    assert isinstance(mcp_server._additional_http_routes[0], Route)
    assert mcp_server._additional_http_routes[0].path == "/liveness"
    assert isinstance(mcp_server._additional_http_routes[1], Route)
    assert mcp_server._additional_http_routes[1].path == "/readiness"
