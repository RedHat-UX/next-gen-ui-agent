import json
from typing import Any, Dict
from unittest.mock import AsyncMock

import pytest
from fastmcp import Client
from llama_stack_client import AsyncLlamaStackClient, LlamaStackClient
from llama_stack_client.types.tool_invocation_result import ToolInvocationResult
from mcp.types import TextContent
from next_gen_ui_agent.types import UIComponentMetadata
from next_gen_ui_mcp.agent import NextGenUIMCPAgent
from next_gen_ui_testing.data_set_movies import find_movie
from next_gen_ui_testing.model import MockedInference

# Initialize the Llama-Stack client
# This assumes the server is running at the default address
client = LlamaStackClient()

# Define the tool you want to call and its arguments
tool_name_to_call = "get_weather"
tool_arguments: Dict[str, Any] = {"city": "Warsaw"}

try:
    # Directly invoke the tool using call_tool
    print(
        f"Directly calling tool: '{tool_name_to_call}' with arguments: {tool_arguments}"
    )

    # Pass tool_arguments as **kwargs to match the expected parameter type
    tool_result = client.tool_runtime.invoke_tool(
        tool_name=tool_name_to_call, kwargs=tool_arguments
    )

    # The result from the tool execution is returned directly
    print("\n✅ Tool successfully called!")
    print("Result:", tool_result)

except Exception as e:
    print(f"\n❌ An error occurred: {e}")


@pytest.mark.asyncio
async def test_mcp_agent_generate_ui():
    """Test the MCP agent's main generate_ui tool."""
    # Setup mocked component
    mocked_component: UIComponentMetadata = UIComponentMetadata.model_validate(
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

    # Create agent with mocked inference
    mocked_inference = MockedInference(mocked_component)
    ngui_agent = NextGenUIMCPAgent(
        component_system="json", inference=mocked_inference, name="NGUI Agent"
    )

    # Get the FastMCP server
    mcp_server = ngui_agent.get_mcp_server()

    # Create test input data
    movies_data = find_movie("Toy Story")
    input_data = [{"id": "test_id", "data": json.dumps(movies_data, default=str)}]

    # Test using the MCP client
    async with Client(mcp_server) as client:
        # Test the generate_ui tool (main functionality)
        result = await client.call_tool(
            "generate_ui",
            {
                "user_prompt": "Tell me brief details of Toy Story",
                "input_data": input_data,
            },
        )

        # Verify the result
        assert result.content is not None
        assert len(result.content) > 0
        assert isinstance(result.content[0], TextContent)
        text_content = result.content[0].text
        assert text_content is not None

        tool_result = ToolInvocationResult(content=text_content)

        mock_llama_stack_client = AsyncMock(spec=LlamaStackClient)
        mock_llama_stack_client.tool_runtime._post = AsyncMock(return_value=tool_result)

        # Pass tool_arguments as **kwargs to match the expected parameter type
        tool_result = mock_llama_stack_client.tool_runtime.invoke_tool(
            tool_name=tool_name_to_call, kwargs=tool_arguments
        )

        assert str(tool_result) == "{}"
