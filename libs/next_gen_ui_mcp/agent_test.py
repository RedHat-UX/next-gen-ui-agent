import json
from typing import List
from unittest.mock import AsyncMock, patch

import pytest
from fastmcp import Client, Context
from fastmcp.exceptions import ToolError
from mcp import CreateMessageResult, types
from mcp.types import ModelPreferences
from next_gen_ui_agent.data_transform.types import ComponentDataBaseWithArrayValueFileds
from next_gen_ui_agent.types import InputData, UIComponentMetadata
from next_gen_ui_mcp import MCPGenerateUIOutput, NextGenUIMCPServer
from next_gen_ui_mcp.__main__ import add_health_routes
from next_gen_ui_mcp.agent_config import (
    MCPAgentConfig,
    MCPAgentToolConfig,
    MCPAgentToolsConfig,
    MCPConfig,
)
from next_gen_ui_testing.data_set_movies import find_movie
from next_gen_ui_testing.model import MockedExceptionInference, MockedInference
from starlette.routing import Route  # pants: no-infer-dep

MOCKED_INFERENCE_THROW_STRING = "THROW-TEST-EXCEPTION"


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
    return MockedInference(mocked_component, MOCKED_INFERENCE_THROW_STRING)


class TestGenerateUIComponent:
    """Tests for generate_ui_component tool."""

    @pytest.mark.asyncio
    async def test_basic_functionality(self, external_inference) -> None:
        ngui_agent = NextGenUIMCPServer(
            config=MCPAgentConfig(component_system="json"),
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
                    "data_type": "movie_detail",
                    "data_id": "external_test_id",
                },
            )

        # Verify the result
        assert result is not None

        # Parse the JSON response
        output = MCPGenerateUIOutput.model_validate(result.data)
        assert output.summary == (
            "Component is rendered in UI. data_type: 'movie_detail', title: 'Toy Story External', component_type: one-card"
        )

        rendering = output.blocks[0].rendering
        # Verify the component structure
        assert rendering is not None
        assert rendering.id == "external_test_id"

        # Parse the inner content to verify the UI component structure
        assert rendering.content is not None
        rendering_json = ComponentDataBaseWithArrayValueFileds.model_validate_json(
            rendering.content
        )
        assert rendering_json.component == "one-card"
        assert rendering_json.title == "Toy Story External"

    @pytest.mark.asyncio
    async def test_sampling_inference_bad_return_type(self) -> None:
        # client sampling handler with mocked response
        async def sampling_handler_image(_messages, _params, _context):
            image = types.ImageContent(type="image", data="", mimeType="t")
            response = CreateMessageResult(content=image, role="assistant", model="t")
            return response

        ngui_agent = NextGenUIMCPServer(config=MCPAgentConfig(component_system="json"))

        # Get the FastMCP server
        mcp_server = ngui_agent.get_mcp_server()

        # Create test input data
        movies_data = find_movie("Toy Story")

        # Mock the context methods to avoid the "context not available" error during testing
        async with Client(
            mcp_server,
            sampling_handler=sampling_handler_image,
        ) as client:
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
    async def test_sampling_not_available(self) -> None:
        """Test error handling when MCP sampling is needed but client doesn't support it."""
        # Create agent configured for MCP sampling (no external inference)
        ngui_agent = NextGenUIMCPServer(
            config=MCPAgentConfig(component_system="json"),
            # NOTE: No inference parameter = expects to use MCP sampling
        )

        movies_data = find_movie("Toy Story")

        # Create client WITHOUT sampling_handler - this client won't support sampling
        async with Client(ngui_agent.get_mcp_server()) as client:
            with pytest.raises(ToolError) as excinfo:
                await client.call_tool(
                    "generate_ui_component",
                    {
                        "user_prompt": "Tell me brief details of Toy Story",
                        "data": json.dumps(movies_data, default=str),
                        "data_type": "movie_detail",
                    },
                )

            # Verify the error message indicates sampling is not available
            error_msg = str(excinfo.value)
            assert "MCP sampling is not available" in error_msg
            assert "does not support the 'sampling' capability" in error_msg

    @pytest.mark.asyncio
    async def test_session_id(self, external_inference) -> None:
        ngui_agent = NextGenUIMCPServer(
            config=MCPAgentConfig(component_system="json"),
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
                    "session_id": "extra_argument_ignored",
                },
            )
        assert result is not None

    @pytest.mark.asyncio
    async def test_data_id_generation(self, external_inference) -> None:
        ngui_agent = NextGenUIMCPServer(
            config=MCPAgentConfig(component_system="json"),
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
    async def test_no_data_validation(self, external_inference) -> None:
        ngui_agent = NextGenUIMCPServer(
            config=MCPAgentConfig(component_system="json"),
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
        assert (
            str(excinfo.value)
            == "Input validation error: 'data' is a required property"
        )

    @pytest.mark.asyncio
    async def test_bad_json_handling(self, external_inference) -> None:
        """
        Test how bad input (invalid json) is propagated to client.
        Important part of agentic flow where agent can fix the input based on the error message.
        """
        ngui_agent = NextGenUIMCPServer(
            config=MCPAgentConfig(component_system="json"),
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
    async def test_data_configuration(self, external_inference) -> None:
        ngui_agent = NextGenUIMCPServer(
            config=MCPAgentConfig(component_system="json"),
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
                    "data_type_metadata": '{"tool": "find_movie", "args": {"title": "Toy Story"}}',
                },
            )

        # Verify the result
        assert result is not None

        # Parse the JSON response
        output = MCPGenerateUIOutput.model_validate(result.data)
        configuration = output.blocks[0].configuration
        assert configuration is not None
        assert configuration.data_type == "data_type_ignored"
        assert (
            configuration.data_type_metadata
            == '{"tool": "find_movie", "args": {"title": "Toy Story"}}'
        )
        assert configuration.input_data_transformer_name == "json"
        assert configuration.json_wrapping_field_name == "data_type_ignored"

        component_metadata = configuration.component_metadata
        assert component_metadata is not None
        assert component_metadata.component == "one-card"
        assert component_metadata.title == "Toy Story External"
        assert component_metadata.fields is not None

        assert component_metadata.fields[0].data_path == "$..movie.title"
        assert component_metadata.fields[0].id == "title"

    @pytest.mark.asyncio
    async def test_inference_error(self) -> None:
        inference = MockedExceptionInference(Exception("call model test error"))

        # Create agent with external inference (not using MCP sampling)
        ngui_agent = NextGenUIMCPServer(
            config=MCPAgentConfig(component_system="json"),
            inference=inference,
            name="TestAgentExternal",
        )

        # Get the FastMCP server
        mcp_server = ngui_agent.get_mcp_server()
        with patch.object(Context, "info", new_callable=AsyncMock) as mock_info:
            with patch.object(Context, "error", new_callable=AsyncMock) as mock_error:
                async with Client(mcp_server) as client:
                    with pytest.raises(Exception, match="call model test error"):
                        await client.call_tool(
                            "generate_ui_component",
                            {
                                "user_prompt": "Tell me brief details of Toy Story",
                                "data": '{"a": "b"}',
                                "data_type": "data_type_ignored",
                                "data_id": "external_test_id",
                            },
                        )
        mock_info.assert_any_call("Using external inference provider...")
        mock_error.assert_any_call("UI generation failed: call model test error")

    @pytest.mark.asyncio
    async def test_data_type_metadata_passed_through(self, external_inference) -> None:
        """Test that data_type_metadata is correctly passed through to the configuration."""
        ngui_agent = NextGenUIMCPServer(
            config=MCPAgentConfig(component_system="json"),
            name="TestAgentExternal",
            inference=external_inference,
        )

        movies_data = find_movie("Toy Story")
        test_metadata = '{"tool": "search", "query": "test", "params": {"limit": 10}}'

        async with Client(ngui_agent.get_mcp_server()) as client:
            result = await client.call_tool(
                "generate_ui_component",
                {
                    "user_prompt": "Tell me brief details of Toy Story",
                    "data": json.dumps(movies_data, default=str),
                    "data_type": "movie_detail",
                    "data_type_metadata": test_metadata,
                    "data_id": "test_id",
                },
            )

        # Verify the result
        assert result is not None

        # Parse the JSON response
        output = MCPGenerateUIOutput.model_validate(result.data)
        configuration = output.blocks[0].configuration
        assert configuration is not None
        assert configuration.data_type == "movie_detail"
        assert configuration.data_type_metadata == test_metadata


class TestGenerateUIMultipleComponents:
    """Tests for generate_ui_multiple_components tool."""

    @pytest.mark.asyncio
    async def test_sampling_inference(self) -> None:
        """Test the MCP agent's generate_ui tool functionality with mocked sampling."""

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

        ngui_agent = NextGenUIMCPServer(config=MCPAgentConfig(component_system="json"))

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
        rendering_json = ComponentDataBaseWithArrayValueFileds.model_validate_json(
            rendering.content
        )
        assert rendering_json.component == "one-card"
        assert rendering_json.title == "Toy Story"

        # Verify some field data
        assert len(rendering_json.fields) == 3
        assert rendering_json.fields[0].name == "Title"
        assert rendering_json.fields[0].data == ["Toy Story"]

        assert rendering_json.fields[1].name == "Year"
        assert rendering_json.fields[1].data == [1995]

        mock_info.assert_any_call("Using MCP sampling to leverage client's LLM...")

    @pytest.mark.asyncio
    async def test_external_inference(self, external_inference) -> None:
        """Test the MCP agent's generate_ui tool functionality with external inference provider."""

        # Create agent with external inference (not using MCP sampling)
        ngui_agent = NextGenUIMCPServer(
            config=MCPAgentConfig(component_system="json"),
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
        rendering_json = ComponentDataBaseWithArrayValueFileds.model_validate_json(
            rendering.content
        )

        assert rendering_json.component == "one-card"
        assert rendering_json.title == "Toy Story External"

        # Verify some field data
        assert len(rendering_json.fields) == 4
        assert rendering_json.fields[0].id == "title"
        assert rendering_json.fields[0].name == "Title"
        assert rendering_json.fields[0].data == ["Toy Story"]

        assert rendering_json.fields[1].name == "Year"
        assert rendering_json.fields[1].data == [1995]

        # Verify summary
        expected_summary = (
            "UI components generation summary:"
            "\nSuccessful generated components:"
            "\n1. title: 'Toy Story External', component_type: one-card"
        )
        assert output.summary == expected_summary

        content = result.content[0].text
        assert content == expected_summary

        # Verify that the mock_info was called with the external inference message
        mock_info.assert_any_call("Using external inference provider...")

    @pytest.mark.asyncio
    async def test_external_inference_no_structured_output(
        self, external_inference
    ) -> None:
        """Test the MCP agent's generate_ui tool functionality with external inference provider."""

        # Create agent with external inference (not using MCP sampling)
        ngui_agent = NextGenUIMCPServer(
            config=MCPAgentConfig(component_system="json"),
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
    async def test_session_id(self, external_inference) -> None:
        ngui_agent = NextGenUIMCPServer(
            config=MCPAgentConfig(component_system="json"),
            inference=external_inference,
        )

        movies_data = find_movie("Toy Story")
        input_data: List[InputData] = [
            {"id": "external_test_id", "data": json.dumps(movies_data, default=str)}
        ]

        async with Client(ngui_agent.get_mcp_server()) as client:
            result = await client.call_tool(
                "generate_ui_multiple_components",
                {
                    "user_prompt": "Tell me brief details of Toy Story",
                    "structured_data": input_data,
                    "session_id": "extra_argument_ignored",
                },
            )
        assert result is not None

    @pytest.mark.asyncio
    async def test_no_data_validation(self, external_inference) -> None:
        ngui_agent = NextGenUIMCPServer(
            config=MCPAgentConfig(component_system="json"),
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
    async def test_partial_error_handling(self, external_inference) -> None:
        # Create agent with external inference (not using MCP sampling)
        ngui_agent = NextGenUIMCPServer(
            config=MCPAgentConfig(component_system="json"),
            inference=external_inference,
        )

        # Create test input data
        movies_data = find_movie("Toy Story")
        input_data: List[InputData] = [
            {"id": "test_id1", "data": json.dumps(movies_data, default=str)},
            {
                "id": "test_id2",
                "data": json.dumps(obj={"a": MOCKED_INFERENCE_THROW_STRING}),
            },
            {"id": "test_id3", "data": json.dumps(movies_data, default=str)},
        ]

        # Get the FastMCP server
        mcp_server = ngui_agent.get_mcp_server()
        with patch.object(Context, "info", new_callable=AsyncMock):
            with patch.object(Context, "error", new_callable=AsyncMock):
                async with Client(mcp_server) as client:
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

        rendering1 = output.blocks[0].rendering
        assert rendering1 is not None
        assert rendering1.id == "test_id1"
        rendering2 = output.blocks[1].rendering
        assert rendering2 is not None
        assert rendering2.id == "test_id3"

        assert output.summary == (
            "UI components generation summary:"
            "\nSuccessful generated components:"
            "\n1. title: 'Toy Story External', component_type: one-card"
            "\n2. title: 'Toy Story External', component_type: one-card"
            "\nFailed component generation:"
            "\n1. UI generation failed for this component. THROW-TEST-EXCEPTION"
        )

    @pytest.mark.asyncio
    async def test_structured_data_with_type_metadata(self, external_inference) -> None:
        """Test that type_metadata in structured_data is preserved in output configuration."""
        ngui_agent = NextGenUIMCPServer(
            config=MCPAgentConfig(component_system="json"),
            name="TestAgentExternal",
            inference=external_inference,
        )

        movies_data = find_movie("Toy Story")
        test_metadata = '{"tool": "find_movie", "args": {"title": "Toy Story"}}'
        input_data: List[InputData] = [
            {
                "id": "test_id",
                "data": json.dumps(movies_data, default=str),
                "type": "movie_detail",
                "type_metadata": test_metadata,
            }
        ]

        async with Client(ngui_agent.get_mcp_server()) as client:
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
        assert len(output.blocks) == 1

        configuration = output.blocks[0].configuration
        assert configuration is not None
        assert configuration.data_type == "movie_detail"
        assert configuration.data_type_metadata == test_metadata


class TestToolDescriptions:
    """Tests for tool description configuration and overrides."""

    @pytest.mark.asyncio
    async def test_default_descriptions(self) -> None:
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
            == "Structured Input Data. Array of objects with 'id', 'data' and 'type' keys. NEVER generate this."
        )
        assert tool_generate_ui.description == (
            "Generate multiple UI components for given user_prompt. "
            "Always get fresh data from another tool first. "
            "It's adviced to run the tool as last tool call in the chain, to be able process all data from previous tools calls."
        )

    @pytest.mark.asyncio
    async def test_override_generate_ui_component(self) -> None:
        """Test that generate_ui_component description can be overridden via config."""
        custom_description = "Custom description for generate_ui_component tool"
        config = MCPAgentConfig(
            component_system="json",
            mcp=MCPConfig(
                tools=MCPAgentToolsConfig(
                    generate_ui_component=MCPAgentToolConfig(
                        description=custom_description
                    )
                )
            ),
        )

        ngui_agent = NextGenUIMCPServer(config=config, name="TestAgent")
        mcp_server = ngui_agent.get_mcp_server()

        async with Client(mcp_server) as client:
            tools = await client.list_tools()

        assert len(tools) == 2
        tool = next(t for t in tools if t.name == "generate_ui_component")
        assert tool.description == custom_description

    @pytest.mark.asyncio
    async def test_override_generate_ui_multiple_components(self) -> None:
        """Test that generate_ui_multiple_components description can be overridden via config."""
        custom_description = (
            "Custom description for generate_ui_multiple_components tool"
        )
        config = MCPAgentConfig(
            component_system="json",
            mcp=MCPConfig(
                tools=MCPAgentToolsConfig(
                    generate_ui_multiple_components=MCPAgentToolConfig(
                        description=custom_description
                    )
                )
            ),
        )

        ngui_agent = NextGenUIMCPServer(config=config, name="TestAgent")
        mcp_server = ngui_agent.get_mcp_server()

        async with Client(mcp_server) as client:
            tools = await client.list_tools()

        assert len(tools) == 2
        tool = next(t for t in tools if t.name == "generate_ui_multiple_components")
        assert tool.description == custom_description

    @pytest.mark.asyncio
    async def test_override_both_tools(self) -> None:
        """Test that both tool descriptions can be overridden simultaneously."""
        custom_desc_single = "Custom description for single component tool"
        custom_desc_multiple = "Custom description for multiple components tool"
        config = MCPAgentConfig(
            component_system="json",
            mcp=MCPConfig(
                tools=MCPAgentToolsConfig(
                    generate_ui_component=MCPAgentToolConfig(
                        description=custom_desc_single
                    ),
                    generate_ui_multiple_components=MCPAgentToolConfig(
                        description=custom_desc_multiple
                    ),
                )
            ),
        )

        ngui_agent = NextGenUIMCPServer(config=config, name="TestAgent")
        mcp_server = ngui_agent.get_mcp_server()

        async with Client(mcp_server) as client:
            tools = await client.list_tools()

        assert len(tools) == 2
        tool_single = next(t for t in tools if t.name == "generate_ui_component")
        tool_multiple = next(
            t for t in tools if t.name == "generate_ui_multiple_components"
        )
        assert tool_single.description == custom_desc_single
        assert tool_multiple.description == custom_desc_multiple

    @pytest.mark.asyncio
    async def test_empty_string_falls_back_to_default(self) -> None:
        """Test that empty string description falls back to default."""
        default_description = (
            "Generate one UI component for given user_prompt and data. "
            "Always get fresh data from another tool first. "
            "It's adviced to run the tool as last tool call in the chain, to be able process all data from previous tools calls."
        )

        config = MCPAgentConfig(
            component_system="json",
            mcp=MCPConfig(
                tools=MCPAgentToolsConfig(
                    generate_ui_component=MCPAgentToolConfig(description="")
                )
            ),
        )

        ngui_agent = NextGenUIMCPServer(config=config, name="TestAgent")
        mcp_server = ngui_agent.get_mcp_server()

        async with Client(mcp_server) as client:
            tools = await client.list_tools()

        tool = next(t for t in tools if t.name == "generate_ui_component")
        assert tool.description == default_description

    @pytest.mark.asyncio
    async def test_whitespace_only_falls_back_to_default(self) -> None:
        """Test that whitespace-only description falls back to default."""
        default_description = (
            "Generate multiple UI components for given user_prompt. "
            "Always get fresh data from another tool first. "
            "It's adviced to run the tool as last tool call in the chain, to be able process all data from previous tools calls."
        )

        config = MCPAgentConfig(
            component_system="json",
            mcp=MCPConfig(
                tools=MCPAgentToolsConfig(
                    generate_ui_multiple_components=MCPAgentToolConfig(
                        description="   \n\t  "
                    )
                )
            ),
        )

        ngui_agent = NextGenUIMCPServer(config=config, name="TestAgent")
        mcp_server = ngui_agent.get_mcp_server()

        async with Client(mcp_server) as client:
            tools = await client.list_tools()

        tool = next(t for t in tools if t.name == "generate_ui_multiple_components")
        assert tool.description == default_description

    @pytest.mark.asyncio
    async def test_none_falls_back_to_default(self) -> None:
        """Test that None description falls back to default."""
        default_description = (
            "Generate one UI component for given user_prompt and data. "
            "Always get fresh data from another tool first. "
            "It's adviced to run the tool as last tool call in the chain, to be able process all data from previous tools calls."
        )

        config = MCPAgentConfig(
            component_system="json",
            mcp=MCPConfig(
                tools=MCPAgentToolsConfig(
                    generate_ui_component=MCPAgentToolConfig(description=None)
                )
            ),
        )

        ngui_agent = NextGenUIMCPServer(config=config, name="TestAgent")
        mcp_server = ngui_agent.get_mcp_server()

        async with Client(mcp_server) as client:
            tools = await client.list_tools()

        tool = next(t for t in tools if t.name == "generate_ui_component")
        assert tool.description == default_description

    @pytest.mark.asyncio
    async def test_missing_tool_config_falls_back_to_default(self) -> None:
        """Test that missing tool config falls back to default description."""
        default_description = (
            "Generate multiple UI components for given user_prompt. "
            "Always get fresh data from another tool first. "
            "It's adviced to run the tool as last tool call in the chain, to be able process all data from previous tools calls."
        )

        # Config with tools but without generate_ui_multiple_components config
        config = MCPAgentConfig(
            component_system="json",
            mcp=MCPConfig(tools=MCPAgentToolsConfig()),
        )

        ngui_agent = NextGenUIMCPServer(config=config, name="TestAgent")
        mcp_server = ngui_agent.get_mcp_server()

        async with Client(mcp_server) as client:
            tools = await client.list_tools()

        tool = next(t for t in tools if t.name == "generate_ui_multiple_components")
        assert tool.description == default_description

    @pytest.mark.asyncio
    async def test_override_argument_descriptions_generate_ui_component(self) -> None:
        """Test that generate_ui_component argument descriptions can be overridden via config."""
        custom_user_prompt_desc = "Custom user prompt description"
        custom_data_desc = "Custom data description"
        config = MCPAgentConfig(
            component_system="json",
            mcp=MCPConfig(
                tools=MCPAgentToolsConfig(
                    generate_ui_component=MCPAgentToolConfig(
                        argument_descriptions={
                            "user_prompt": custom_user_prompt_desc,
                            "data": custom_data_desc,
                        }
                    )
                )
            ),
        )

        ngui_agent = NextGenUIMCPServer(config=config, name="TestAgent")
        mcp_server = ngui_agent.get_mcp_server()

        async with Client(mcp_server) as client:
            tools = await client.list_tools()

        tool = next(t for t in tools if t.name == "generate_ui_component")
        assert (
            tool.inputSchema["properties"]["user_prompt"]["description"]
            == custom_user_prompt_desc
        )
        assert tool.inputSchema["properties"]["data"]["description"] == custom_data_desc
        # Verify other arguments still use default descriptions
        assert (
            tool.inputSchema["properties"]["data_type"]["description"]
            == "Name of tool call used for 'data' argument. COPY of tool name. Do not change anything! NEVER generate this."
        )

    @pytest.mark.asyncio
    async def test_override_argument_descriptions_generate_ui_multiple_components(
        self,
    ) -> None:
        """Test that generate_ui_multiple_components argument descriptions can be overridden via config."""
        custom_user_prompt_desc = (
            "Custom user prompt description for multiple components"
        )
        custom_structured_data_desc = "Custom structured data description"
        config = MCPAgentConfig(
            component_system="json",
            mcp=MCPConfig(
                tools=MCPAgentToolsConfig(
                    generate_ui_multiple_components=MCPAgentToolConfig(
                        argument_descriptions={
                            "user_prompt": custom_user_prompt_desc,
                            "structured_data": custom_structured_data_desc,
                        }
                    )
                )
            ),
        )

        ngui_agent = NextGenUIMCPServer(config=config, name="TestAgent")
        mcp_server = ngui_agent.get_mcp_server()

        async with Client(mcp_server) as client:
            tools = await client.list_tools()

        tool = next(t for t in tools if t.name == "generate_ui_multiple_components")
        assert (
            tool.inputSchema["properties"]["user_prompt"]["description"]
            == custom_user_prompt_desc
        )
        assert (
            tool.inputSchema["properties"]["structured_data"]["description"]
            == custom_structured_data_desc
        )

    @pytest.mark.asyncio
    async def test_override_single_argument_description(self) -> None:
        """Test that a single argument description can be overridden while others use defaults."""
        custom_data_desc = "Custom data description only"
        config = MCPAgentConfig(
            component_system="json",
            mcp=MCPConfig(
                tools=MCPAgentToolsConfig(
                    generate_ui_component=MCPAgentToolConfig(
                        argument_descriptions={"data": custom_data_desc}
                    )
                )
            ),
        )

        ngui_agent = NextGenUIMCPServer(config=config, name="TestAgent")
        mcp_server = ngui_agent.get_mcp_server()

        async with Client(mcp_server) as client:
            tools = await client.list_tools()

        tool = next(t for t in tools if t.name == "generate_ui_component")
        assert tool.inputSchema["properties"]["data"]["description"] == custom_data_desc
        # Verify other arguments still use default descriptions
        assert (
            tool.inputSchema["properties"]["user_prompt"]["description"]
            == "Original user query without any changes. Do not generate this."
        )
        assert (
            tool.inputSchema["properties"]["data_type"]["description"]
            == "Name of tool call used for 'data' argument. COPY of tool name. Do not change anything! NEVER generate this."
        )

    @pytest.mark.asyncio
    async def test_argument_descriptions_with_tool_description_override(self) -> None:
        """Test that both tool description and argument descriptions can be overridden together."""
        custom_tool_desc = "Custom tool description"
        custom_user_prompt_desc = "Custom user prompt description"
        config = MCPAgentConfig(
            component_system="json",
            mcp=MCPConfig(
                tools=MCPAgentToolsConfig(
                    generate_ui_component=MCPAgentToolConfig(
                        description=custom_tool_desc,
                        argument_descriptions={"user_prompt": custom_user_prompt_desc},
                    )
                )
            ),
        )

        ngui_agent = NextGenUIMCPServer(config=config, name="TestAgent")
        mcp_server = ngui_agent.get_mcp_server()

        async with Client(mcp_server) as client:
            tools = await client.list_tools()

        tool = next(t for t in tools if t.name == "generate_ui_component")
        assert tool.description == custom_tool_desc
        assert (
            tool.inputSchema["properties"]["user_prompt"]["description"]
            == custom_user_prompt_desc
        )

    @pytest.mark.asyncio
    async def test_empty_argument_descriptions_dict_uses_defaults(self) -> None:
        """Test that empty argument_descriptions dict falls back to defaults."""
        config = MCPAgentConfig(
            component_system="json",
            mcp=MCPConfig(
                tools=MCPAgentToolsConfig(
                    generate_ui_component=MCPAgentToolConfig(argument_descriptions={})
                )
            ),
        )

        ngui_agent = NextGenUIMCPServer(config=config, name="TestAgent")
        mcp_server = ngui_agent.get_mcp_server()

        async with Client(mcp_server) as client:
            tools = await client.list_tools()

        tool = next(t for t in tools if t.name == "generate_ui_component")
        # Verify all arguments use default descriptions
        assert (
            tool.inputSchema["properties"]["user_prompt"]["description"]
            == "Original user query without any changes. Do not generate this."
        )
        assert (
            tool.inputSchema["properties"]["data"]["description"]
            == "Input raw data. COPY of data from another tool call. Do not change anything!. NEVER generate this."
        )

    @pytest.mark.asyncio
    async def test_blank_string_argument_description_falls_back_to_default(
        self,
    ) -> None:
        """Test that blank string argument descriptions fall back to defaults."""
        default_data_desc = "Input raw data. COPY of data from another tool call. Do not change anything!. NEVER generate this."
        config = MCPAgentConfig(
            component_system="json",
            mcp=MCPConfig(
                tools=MCPAgentToolsConfig(
                    generate_ui_component=MCPAgentToolConfig(
                        argument_descriptions={"data": ""}
                    )
                )
            ),
        )

        ngui_agent = NextGenUIMCPServer(config=config, name="TestAgent")
        mcp_server = ngui_agent.get_mcp_server()

        async with Client(mcp_server) as client:
            tools = await client.list_tools()

        tool = next(t for t in tools if t.name == "generate_ui_component")
        assert (
            tool.inputSchema["properties"]["data"]["description"] == default_data_desc
        )

    @pytest.mark.asyncio
    async def test_whitespace_only_argument_description_falls_back_to_default(
        self,
    ) -> None:
        """Test that whitespace-only argument descriptions fall back to defaults."""
        default_user_prompt_desc = (
            "Original user query without any changes. Do not generate this."
        )
        config = MCPAgentConfig(
            component_system="json",
            mcp=MCPConfig(
                tools=MCPAgentToolsConfig(
                    generate_ui_component=MCPAgentToolConfig(
                        argument_descriptions={"user_prompt": "   \n\t  "}
                    )
                )
            ),
        )

        ngui_agent = NextGenUIMCPServer(config=config, name="TestAgent")
        mcp_server = ngui_agent.get_mcp_server()

        async with Client(mcp_server) as client:
            tools = await client.list_tools()

        tool = next(t for t in tools if t.name == "generate_ui_component")
        assert (
            tool.inputSchema["properties"]["user_prompt"]["description"]
            == default_user_prompt_desc
        )


class TestAgentConfiguration:
    """Tests for agent configuration options."""

    @pytest.mark.asyncio
    async def test_enabled_tools(self) -> None:
        ngui_agent = NextGenUIMCPServer(
            enabled_tools=["generate_ui_multiple_components"]
        )
        async with Client(ngui_agent.get_mcp_server()) as client:
            tools = await client.list_tools()
            assert len(tools) == 1
            assert tools[0].name == "generate_ui_multiple_components"

    def test_invalid_tool_name(self) -> None:
        with pytest.raises(Exception) as excinfo:
            NextGenUIMCPServer(enabled_tools=["bad_tool"])
        assert (
            str(excinfo.value)
            == "tool 'bad_tool' is no valid. Available tools are: ['generate_ui_component', 'generate_ui_multiple_components']"
        )


class TestSystemResources:
    """Tests for MCP system resources."""

    @pytest.mark.asyncio
    async def test_system_info_resource(self) -> None:
        """Test the MCP agent's system info resource."""
        # Create agent (no inference parameter needed with new MCP sampling approach)
        ngui_agent = NextGenUIMCPServer(
            config=MCPAgentConfig(component_system="json"), name="TestAgent"
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


class TestHealthRoutes:
    """Tests for health check routes."""

    def test_liveness_routes(self) -> None:
        ngui_agent = NextGenUIMCPServer(name="TestAgent")

        mcp_server = ngui_agent.get_mcp_server()

        add_health_routes(mcp_server)

        assert len(mcp_server._additional_http_routes) == 2

        assert isinstance(mcp_server._additional_http_routes[0], Route)
        assert mcp_server._additional_http_routes[0].path == "/liveness"
        assert isinstance(mcp_server._additional_http_routes[1], Route)
        assert mcp_server._additional_http_routes[1].path == "/readiness"


class TestMCPModelPreferences:
    """Tests for MCP sampling model preferences (hints and priorities)."""

    @pytest.mark.asyncio
    async def test_sampling_with_model_hints(self) -> None:
        """Test that model hints are passed correctly to MCP sampling."""
        # Setup mocked component response
        mocked_llm_response: UIComponentMetadata = UIComponentMetadata.model_validate(
            {
                "title": "Toy Story",
                "reasonForTheComponentSelection": "One item available in the data",
                "confidenceScore": "100%",
                "component": "one-card",
                "fields": [
                    {"name": "Title", "data_path": "movie.title"},
                ],
                "id": "test-id",
            }
        )

        # Capture model preferences from the sampling request
        captured_preferences: ModelPreferences | None = None

        async def sampling_handler(_messages, params, _context):
            # Capture model preferences if present
            if hasattr(params, "modelPreferences"):
                nonlocal captured_preferences
                captured_preferences = params.modelPreferences
            # Return mocked response
            return CreateMessageResult(
                content=types.TextContent(
                    type="text", text=mocked_llm_response.model_dump_json()
                ),
                role="assistant",
                model="claude-3-sonnet",
            )

        # Create server with model hints
        ngui_agent = NextGenUIMCPServer(
            config=MCPAgentConfig(component_system="json"),
            sampling_model_hints=["claude-3-sonnet", "claude"],
        )

        movies_data = find_movie("Toy Story")

        with patch.object(Context, "info", new_callable=AsyncMock):
            async with Client(
                ngui_agent.get_mcp_server(), sampling_handler=sampling_handler
            ) as client:
                await client.call_tool(
                    "generate_ui_component",
                    {
                        "user_prompt": "Tell me about Toy Story",
                        "data": json.dumps(movies_data, default=str),
                        "data_type": "movie_detail",
                    },
                )

        # Verify hints were passed
        assert captured_preferences is not None
        assert captured_preferences.hints is not None
        assert len(captured_preferences.hints) == 2
        assert captured_preferences.hints[0].name == "claude-3-sonnet"
        assert captured_preferences.hints[1].name == "claude"

    @pytest.mark.asyncio
    async def test_sampling_with_priorities(self) -> None:
        """Test that priority values are passed correctly to MCP sampling."""
        mocked_llm_response: UIComponentMetadata = UIComponentMetadata.model_validate(
            {
                "title": "Toy Story",
                "reasonForTheComponentSelection": "Test",
                "confidenceScore": "100%",
                "component": "one-card",
                "fields": [{"name": "Title", "data_path": "movie.title"}],
                "id": "test-id",
            }
        )

        captured_preferences: ModelPreferences | None = None

        async def sampling_handler(_messages, params, _context):
            if hasattr(params, "modelPreferences"):
                nonlocal captured_preferences
                captured_preferences = params.modelPreferences
            return CreateMessageResult(
                content=types.TextContent(
                    type="text", text=mocked_llm_response.model_dump_json()
                ),
                role="assistant",
                model="test-model",
            )

        # Create server with priority values
        ngui_agent = NextGenUIMCPServer(
            config=MCPAgentConfig(component_system="json"),
            sampling_cost_priority=0.8,
            sampling_speed_priority=0.5,
            sampling_intelligence_priority=0.7,
        )

        movies_data = find_movie("Toy Story")

        with patch.object(Context, "info", new_callable=AsyncMock):
            async with Client(
                ngui_agent.get_mcp_server(), sampling_handler=sampling_handler
            ) as client:
                await client.call_tool(
                    "generate_ui_component",
                    {
                        "user_prompt": "Tell me about Toy Story",
                        "data": json.dumps(movies_data, default=str),
                        "data_type": "movie_detail",
                    },
                )

        # Verify priorities were passed
        assert captured_preferences is not None
        assert captured_preferences.costPriority == 0.8
        assert captured_preferences.speedPriority == 0.5
        assert captured_preferences.intelligencePriority == 0.7

    @pytest.mark.asyncio
    async def test_sampling_without_preferences(self) -> None:
        """Test backward compatibility - no preferences should work as before."""
        mocked_llm_response: UIComponentMetadata = UIComponentMetadata.model_validate(
            {
                "title": "Toy Story",
                "reasonForTheComponentSelection": "Test",
                "confidenceScore": "100%",
                "component": "one-card",
                "fields": [{"name": "Title", "data_path": "movie.title"}],
                "id": "test-id",
            }
        )

        captured_preferences: ModelPreferences | None = None

        async def sampling_handler(_messages, params, _context):
            # Check if modelPreferences is present (should be None or not present)
            if hasattr(params, "modelPreferences"):
                nonlocal captured_preferences
                captured_preferences = params.modelPreferences
            return CreateMessageResult(
                content=types.TextContent(
                    type="text", text=mocked_llm_response.model_dump_json()
                ),
                role="assistant",
                model="test-model",
            )

        # Create server without any preferences
        ngui_agent = NextGenUIMCPServer(config=MCPAgentConfig(component_system="json"))

        movies_data = find_movie("Toy Story")

        with patch.object(Context, "info", new_callable=AsyncMock):
            async with Client(
                ngui_agent.get_mcp_server(), sampling_handler=sampling_handler
            ) as client:
                await client.call_tool(
                    "generate_ui_component",
                    {
                        "user_prompt": "Tell me about Toy Story",
                        "data": json.dumps(movies_data, default=str),
                        "data_type": "movie_detail",
                    },
                )

        # Verify modelPreferences is None (backward compatibility - no preferences)
        assert captured_preferences is None

    @pytest.mark.asyncio
    async def test_sampling_preferences_multiple_components(self) -> None:
        """Test that preferences work with generate_ui_multiple_components."""
        mocked_llm_response: UIComponentMetadata = UIComponentMetadata.model_validate(
            {
                "title": "Toy Story",
                "reasonForTheComponentSelection": "Test",
                "confidenceScore": "100%",
                "component": "one-card",
                "fields": [{"name": "Title", "data_path": "movie.title"}],
                "id": "test-id",
            }
        )

        captured_preferences: ModelPreferences | None = None

        async def sampling_handler(_messages, params, _context):
            if hasattr(params, "modelPreferences"):
                nonlocal captured_preferences
                captured_preferences = params.modelPreferences
            return CreateMessageResult(
                content=types.TextContent(
                    type="text", text=mocked_llm_response.model_dump_json()
                ),
                role="assistant",
                model="claude-3-sonnet",
            )

        ngui_agent = NextGenUIMCPServer(
            config=MCPAgentConfig(component_system="json"),
            sampling_model_hints=["claude-3-sonnet"],
            sampling_intelligence_priority=0.9,
        )

        movies_data = find_movie("Toy Story")
        input_data: List[InputData] = [
            {"id": "test_id", "data": json.dumps(movies_data, default=str)}
        ]

        with patch.object(Context, "info", new_callable=AsyncMock):
            async with Client(
                ngui_agent.get_mcp_server(), sampling_handler=sampling_handler
            ) as client:
                await client.call_tool(
                    "generate_ui_multiple_components",
                    {
                        "user_prompt": "Tell me about Toy Story",
                        "structured_data": input_data,
                    },
                )

        # Verify preferences were passed
        assert captured_preferences is not None
        assert captured_preferences.hints is not None
        assert captured_preferences.hints[0].name == "claude-3-sonnet"
        assert captured_preferences.intelligencePriority == 0.9
