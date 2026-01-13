#!/usr/bin/env python3
"""
Next Gen UI MCP Server Module Entry Point.

This module provides the Next Gen UI MCP server that can use MCP sampling
(default) or external LLM providers. The next_gen_ui_mcp package does not require
the necessary dependencies to run the server with custom inference providers, nor component systems.
You have to install the dependencies yourself as per your needs. By default MCP Sampling will be used for inference.

Usage:
    # Run with MCP sampling (default - leverages client's LLM)
    python -m next_gen_ui_mcp

    # Run with LlamaStack inference
    python -m next_gen_ui_mcp --provider llamastack --model llama3.2-3b --llama-url http://localhost:5001

    # Run with LangChain OpenAI inference
    python -m next_gen_ui_mcp --provider langchain --model gpt-3.5-turbo

    # Run with LangChain via Ollama (local)
    python -m next_gen_ui_mcp --provider langchain --model llama3.2 --base-url http://localhost:11434/v1 --api-key ollama

    # Run with MCP sampling and custom max tokens
    python -m next_gen_ui_mcp --sampling-max-tokens 4096

    # Run with MCP sampling and model preferences
    python -m next_gen_ui_mcp --provider mcp --sampling-hints claude-3-sonnet,claude --sampling-speed-priority 0.8 --sampling-intelligence-priority 0.7

    # Run with SSE transport (for HTTP clients)
    python -m next_gen_ui_mcp --transport sse --host 127.0.0.1 --port 8000

    # Run with streamable-http transport
    python -m next_gen_ui_mcp --transport streamable-http --host 127.0.0.1 --port 8000

    # Run with patternfly component system
    python -m next_gen_ui_mcp --component-system patternfly
"""

import argparse
import logging
import sys
from pathlib import Path

from fastmcp import FastMCP
from next_gen_ui_agent.agent_config import (
    add_agent_config_comandline_args,
    read_agent_config_dict_from_arguments,
)
from next_gen_ui_agent.argparse_env_default_action import EnvDefault, EnvDefaultExtend
from next_gen_ui_agent.inference.inference_builder import (
    add_inference_comandline_args,
    create_inference_from_arguments,
    get_sampling_cost_priority_configuration,
    get_sampling_hints_configuration,
    get_sampling_intelligence_priority_configuration,
    get_sampling_max_tokens_configuration,
    get_sampling_speed_priority_configuration,
)
from next_gen_ui_mcp.agent import MCP_ALL_TOOLS
from next_gen_ui_mcp.agent_config import MCPAgentConfig

# Add libs to path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

from next_gen_ui_agent.inference.inference_base import InferenceBase  # noqa: E402
from next_gen_ui_mcp import NextGenUIMCPServer  # noqa: E402

logger = logging.getLogger("NextGenUI-MCP-Server")


def create_server(
    config: MCPAgentConfig = MCPAgentConfig(component_system="json"),
    inference: InferenceBase | None = None,
    sampling_max_tokens: int = 2048,
    sampling_model_hints: list[str] | None = None,
    sampling_cost_priority: float | None = None,
    sampling_speed_priority: float | None = None,
    sampling_intelligence_priority: float | None = None,
    debug: bool = False,
    enabled_tools=None,
    structured_output_enabled=True,
) -> NextGenUIMCPServer:
    """Create NextGenUIMCPServer with optional external inference provider.

    Args:
        config: AgentConfig to use for the agent
        sampling_max_tokens: Maximum tokens for MCP sampling inference
        sampling_model_hints: Model hints for MCP sampling
        sampling_cost_priority: Cost priority for MCP sampling (0.0-1.0)
        sampling_speed_priority: Speed priority for MCP sampling (0.0-1.0)
        sampling_intelligence_priority: Intelligence priority for MCP sampling (0.0-1.0)

    Returns:
        Configured NextGenUIMCPServer
    """
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("NGUI Configuration: %s", config.model_dump())

    return NextGenUIMCPServer(
        config=config,
        inference=inference,
        sampling_max_tokens=sampling_max_tokens,
        sampling_model_hints=sampling_model_hints,
        sampling_cost_priority=sampling_cost_priority,
        sampling_speed_priority=sampling_speed_priority,
        sampling_intelligence_priority=sampling_intelligence_priority,
        name="NextGenUI-MCP-Server",
        debug=debug,
        enabled_tools=enabled_tools,
        structured_output_enabled=structured_output_enabled,
    )


