import json
import logging
from typing import List
from unittest.mock import AsyncMock, MagicMock

import pytest
from mcp import types
from mcp.server.fastmcp import Context
from mcp.server.lowlevel.helper_types import ReadResourceContents
from mcp.server.session import ServerSession
from mcp.types import TextContent
from next_gen_ui_agent.types import InputData, UIComponentMetadata
from next_gen_ui_mcp.agent import NextGenUIMCPAgent
from next_gen_ui_testing.data_set_movies import find_movie

logger = logging.getLogger(__name__)


class MockMCPContext:
    """Mock MCP Context for testing that simulates sampling responses."""
    
    def __init__(self, mocked_response: UIComponentMetadata):
        self.mocked_response = mocked_response
        self.session = AsyncMock(spec=ServerSession)
        # Mock the create_message method to return our mocked response
        self.session.create_message.return_value = MagicMock(
            content=types.TextContent(
                type="text", 
                text=mocked_response.model_dump_json()
            )
        )
    
    async def info(self, message: str):
        """Mock info logging."""
        logger.info(f"Mock context info: {message}")
    
    async def error(self, message: str):
        """Mock error logging."""
        logger.error(f"Mock context error: {message}")


from next_gen_ui_mcp.agent import MCPSamplingInference


@pytest.mark.asyncio
async def test_mcp_agent_functionality() -> None:
    """Test the MCP agent's generate_ui tool functionality with mocked sampling."""
    from unittest.mock import patch
    
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

    # Create agent
    ngui_agent = NextGenUIMCPAgent(
        component_system="json", name="TestAgent"
    )

    # Get the FastMCP server
    mcp_server = ngui_agent.get_mcp_server()

    # Create test input data
    movies_data = find_movie("Toy Story")
    input_data: List[InputData] = [
        {"id": "test_id", "data": json.dumps(movies_data, default=str)}
    ]

    # Mock the MCPSamplingInference to return our mocked component
    def mock_mcp_sampling_inference(ctx):
        mock_inference = AsyncMock()
        mock_inference.call_model.return_value = mocked_component.model_dump_json()
        return mock_inference

    # Patch the MCPSamplingInference class and context methods
    with patch('next_gen_ui_mcp.agent.MCPSamplingInference', side_effect=mock_mcp_sampling_inference):
        # Mock the context methods to avoid the "context not available" error during testing
        with patch.object(Context, 'info', new_callable=AsyncMock) as mock_info:
            with patch.object(Context, 'error', new_callable=AsyncMock) as mock_error:
                # Test the generate_ui tool through the MCP server
                result = await mcp_server.call_tool(
                    "generate_ui",
                    {
                        "user_prompt": "Tell me brief details of Toy Story",
                        "input_data": input_data,
                    },
                )

    # Verify the result
    assert result is not None
    assert len(result) > 0

    # FastMCP call_tool returns a list containing another list with TextContent objects
    # Based on the error output, result[0] is a list containing TextContent objects
    inner_result = result[0]
    assert isinstance(inner_result, list)
    assert len(inner_result) > 0
    assert isinstance(inner_result[0], TextContent)
    
    text_content = inner_result[0].text
    assert text_content is not None

    # Parse the JSON response which should be a single UI component
    component = json.loads(text_content)
    assert isinstance(component, dict)
    
    # Verify the component structure
    assert "id" in component
    assert "content" in component
    assert "name" in component
    assert component["name"] == "rendering"
    assert component["id"] == "test_id"
    
    # Parse the inner content to verify the UI component structure
    inner_content = json.loads(component["content"])
    assert inner_content["component"] == "one-card"
    assert inner_content["title"] == "Toy Story"
    assert len(inner_content["fields"]) == 3
    
    # Verify some field data
    title_field = next(f for f in inner_content["fields"] if f["name"] == "Title")
    assert title_field["data"] == ["Toy Story"]
    
    year_field = next(f for f in inner_content["fields"] if f["name"] == "Year")
    assert year_field["data"] == [1995]
    
    logger.info("MCP generate_ui tool test passed: %s", text_content)


@pytest.mark.asyncio
async def test_mcp_agent_system_info_resource() -> None:
    """Test the MCP agent's system info resource."""
    # Create agent (no inference parameter needed with new MCP sampling approach)
    ngui_agent = NextGenUIMCPAgent(
        component_system="rhds", name="TestAgent"
    )

    # Get the FastMCP server
    mcp_server = ngui_agent.get_mcp_server()

    # Test the system info resource directly
    result = await mcp_server.read_resource("system://info")

    # Verify the result
    assert result is not None
    assert len(result) > 0
    assert isinstance(result[0], ReadResourceContents)
    text_content = result[0].content
    assert text_content is not None
    system_info = json.loads(text_content)
    assert system_info["agent_name"] == "NextGenUIMCPAgent"
    assert system_info["component_system"] == "rhds"
    assert "capabilities" in system_info
