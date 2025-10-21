import logging
import uuid
from typing import Annotated, List, Literal

from fastmcp import Context, FastMCP
from fastmcp.tools.tool import ToolResult
from mcp import types
from mcp.types import TextContent
from next_gen_ui_agent.agent import NextGenUIAgent
from next_gen_ui_agent.data_transform.types import ComponentDataBaseWithTitle
from next_gen_ui_agent.model import InferenceBase
from next_gen_ui_agent.types import AgentConfig, AgentInput, InputData, UIBlock
from next_gen_ui_mcp.types import MCPGenerateUIOutput
from pydantic import Field

logger = logging.getLogger(__name__)


class MCPSamplingInference(InferenceBase):
    """Inference implementation that uses MCP sampling for LLM calls."""

    def __init__(self, ctx: Context, max_tokens: int = 2048):
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
            else:
                raise Exception(
                    "Sample Response returned unknown type: " + result.content.type
                )

        except Exception as e:
            logger.exception("MCP sampling failed")
            raise RuntimeError(f"Failed to call model via MCP sampling: {e}") from e


MCP_ALL_TOOLS = [
    "generate_ui",
    "generate_ui_structured_data",
]


class NextGenUIMCPServer:
    """Next Gen UI Agent as MCP server that can use sampling or external inference."""

    def __init__(
        self,
        config: AgentConfig = AgentConfig(component_system="json"),
        name: str = "NextGenUIMCPServer",
        sampling_max_tokens: int = 2048,
        inference: InferenceBase | None = None,
        debug: bool = False,
        enabled_tools=None,
        structured_output_enabled=True,
    ):
        self.debug = debug
        self.config = config
        self.sampling_max_tokens = sampling_max_tokens
        self.structured_output_enabled = structured_output_enabled
        self.mcp: FastMCP = FastMCP(name)
        if enabled_tools:
            for t in enabled_tools:
                if t not in MCP_ALL_TOOLS:
                    raise ValueError(
                        f"tool '{t}' is no valid. Available tools are: {MCP_ALL_TOOLS}"
                    )
            self.enabled_tools = enabled_tools
        else:
            self.enabled_tools = MCP_ALL_TOOLS
        self._setup_mcp_tools()
        self.inference = inference

    generate_ui_description = (
        "Generate UI components from user prompt and input data. "
        "It's adviced to run the tool as last tool call in the chain, to be able process all data from previous tools calls."
    )

    def _setup_mcp_tools(self) -> None:
        """Set up MCP tools for the agent."""
        logger.info("Registering generate_ui tool with data* arguments")

        @self.mcp.tool(
            name="generate_ui",
            description=self.generate_ui_description,
            exclude_args=["structured_data"],
            enabled="generate_ui" in self.enabled_tools,
        )
        async def generate_ui(
            ctx: Context,
            # Be sync with types.MCPGenerateUIInput !!!
            user_prompt: Annotated[
                str,
                Field(
                    description="Original user query without any changes. Do not generate this."
                ),
            ],
            data: Annotated[
                str,
                Field(
                    description="Input raw data. COPY of data from another tool call. Do not change anything!. NEVER generate this."
                ),
            ],
            data_type: Annotated[
                str,
                Field(
                    description="Name of tool call used for 'data' argument. COPY of tool name. Do not change anything! NEVER generate this."
                ),
            ],
            data_id: Annotated[
                str | None,
                Field(
                    description="ID of tool call used for 'data' argument. Exact COPY of tool name. Do not change anything! NEVER generate this."
                ),
            ] = None,
            # In case that agent pass data overrides data programatically
            structured_data: Annotated[
                List[InputData] | None,
                Field(
                    description="Structured Input Data. Array of objects with 'id' and 'data' keys. NEVER generate this."
                ),
            ] = None,
        ) -> ToolResult:
            if structured_data and len(structured_data) > 0:
                return await self.generate_ui_structured_data(
                    ctx=ctx, user_prompt=user_prompt, structured_data=structured_data
                )
            elif data and data_type:
                if not data_id:
                    data_id = str(uuid.uuid4())
                structured_data = [InputData(data=data, type=data_type, id=data_id)]
                return await self.generate_ui_structured_data(
                    ctx=ctx, user_prompt=user_prompt, structured_data=structured_data
                )
            else:
                raise ValueError(
                    "No data or data_type arguments provided. No UI component generated."
                )

        @self.mcp.tool(
            name="generate_ui_structured_data",
            description=self.generate_ui_description,
            enabled="generate_ui_structured_data" in self.enabled_tools,
        )
        async def generate_ui_structured_data(
            ctx: Context,
            # Be sync with types.MCPGenerateUIInput !!!
            user_prompt: Annotated[
                str,
                Field(
                    description="Original user query without any changes. Do not generate this."
                ),
            ],
            structured_data: Annotated[
                List[InputData] | None,
                Field(
                    description="Structured Input Data. Array of objects with 'id' and 'data' keys. NEVER generate this."
                ),
            ],
        ) -> ToolResult:
            if not structured_data or len(structured_data) == 0:
                # TODO: Do analysis of input_data and check if data field contains data or not
                raise ValueError("No data provided. No UI component generated.")
            return await self.generate_ui_structured_data(
                ctx=ctx, user_prompt=user_prompt, structured_data=structured_data
            )

        @self.mcp.resource(
            "system://info",
            mime_type="application/json",
        )
        def get_system_info() -> dict:
            """Get system information about the Next Gen UI Agent."""
            return {
                "agent_name": "NextGenUIMCPServer",
                "component_system": self.config.component_system,
                "description": "Next Gen UI Agent exposed via MCP protocol",
                "capabilities": [
                    "UI component generation based of user prompt and input data"
                ],
            }

    async def generate_ui_structured_data(
        self,
        ctx: Context,
        user_prompt: str,
        structured_data: List[InputData],
    ) -> ToolResult:
        """Generate UI components from user prompt and input data.

        This tool can use either external inference providers or MCP sampling capabilities.
        When external inference is provided, it uses that directly. Otherwise, it creates
        an InferenceBase using MCP sampling to leverage the client's LLM.

        Args:
            user_prompt: User's request or prompt describing what UI to generate
            structured_data: List of input data items with 'id' and 'data' keys
            ctx: MCP context providing access to sampling capabilities

        Returns:
            List of rendered UI components ready for display
        """

        if not structured_data or len(structured_data) == 0:
            # TODO: Do analysis of input_data and check if data field contains data or not
            raise ValueError("No data provided. No UI component generated.")

        try:
            inference = self.inference

            # Choose inference provider based on configuration
            if not inference:
                # Create sampling-based inference using the MCP context
                inference = MCPSamplingInference(
                    ctx, max_tokens=self.sampling_max_tokens
                )
                await ctx.info("Using MCP sampling to leverage client's LLM...")
            else:
                # Using external inference provider
                await ctx.info("Using external inference provider...")

            # Instantiate NextGenUIAgent with the chosen inference
            ngui_agent = NextGenUIAgent(config=self.config, inference=inference)

            await ctx.info("Starting UI generation...")

            # Create agent input
            agent_input = AgentInput(
                user_prompt=user_prompt, input_data=structured_data
            )

            # Run the complete agent pipeline using the configured inference
            # 1. Component selection
            await ctx.info("Performing component selection...")
            components = await ngui_agent.component_selection(input=agent_input)

            # 2. Data transformation
            await ctx.info("Transforming data to match components...")
            components_data = ngui_agent.data_transformation(
                input_data=structured_data, components=components
            )

            # 3. Design system rendering
            await ctx.info("Rendering final UI components...")
            renderings = ngui_agent.design_system_handler(
                components=components_data,
                component_system=self.config.component_system,
            )

            await ctx.info(f"Successfully generated {len(renderings)} UI components")

            # Format output as artifacts
            human_output = [
                "Components are rendered in UI.",
                f"Count: {len(components_data)}",
            ]
            for index, c in enumerate(components_data):
                c_info = f"{index + 1}."
                if isinstance(c, ComponentDataBaseWithTitle):
                    c_info += f" Title: '{c.title}'"
                human_output.append(f"{c_info} type: {c.component}")

            human_output_str = "\n".join(human_output)

            blocks: list[UIBlock] = []
            for r in renderings:
                blocks.append(UIBlock(id=r.id, rendering=r))

            output = MCPGenerateUIOutput(blocks=blocks, summary=human_output_str)

            if self.structured_output_enabled:
                return ToolResult(
                    content=[TextContent(text=human_output_str, type="text")],
                    structured_content=output.model_dump(
                        exclude_unset=True, exclude_defaults=True
                    ),
                )
            else:
                return ToolResult(
                    content=[TextContent(text=output.model_dump_json(), type="text")]
                )

        except Exception as e:
            logger.exception("Error during UI generation")
            await ctx.error(f"UI generation failed: {e}")
            raise e

    def run(
        self,
        transport: Literal["stdio", "sse", "streamable-http"] = "stdio",
        host: str = "127.0.0.1",
        port: int = 8000,
    ):
        """Run the MCP server.

        Args:
            transport: Transport type ('stdio', 'sse', 'streamable-http')
            host: Host to bind to (for sse and streamable-http transports)
            port: Port to bind to (for sse and streamable-http transports)
        """
        # Configure host and port in FastMCP settings for non-stdio transports
        if transport in ["sse", "streamable-http"]:
            self.mcp.run(
                transport=transport,
                host=host,
                port=port,
            )
        else:
            self.mcp.run(transport=transport)

    def get_mcp_server(self) -> FastMCP:
        """Get the underlying FastMCP server instance."""
        return self.mcp