def add_health_routes(mcp: FastMCP):
    """Add /liveness and /readiness via custom routes"""

    from starlette.responses import JSONResponse  # pants: no-infer-dep

    @mcp.custom_route("/liveness", methods=["GET"])
    async def liveness(request) -> JSONResponse:
        return JSONResponse({"status": "healthy", "service": "mcp-server"})

    @mcp.custom_route("/readiness", methods=["GET"])
    async def readiness(request) -> JSONResponse:
        return JSONResponse({"status": "healthy", "service": "mcp-server"})

    logger.info("Health checks available under /liveness and /readiness.")


PROVIDER_MCP = "mcp"


def main():
    """Main entry point."""

    parser = argparse.ArgumentParser(
        description="Next Gen UI MCP Server with Sampling or External LLM Providers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with MCP sampling (default - leverages client's LLM)
  python -m next_gen_ui_mcp

  # Run with YAML configurations
  python -m next_gen_ui_mcp -c ngui_config.yaml

  # Run with LlamaStack inference
  python -m next_gen_ui_mcp --provider openai --model llama3.2-3b --base-url http://localhost:5001/v1

  # Run with OpenAI inference
  python -m next_gen_ui_mcp --provider openai --model gpt-3.5-turbo

  # Run with OpenAI API of Ollama (local)
  python -m next_gen_ui_mcp --provider openai --model llama3.2 --base-url http://localhost:11434/v1 --api-key ollama

  # Run with MCP sampling and custom max tokens
  python -m next_gen_ui_mcp --sampling-max-tokens 4096

  # Run with MCP sampling and model preferences
  python -m next_gen_ui_mcp --sampling-hints claude-3-sonnet,claude --sampling-speed-priority 0.8 --sampling-intelligence-priority 0.7

  # Run with SSE transport (for web clients)
  python -m next_gen_ui_mcp --transport sse --host 127.0.0.1 --port 8000

  # Run with streamable-http transport
  python -m next_gen_ui_mcp --transport streamable-http --host 127.0.0.1 --port 8000

  # Run with rhds component system
  python -m next_gen_ui_mcp --component-system rhds

  # Run with rhds component system via SSE transport
  python -m next_gen_ui_mcp --transport sse --component-system rhds --port 8000
        """,
    )

    add_agent_config_comandline_args(parser)

    add_inference_comandline_args(
        parser, default_provider=PROVIDER_MCP, additional_providers=[PROVIDER_MCP]
    )

    # MCP sampling specific arguments
    parser.add_argument(
        "--sampling-hints",
        help="Comma-separated list of model hint names (e.g., 'claude-3-sonnet,claude'). Env variable NGUI_SAMPLING_HINTS can be used.",
        action=EnvDefault,
        envvar="NGUI_SAMPLING_HINTS",
        required=False,
    )
    parser.add_argument(
        "--sampling-cost-priority",
        type=float,
        help="Cost priority (0.0-1.0). Higher values prefer cheaper models. Env variable NGUI_SAMPLING_COST_PRIORITY can be used.",
        action=EnvDefault,
        envvar="NGUI_SAMPLING_COST_PRIORITY",
        required=False,
    )
    parser.add_argument(
        "--sampling-speed-priority",
        type=float,
        help="Speed priority (0.0-1.0). Higher values prefer faster models. Env variable NGUI_SAMPLING_SPEED_PRIORITY can be used.",
        action=EnvDefault,
        envvar="NGUI_SAMPLING_SPEED_PRIORITY",
        required=False,
    )
    parser.add_argument(
        "--sampling-intelligence-priority",
        type=float,
        help="Intelligence priority (0.0-1.0). Higher values prefer more capable models. Env variable NGUI_SAMPLING_INTELLIGENCE_PRIORITY can be used.",
        action=EnvDefault,
        envvar="NGUI_SAMPLING_INTELLIGENCE_PRIORITY",
        required=False,
    )

    # MCP Server specific arguments
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        required=True,
        help="Transport protocol to use",
        action=EnvDefault,
        envvar="MCP_TRANSPORT",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        required=True,
        help="Host to bind to",
        action=EnvDefault,
        envvar="MCP_HOST",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        required=True,
        help="Port to bind to",
        action=EnvDefault,
        envvar="MCP_PORT",
    )

    parser.add_argument(
        "--tools",
        action=EnvDefaultExtend,
        nargs="+",
        type=str,
        help=(
            "Control which tools should be enabled. "
            "You can specify multiple values by repeating same parameter "
            "or passing comma separated value. Value `all` means all tools are enabled, but you can simply omit this argument to enable all tools."
        ),
        envvar="MCP_TOOLS",
        required=False,
    )
    parser.add_argument(
        "--structured_output_enabled",
        choices=["true", "false"],
        default="true",
        help="Control if structured output is used. If not enabled the ouput is serialized as JSON in content property only.",
        action=EnvDefault,
        envvar="MCP_STRUCTURED_OUTPUT_ENABLED",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    config_dict = read_agent_config_dict_from_arguments(args, logger)
    config = MCPAgentConfig(**config_dict)

    enabled_tools = MCP_ALL_TOOLS
    if args.tools and args.tools != ["all"]:
        enabled_tools = args.tools

    transport: str = args.transport

    logger.info(
        "Starting Next Gen UI MCP Server with %s transport at host %s and port %s, debug=%s, tools=%s, structured_output_enabled=%s",
        transport,
        args.host,
        args.port,
        args.debug,
        enabled_tools,
        args.structured_output_enabled,
    )

    # Create inference provider
    try:
        inference = None
        if args.provider == "mcp":
            logger.info("Using MCP sampling - will leverage client's LLM capabilities")
            inference = None  # inference remains None for MCP sampling
        else:
            inference = create_inference_from_arguments(parser, args, logger)

        # Extract model preferences for MCP sampling
        sampling_model_hints = get_sampling_hints_configuration(args)
        sampling_cost_priority = get_sampling_cost_priority_configuration(args)
        sampling_speed_priority = get_sampling_speed_priority_configuration(args)
        sampling_intelligence_priority = (
            get_sampling_intelligence_priority_configuration(args)
        )

        # Create the agent
        agent = create_server(
            config=config,
            inference=inference,
            sampling_max_tokens=get_sampling_max_tokens_configuration(args, 2048),
            sampling_model_hints=sampling_model_hints,
            sampling_cost_priority=sampling_cost_priority,
            sampling_speed_priority=sampling_speed_priority,
            sampling_intelligence_priority=sampling_intelligence_priority,
            debug=args.debug,
            enabled_tools=enabled_tools,
            structured_output_enabled=args.structured_output_enabled == "true",
        )

    except (ImportError, RuntimeError) as e:
        logger.exception("Failed to initialize %s provider: %s", args.provider, e)
        sys.exit(1)

    # Run the server
    try:
        if transport == "stdio":
            logger.info("Server running on stdio - connect with MCP clients")
            agent.run(transport="stdio")
        elif transport == "sse":
            add_health_routes(agent.get_mcp_server())
            logger.info("Starting server on http://%s:%s/sse", args.host, args.port)
            agent.run(transport="sse", host=args.host, port=args.port)
        elif transport == "streamable-http":
            add_health_routes(agent.get_mcp_server())
            logger.info("Starting server on http://%s:%s/mcp", args.host, args.port)
            agent.run(transport="streamable-http", host=args.host, port=args.port)
        else:
            logger.error(
                "Invalid transport: %s. Use one of the following: stdio, sse, streamable-http",
                transport,
            )
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.exception("Server error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
