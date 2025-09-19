import json
import logging
from typing import Any, Dict, List, Literal

from mcp import types
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession
from next_gen_ui_agent.agent import NextGenUIAgent
from next_gen_ui_agent.model import InferenceBase
from next_gen_ui_agent.types import AgentConfig, AgentInput, InputData

logger = logging.getLogger(__name__)


class MCPSamplingInference(InferenceBase):
    """Inference implementation that uses MCP sampling for LLM calls."""

    def __init__(self, ctx: Context[ServerSession, None], max_tokens: int = 2048):
        self.ctx = ctx
        self.max_tokens = max_tokens

    async def call_model(self, system_msg: str, prompt: str) -> str:
        """Call the LLM model using MCP sampling.

        Args:
            system_msg: System message for the LLM
            prompt: User prompt for the LLM

        Returns:
            The LLM response as a string
        """
        try:
            # Create sampling message for the LLM call
            user_message = types.SamplingMessage(
                role="user", content=types.TextContent(type="text", text=prompt)
            )

            # Use the MCP session to make a sampling request
            result = await self.ctx.session.create_message(
                messages=[user_message],
                system_prompt=system_msg,
                temperature=0.0,  # Deterministic responses as required
                max_tokens=self.max_tokens,  # Use configurable max_tokens parameter
            )

            # Extract the text content from the response
            if isinstance(result.content, types.TextContent):
                return result.content.text
            elif isinstance(result.content, str):
                return result.content
            else:
                # Handle list of content items
                content_text = ""
                for item in result.content:
                    if isinstance(item, types.TextContent):
                        content_text += item.text
                    elif hasattr(item, "text"):
                        content_text += item.text
                return content_text

        except Exception as e:
            logger.exception("MCP sampling failed")
            raise RuntimeError(f"Failed to call model via MCP sampling: {e}") from e


class NextGenUIMCPAgent:
    """Next Gen UI Agent as MCP server that can use sampling or external inference."""

    def __init__(
        self,
        config: AgentConfig = AgentConfig(component_system="json"),
        name: str = "NextGenUIMCPAgent",
        sampling_max_tokens: int = 2048,
    ):
        self.config = config
        self.sampling_max_tokens = sampling_max_tokens
        self.mcp: FastMCP = FastMCP(name)
        self._setup_mcp_tools()

    def _setup_mcp_tools(self):
        """Set up MCP tools for the agent."""

        @self.mcp.tool()
        async def generate_ui(
            user_prompt: str,
            input_data: List[InputData],
            ctx: Context[ServerSession, None],
        ) -> List[Dict[str, Any]]:
            """Generate UI components from user prompt and input data.

            This tool can use either external inference providers or MCP sampling capabilities.
            When external inference is provided, it uses that directly. Otherwise, it creates
            an InferenceBase using MCP sampling to leverage the client's LLM.

            Args:
                user_prompt: User's request or prompt describing what UI to generate
                input_data: List of input data items with 'id' and 'data' keys
                ctx: MCP context providing access to sampling capabilities

            Returns:
                List of rendered UI components ready for display
            """

            try:
                # Create a copy of the config to avoid modifying the original config but preserve type
                config_copy = AgentConfig(**self.config)

                # Choose inference provider based on configuration
                if config_copy.get("inference") is None:
                    # Create sampling-based inference using the MCP context
                    inference = MCPSamplingInference(
                        ctx, max_tokens=self.sampling_max_tokens
                    )
                    config_copy["inference"] = inference
                    await ctx.info("Using MCP sampling to leverage client's LLM...")
                else:
                    # Using external inference provider
                    await ctx.info("Using external inference provider...")

                # Instantiate NextGenUIAgent with the chosen inference
                ngui_agent = NextGenUIAgent(config=config_copy)

                await ctx.info("Starting UI generation...")

                # Create agent input
                agent_input = AgentInput(user_prompt=user_prompt, input_data=input_data)

                # Run the complete agent pipeline using the configured inference
                # 1. Component selection
                await ctx.info("Performing component selection...")
                components = await ngui_agent.component_selection(input=agent_input)

                # 2. Data transformation
                await ctx.info("Transforming data to match components...")
                components_data = ngui_agent.data_transformation(
                    input_data=input_data, components=components
                )

                # 3. Design system rendering
                await ctx.info("Rendering final UI components...")
                renditions = ngui_agent.design_system_handler(
                    components=components_data,
                    component_system=self.config.get("component_system"),
                )

                await ctx.info(
                    f"Successfully generated {len(renditions)} UI components"
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
                await ctx.error(f"UI generation failed: {e}")
                return [{"error": str(e), "name": "error"}]

        @self.mcp.resource("system://info")
        def get_system_info() -> str:
            """Get system information about the Next Gen UI Agent."""
            return json.dumps(
                {
                    "agent_name": "NextGenUIMCPAgent",
                    "component_system": self.config.get("component_system"),
                    "description": "Next Gen UI Agent exposed via MCP protocol",
                    "capabilities": [
                        "UI component generation based of user prompt and input data"
                    ],
                }
            )

    def run(
        self,
        transport: Literal["stdio", "sse", "streamable-http"] = "stdio",
        host: str = "127.0.0.1",
        port: int = 8000,
        mount_path: str | None = None,
    ):
        """Run the MCP server.

        Args:
            transport: Transport type ('stdio', 'sse', 'streamable-http')
            host: Host to bind to (for sse and streamable-http transports)
            port: Port to bind to (for sse and streamable-http transports)
            mount_path: Mount path for SSE transport
        """
        # Configure host and port in FastMCP settings for non-stdio transports
        if transport in ["sse", "streamable-http"]:
            self.mcp.settings.host = host
            self.mcp.settings.port = port

        # Run with appropriate parameters based on transport
        if transport == "sse":
            self.mcp.run(transport=transport, mount_path=mount_path)
        else:
            self.mcp.run(transport=transport)

    def get_mcp_server(self) -> FastMCP:
        """Get the underlying FastMCP server instance."""
        return self.mcp
