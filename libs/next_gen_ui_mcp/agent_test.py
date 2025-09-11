import json
import logging
from typing import List

import pytest
from mcp.server.lowlevel.helper_types import ReadResourceContents
from mcp.types import TextContent
from next_gen_ui_agent.types import InputData, UIComponentMetadata
from next_gen_ui_mcp.agent import NextGenUIMCPAgent
from next_gen_ui_testing.data_set_movies import find_movie
from next_gen_ui_testing.model import MockedInference

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_mcp_agent_tool_directly() -> None:
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
        component_system="json", inference=mocked_inference, name="TestAgent"
    )

    # Get the FastMCP server
    mcp_server = ngui_agent.get_mcp_server()

    # Create test input data
    movies_data = find_movie("Toy Story")
    input_data: List[InputData] = [
        {"id": "test_id", "data": json.dumps(movies_data, default=str)}
    ]

    # Test the generate_ui tool directly
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

    # FastMCP call_tool returns a tuple, get the first element
    tool_result = result[0] if isinstance(result, tuple) else result
    assert tool_result is not None
    assert len(tool_result) > 0
    assert isinstance(tool_result[0], TextContent)
    text_content = tool_result[0].text
    assert text_content is not None

    components = json.loads(text_content)
    assert len(components) > 0
    assert components["name"] == "rendering"
    assert '"data":[1995]' in str(components["content"])
    logger.info("Result: %s", text_content)


@pytest.mark.asyncio
async def test_mcp_agent_system_info_resource() -> None:
    """Test the MCP agent's system info resource."""
    # Create agent with mocked inference
    mocked_component: UIComponentMetadata = UIComponentMetadata.model_validate(
        {
            "title": "Test",
            "reasonForTheComponentSelection": "Test",
            "confidenceScore": "100%",
            "component": "one-card",
            "fields": [],
            "id": "test-id",
        }
    )

    mocked_inference = MockedInference(mocked_component)
    ngui_agent = NextGenUIMCPAgent(
        component_system="rhds", inference=mocked_inference, name="TestAgent"
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
