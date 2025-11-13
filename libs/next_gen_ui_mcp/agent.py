import asyncio
import logging
import uuid
from typing import Annotated, List, Literal

from fastmcp import Context, FastMCP
from fastmcp.tools.tool import ToolResult
from mcp import types
from mcp.types import TextContent
from next_gen_ui_agent.agent import NextGenUIAgent
from next_gen_ui_agent.model import InferenceBase
from next_gen_ui_agent.types import (
    AgentConfig,
    InputData,
    UIBlock,
    UIBlockConfiguration,
)
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
    "generate_ui_component",
    "generate_ui_multiple_components",
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
        self.ngui_agent = NextGenUIAgent(config=self.config)

    def _setup_mcp_tools(self) -> None:
        """Set up MCP tools for the agent."""
        logger.info("Registering tools")

        @self.mcp.tool(
            name="generate_ui_component",
            description=(
                "Generate one UI component for given user_prompt and data. "
                "Always get fresh data from another tool first. "
                "It's adviced to run the tool as last tool call in the chain, to be able process all data from previous tools calls."
            ),
            enabled="generate_ui_component" in self.enabled_tools,
        )
        async def generate_ui_component(
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
        ) -> ToolResult:
            if not data_id:
                data_id = str(uuid.uuid4())

            await ctx.info("Starting UI generation...")
            try:
                input_data = InputData(data=data, type=data_type, id=data_id)
                inference = await self.get_ngui_inference(ctx)
                ui_block = await self.generate_ui_block(
                    ctx=ctx,
                    user_prompt=user_prompt,
                    input_data=input_data,
                    inference=inference,
                )
                summary = f"Component is rendered in UI. {self.component_info(ui_block.configuration)}"
                return self.create_mcp_output(blocks=[ui_block], summary=summary)
            except Exception as e:
                logger.exception("Error during UI generation")
                await ctx.error(f"UI generation failed: {e}")
                raise e

        @self.mcp.tool(
            name="generate_ui_multiple_components",
            description=(
                "Generate multiple UI components for given user_prompt. "
                "Always get fresh data from another tool first. "
                "It's adviced to run the tool as last tool call in the chain, to be able process all data from previous tools calls."
            ),
            enabled="generate_ui_multiple_components" in self.enabled_tools,
            # exclude_args=["structured_data"],
        )
        async def generate_ui_multiple_components(
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
                    description="Structured Input Data. Array of objects with 'id', 'data' and 'type' keys. NEVER generate this."
                ),
            ] = None,
        ) -> ToolResult:
            if not structured_data or len(structured_data) == 0:
                # TODO: Do analysis of input_data and check if data field contains data or not
                raise ValueError(
                    "No data provided! Get data from another tool again and then call this tool again."
                )

            inference = await self.get_ngui_inference(ctx)

            await ctx.info("Starting UI generation...")

            tasks = [
                asyncio.create_task(
                    self.generate_ui_block(
                        ctx=ctx,
                        user_prompt=user_prompt,
                        input_data=input_data,
                        inference=inference,
                    )
                )
                for input_data in structured_data
            ]
            success_output = ["\nSuccessful generated components:"]
            failed_output = ["\nFailed component generation:"]
            blocks = []
            for completed_task in asyncio.as_completed(tasks):
                try:
                    # TODO: Consider using Progress to inform client about the progress and send result of individual component processing
                    # https://modelcontextprotocol.io/specification/2025-03-26/basic/utilities/progress

                    ui_block: UIBlock = await completed_task

                    blocks.append(ui_block)
                    success_output.append(
                        f"{len(success_output)}. {self.component_info(ui_block.configuration)}"
                    )
                except Exception as e:
                    logger.exception("Error processing component")
                    failed_output.append(
                        f"{len(failed_output)}. UI generation failed for this component. {e}"
                    )

            await ctx.info(
                f"Successfully generated {len(success_output)} UI components. Failed: {len(failed_output)} "
            )
            summary = "UI components generation summary:"
            if len(success_output) > 1:
                summary += "\n".join(success_output)
            if len(failed_output) > 1:
                summary += "\n".join(failed_output)
            return self.create_mcp_output(blocks=blocks, summary=summary)

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

    async def get_ngui_inference(self, ctx: Context) -> InferenceBase:
        # Choose inference provider based on configuration
        if not self.inference:
            # Create sampling-based inference using the MCP context
            inference = MCPSamplingInference(ctx, max_tokens=self.sampling_max_tokens)
            await ctx.info("Using MCP sampling to leverage client's LLM...")
            return inference
        else:
            # Using external inference provider
            await ctx.info("Using external inference provider...")
            return self.inference

    async def generate_ui_block(
        self,
        ctx: Context,
        user_prompt: str,
        input_data: InputData,
        inference: InferenceBase,
    ) -> UIBlock:
        await ctx.info("Starting UI generation...")

        # Run the complete agent pipeline using the configured inference
        # 1. Component selection
        await ctx.info("Performing component selection...")
        component_metadata = await self.ngui_agent.select_component(
            user_prompt=user_prompt, input_data=input_data, inference=inference
        )

        # 2. Data transformation
        await ctx.info("Transforming data to match components...")
        components_data = self.ngui_agent.transform_data(
            input_data=input_data, component=component_metadata
        )

        # 3. Design system rendering
        await ctx.info("Rendering final UI components...")
        rendering = self.ngui_agent.generate_rendering(
            component=components_data,
            component_system=self.config.component_system,
        )
        await ctx.info("Successfully generated UI component")

        block_config = self.ngui_agent.construct_UIBlockConfiguration(
            input_data=input_data,
            component_metadata=component_metadata,
        )
        ui_block = UIBlock(
            id=rendering.id, rendering=rendering, configuration=block_config
        )
        return ui_block

    def component_info(self, uiblock_config: UIBlockConfiguration | None) -> str:
        if not uiblock_config:
            return ""
        c_info = []
        if uiblock_config.data_type:
            c_info.append(f"data_type: '{uiblock_config.data_type}'")
        if uiblock_config.component_metadata:
            c_info.append(f"title: '{uiblock_config.component_metadata.title}'")
            c_info.append(
                f"component_type: {uiblock_config.component_metadata.component}"
            )
        return ", ".join(c_info)

    def create_mcp_output(
        self,
        blocks: list[UIBlock],
        summary: str,
    ) -> ToolResult:
        output = MCPGenerateUIOutput(blocks=blocks, summary=summary)

        if self.structured_output_enabled:
            return ToolResult(
                content=[TextContent(text=summary, type="text")],
                structured_content=output.model_dump(
                    exclude_unset=True, exclude_defaults=True, exclude_none=True
                ),
            )
        else:
            return ToolResult(
                content=[
                    TextContent(
                        text=output.model_dump_json(
                            exclude_unset=True,
                            exclude_defaults=True,
                            exclude_none=True,
                        ),
                        type="text",
                    )
                ]
            )

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
