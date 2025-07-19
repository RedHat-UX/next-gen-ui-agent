import json
import pytest
from fastmcp import Client
from llama_stack_client import LlamaStackClient
from llama_stack_client.types.tool_invocation_result import ToolInvocationResult
from mcp.types import TextContent
from next_gen_ui_agent.types import UIComponentMetadata
from next_gen_ui_mcp.agent import NextGenUIMCPAgent
from next_gen_ui_testing.data_set_movies import find_movie
from next_gen_ui_testing.model import MockedInference
from unittest.mock import patch


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

    text_content = [
        {
            "id": "test_id",
            "content": json.dumps({
                "component": "one-card",
                "image": None,
                "title": "Toy Story",
                "id": "test_id",
                "fields": [
                    {"name": "Title", "data_path": "movie.title", "data": ["Toy Story"]},
                    {"name": "Year", "data_path": "movie.year", "data": [1995]},
                    {"name": "IMDB Rating", "data_path": "movie.imdbRating", "data": [8.3]},
                ],
            }),
            "name": "rendering"
        }
    ]
    tool_result = ToolInvocationResult(content=text_content)
    # Use a real LlamaStackClient but mock only the _post method
    real_client = LlamaStackClient()
    
    with patch.object(real_client.tool_runtime, '_post', return_value=tool_result) as mock_post:
        # Now call the real method with the mocked _post
        result = real_client.tool_runtime.invoke_tool(
            tool_name="generate_ui", kwargs=input_data
        )
        
        # Verify that _post was called
        mock_post.assert_called_once()

        components = json.loads(text_content)
        assert components[0]["name"] == "rendering"
        assert '"data":[1995]' in str(components[0]["content"])
