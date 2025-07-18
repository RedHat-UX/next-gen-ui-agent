import json
import logging
from typing import Any, Dict, List

from fastmcp import FastMCP
from fastmcp.server.server import Transport
from next_gen_ui_agent.agent import NextGenUIAgent
from next_gen_ui_agent.model import InferenceBase
from next_gen_ui_agent.types import AgentConfig, AgentInput, InputData

logger = logging.getLogger(__name__)


class NextGenUIMCPAgent:
    """Next Gen UI Agent as MCP server."""

    def __init__(
        self,
        inference: InferenceBase,
        component_system: str,
        name: str = "NextGenUIMCPAgent",
    ):
        self.ngui_agent = NextGenUIAgent(AgentConfig(inference=inference))
        self.component_system = component_system
        self.mcp = FastMCP(name)
        self._setup_mcp_tools()

    def _setup_mcp_tools(self):
        """Set up MCP tools for the agent."""

        @self.mcp.tool
        async def generate_ui(
            user_prompt: str, input_data: List[Dict[str, Any]]
        ) -> List[Dict[str, Any]]:
            """Generate UI components from user prompt and input data.

            This is the main tool that wraps the entire Next Gen UI Agent functionality:
            - Component selection based on user prompt and data
            - Data transformation to match selected components
            - Design system rendering to produce final UI

            Args:
                user_prompt: User's request or prompt describing what UI to generate
                input_data: List of input data items with 'id' and 'data' keys

            Returns:
                List of rendered UI components ready for display
            """
            try:
                # Convert to InputData format
                formatted_input_data: List[InputData] = [
                    {"id": item["id"], "data": item["data"]} for item in input_data
                ]

                # Create agent input
                agent_input = AgentInput(
                    user_prompt=user_prompt, input_data=formatted_input_data
                )

                # Run the complete agent pipeline
                # 1. Component selection
                components = await self.ngui_agent.component_selection(
                    input=agent_input
                )

                # 2. Data transformation
                components_data = self.ngui_agent.data_transformation(
                    input_data=formatted_input_data, components=components
                )

                # 3. Design system rendering
                renditions = self.ngui_agent.design_system_handler(
                    components=components_data, component_system=self.component_system
                )

                # Format output as artifacts
                return [
                    {
                        "id": rendition.id,
                        "content": rendition.content,
                        "name": "rendering",
                    }
                    for rendition in renditions
                ]

            except Exception as e:
                logger.exception("Error during UI generation")
                return [{"error": str(e), "name": "error"}]

        @self.mcp.resource("system://info")
        def get_system_info() -> str:
            """Get system information about the Next Gen UI Agent."""
            return json.dumps(
                {
                    "agent_name": "NextGenUIMCPAgent",
                    "component_system": self.component_system,
                    "description": "Next Gen UI Agent exposed via MCP protocol",
                    "capabilities": [
                        "UI component selection",
                        "Data transformation",
                        "Design system rendering",
                    ],
                }
            )

        @self.mcp.prompt()
        def ui_generation_prompt(user_request: str) -> str:
            """Generate a prompt for UI component creation.

            Args:
                user_request: The user's request for UI components

            Returns:
                Formatted prompt for UI generation
            """
            return f"""
            Generate appropriate UI components for the following request:
            
            User Request: {user_request}
            
            Please provide input data in the following format:
            - id: unique identifier for the data item
            - data: the actual data content (JSON string)
            
            The system will automatically select and render the most appropriate UI components.
            """

    def run(self, transport: Transport = "stdio", **kwargs):
        """Run the MCP server.

        Args:
            transport: Transport type ('stdio', 'http', 'sse')
            **kwargs: Additional arguments for the transport
        """
        self.mcp.run(transport=transport, **kwargs)

    def get_mcp_server(self) -> FastMCP:
        """Get the underlying FastMCP server instance."""
        return self.mcp
