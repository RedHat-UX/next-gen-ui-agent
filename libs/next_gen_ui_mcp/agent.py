import asyncio
import logging
import uuid
from typing import Annotated, Any, List, Literal, Optional

from fastmcp import Context, FastMCP
from fastmcp.tools.tool import ToolResult
from mcp import types
from mcp.types import ModelPreferences, TextContent
from next_gen_ui_agent.agent import NextGenUIAgent
from next_gen_ui_agent.inference.inference_base import InferenceBase
from next_gen_ui_agent.types import InputData, UIBlock
from next_gen_ui_mcp.agent_config import MCPAgentConfig, MCPAgentToolConfig
from next_gen_ui_mcp.types import MCPGenerateUIOutput
from pydantic import Field

logger = logging.getLogger(__name__)


class MCPSamplingInference(InferenceBase):
    """Inference implementation that uses MCP sampling for LLM calls."""

    def __init__(
        self,
        ctx: Context,
        max_tokens: int = 2048,
        model_hints: list[str] | None = None,
        cost_priority: float | None = None,
        speed_priority: float | None = None,
        intelligence_priority: float | None = None,
    ):
        self.ctx = ctx
        self.max_tokens = max_tokens
        self.model_hints = model_hints
        self.cost_priority = cost_priority
        self.speed_priority = speed_priority
        self.intelligence_priority = intelligence_priority

    def _get_client_identification(self) -> str:
        """Extract client identification information from the MCP context.

        Returns:
            A string identifying the client, formatted as "name vversion" or "Unknown Client"
        """
        try:
            # Access client_params from session which contains client info
            client_params = self.ctx.session.client_params

            if client_params and hasattr(client_params, "clientInfo"):
                client_info = client_params.clientInfo
                if client_info:
                    name = client_info.name
                    version = getattr(client_info, "version", None)
                    if version:
                        return f"{name} v{version}"
                    return name

            # Fallback to unknown
            return "Unknown Client"

        except Exception as e:
            logger.debug("Could not extract client identification: %s", e)
            return "Unknown Client"

    def _check_sampling_capability(self) -> bool:
        """Check if the MCP client supports sampling capability.

        Returns:
            True if sampling is supported or cannot be determined, False if explicitly not supported
        """
        try:

            return (
                self.ctx.session.client_params is not None
                and self.ctx.session.client_params.capabilities.sampling is not None
            )

        except Exception as e:
            logger.debug("Sampling capability information not available: %s", e)
            return False

    async def call_model(self, system_msg: str, prompt: str) -> str:
        """Call the LLM model using MCP sampling.

        Args:
            system_msg: System message for the LLM
            prompt: User prompt for the LLM

        Returns:
            The LLM response as a string
        """
        # Check if the MCP client supports sampling capability before attempting to use it
        if not self._check_sampling_capability():
            client_id = self._get_client_identification()
            request_id = self.ctx.request_id or "unknown"

            # Log warning with client identification
            logger.warning(
                "MCP Sampling Not Available - Client: %s (Request: %s) does not support 'sampling' capability",
                client_id,
                request_id,
            )

            # Raise descriptive error
            raise RuntimeError(
                f"MCP sampling is not available. The calling MCP client '{client_id}' does not support "
                f"the 'sampling' capability required for using the client's LLM to generate UI components.\n\n"
                f"Please either:\n"
                f"1. Use an MCP client that supports sampling (e.g., Claude Desktop, Cline, etc.)\n"
                f"2. Configure UI Agent to use an external inference provider (`--provider openai` or `--provider anthropic`)"
            )

        try:
            # Create sampling message for the LLM call
            user_message = types.SamplingMessage(
                role="user", content=types.TextContent(type="text", text=prompt)
            )

            # Build model preferences if any are provided
            model_preferences: ModelPreferences | None = None
            if (
                self.model_hints
                or self.cost_priority is not None
                or self.speed_priority is not None
                or self.intelligence_priority is not None
            ):
                # Build model preferences dict according to MCP spec
                prefs_dict: dict[str, Any] = {}
                if self.model_hints:
                    prefs_dict["hints"] = [{"name": hint} for hint in self.model_hints]
                if self.cost_priority is not None:
                    prefs_dict["costPriority"] = self.cost_priority
                if self.speed_priority is not None:
                    prefs_dict["speedPriority"] = self.speed_priority
                if self.intelligence_priority is not None:
                    prefs_dict["intelligencePriority"] = self.intelligence_priority
                # Construct ModelPreferences from dict
                model_preferences = ModelPreferences(**prefs_dict)

            # Use the MCP session to make a sampling request
            result = await self.ctx.session.create_message(
                messages=[user_message],
                system_prompt=system_msg,
                temperature=0.0,  # Deterministic responses as required
                max_tokens=self.max_tokens,  # Use configurable max_tokens parameter
                model_preferences=model_preferences,
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
        config: MCPAgentConfig = MCPAgentConfig(component_system="json"),
        name: str = "NextGenUIMCPServer",
        sampling_max_tokens: int = 2048,
        sampling_model_hints: list[str] | None = None,
        sampling_cost_priority: float | None = None,
        sampling_speed_priority: float | None = None,
        sampling_intelligence_priority: float | None = None,
        inference: InferenceBase | None = None,
        debug: bool = False,
        enabled_tools=None,
        structured_output_enabled=True,
    ):
        self.debug = debug
        self.config = config
        self.sampling_max_tokens = sampling_max_tokens
        self.sampling_model_hints = sampling_model_hints
        self.sampling_cost_priority = sampling_cost_priority
        self.sampling_speed_priority = sampling_speed_priority
        self.sampling_intelligence_priority = sampling_intelligence_priority
        self.structured_output_enabled = structured_output_enabled
        self.mcp: FastMCP = FastMCP(
            name,
            strict_input_validation=True,
            mask_error_details=False,
        )
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

    def _get_argument_description(
        self,
        tool_config: Optional[MCPAgentToolConfig],
        argument_name: str,
        default: str,
    ) -> str:
        """Get argument description, using override from config if available.

        Args:
            tool_config: The tool config object (e.g., self.config.mcp.tools.generate_ui_component)
            argument_name: Name of the argument
            default: Default description to use if no override is found

        Returns:
            The argument description (override if available, otherwise default)
        """
        if (
            tool_config
            and tool_config.argument_descriptions
            and argument_name in tool_config.argument_descriptions
            and tool_config.argument_descriptions[argument_name]
            and tool_config.argument_descriptions[argument_name].strip() != ""
        ):
            return tool_config.argument_descriptions[argument_name]
        return default

    def _setup_mcp_tools(self) -> None:
        """Set up MCP tools for the agent."""
        logger.info("Registering tools")

        tool_config = (
            self.config.mcp.tools.generate_ui_component
            if (
                self.config.mcp
                and self.config.mcp.tools
                and self.config.mcp.tools.generate_ui_component
            )
            else None
        )

        @self.mcp.tool(
            name="generate_ui_component",
            description=(
                tool_config.description
                if (
                    tool_config
                    and tool_config.description
                    and tool_config.description.strip() != ""
                )
                else (
                    "Generate one UI component for given user_prompt and data. "
                    "Always get fresh data from another tool first. "
                    "It's adviced to run the tool as last tool call in the chain, to be able process all data from previous tools calls."
                )
            ),
            enabled="generate_ui_component" in self.enabled_tools,
            # exclude session_id so LLM does not see it
            exclude_args=["session_id"],
        )
        async def generate_ui_component(
            ctx: Context,
            # Be sync with types.MCPGenerateUIInput !!!
            user_prompt: Annotated[
                str,
                Field(
                    description=self._get_argument_description(
                        tool_config,
                        "user_prompt",
                        "Original user query without any changes. Do not generate this.",
                    )
                ),
            ],
            data: Annotated[
                str,
                Field(
                    description=self._get_argument_description(
                        tool_config,
                        "data",
                        "Input raw data. COPY of data from another tool call. Do not change anything!. NEVER generate this.",
                    )
                ),
            ],
            data_type: Annotated[
                str,
                Field(
                    description=self._get_argument_description(
                        tool_config,
                        "data_type",
                        "Name of tool call used for 'data' argument. COPY of tool name. Do not change anything! NEVER generate this.",
                    )
                ),
            ],
            data_id: Annotated[
                str | None,
                Field(
                    description=self._get_argument_description(
                        tool_config,
                        "data_id",
                        "ID of tool call used for 'data' argument. Exact COPY of tool name. Do not change anything! NEVER generate this.",
                    )
                ),
            ] = None,
            # session_id should be sent as part of metadata. However some frameworks do not support that yet and send it as argument, e.g. Llama-stack
            session_id: Annotated[
                str | None,
                Field(
                    description=self._get_argument_description(
                        tool_config, "session_id", "Session ID"
                    )
                ),
            ] = None,
        ) -> ToolResult:
            if not data_id:
                data_id = str(uuid.uuid4())

            await ctx.info("Starting UI generation...")
            logger.debug("generate_ui_component invoked with session_id=%s", session_id)
            try:
                input_data = InputData(data=data, type=data_type, id=data_id)
                inference = await self.get_ngui_inference(ctx)
                ui_block = await self.generate_ui_block(
                    ctx=ctx,
                    user_prompt=user_prompt,
                    input_data=input_data,
                    inference=inference,
                )
                summary = f"Component is rendered in UI. {self.ngui_agent.component_info(ui_block.configuration)}"
                return self.create_mcp_output(blocks=[ui_block], summary=summary)
            except Exception as e:
                logger.exception("Error during UI generation")
                await ctx.error(f"UI generation failed: {e}")
                raise e

        tool_config_multiple = (
            self.config.mcp.tools.generate_ui_multiple_components
            if (
                self.config.mcp
                and self.config.mcp.tools
                and self.config.mcp.tools.generate_ui_multiple_components
            )
            else None
        )

        @self.mcp.tool(
            name="generate_ui_multiple_components",
            description=(
                tool_config_multiple.description
                if (
                    tool_config_multiple
                    and tool_config_multiple.description
                    and tool_config_multiple.description.strip() != ""
                )
                else (
                    "Generate multiple UI components for given user_prompt. "
                    "Always get fresh data from another tool first. "
                    "It's adviced to run the tool as last tool call in the chain, to be able process all data from previous tools calls."
                )
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
                    description=self._get_argument_description(
                        tool_config_multiple,
                        "user_prompt",
                        "Original user query without any changes. Do not generate this.",
                    )
                ),
            ],
            structured_data: Annotated[
                List[InputData] | None,
                Field(
                    description=self._get_argument_description(
                        tool_config_multiple,
                        "structured_data",
                        "Structured Input Data. Array of objects with 'id', 'data' and 'type' keys. NEVER generate this.",
                    )
                ),
            ] = None,
            # session_id should be sent as part of metadata. However some frameworks do not support that yet and send it as argument, e.g. Llama-stack
            session_id: Annotated[
                str | None,
                Field(
                    description=self._get_argument_description(
                        tool_config_multiple, "session_id", "Session ID"
                    )
                ),
            ] = None,
        ) -> ToolResult:
            logger.debug(
                "generate_ui_multiple_components invoked with session_id=%s", session_id
            )
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
                        f"{len(success_output)}. {self.ngui_agent.component_info(ui_block.configuration)}"
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
            inference = MCPSamplingInference(
                ctx,
                max_tokens=self.sampling_max_tokens,
                model_hints=self.sampling_model_hints,
                cost_priority=self.sampling_cost_priority,
                speed_priority=self.sampling_speed_priority,
                intelligence_priority=self.sampling_intelligence_priority,
            )
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
