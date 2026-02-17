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

    # Run with custom CORS configuration
    python -m next_gen_ui_mcp --transport sse --cors-allow-origins "http://localhost:3000,http://localhost:8080"

    # Run with CORS allowing all origins (development only)
    python -m next_gen_ui_mcp --transport streamable-http --cors-allow-origins "*"

    # Run with patternfly component system
    python -m next_gen_ui_mcp --component-system patternfly
"""

import logging
import sys
from pathlib import Path

from fastmcp import FastMCP
from next_gen_ui_agent.agent_config import read_agent_config_dict_from_arguments
from next_gen_ui_agent.inference.inference_builder import (
    create_inference_from_arguments,
    get_sampling_max_tokens_configuration,
)
from next_gen_ui_mcp.agent import MCP_ALL_TOOLS
from next_gen_ui_mcp.agent_config import MCPAgentConfig
from next_gen_ui_mcp.main_args_handler import (
    create_argument_parser,
    get_cors_allow_credentials_configuration,
    get_cors_allow_headers_configuration,
    get_cors_allow_methods_configuration,
    get_cors_allow_origins_configuration,
    get_cors_expose_headers_configuration,
    get_csp_resource_domains_configuration,
    get_sampling_cost_priority_configuration,
    get_sampling_hints_configuration,
    get_sampling_intelligence_priority_configuration,
    get_sampling_speed_priority_configuration,
)

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
    csp_resource_domains: list[str] | None = None,
) -> NextGenUIMCPServer:
    """Create NextGenUIMCPServer with optional external inference provider.

    Args:
        config: AgentConfig to use for the agent
        sampling_max_tokens: Maximum tokens for MCP sampling inference
        sampling_model_hints: Model hints for MCP sampling
        sampling_cost_priority: Cost priority for MCP sampling (0.0-1.0)
        sampling_speed_priority: Speed priority for MCP sampling (0.0-1.0)
        sampling_intelligence_priority: Intelligence priority for MCP sampling (0.0-1.0)
        csp_resource_domains: List of allowed domains for Content Security Policy in UI

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
        csp_resource_domains=csp_resource_domains,
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


def main():
    """Main entry point."""

    parser = create_argument_parser()
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

        # Get CSP resource domains configuration
        csp_resource_domains = get_csp_resource_domains_configuration(args)

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
            csp_resource_domains=csp_resource_domains,
        )

    except (ImportError, RuntimeError) as e:
        logger.exception("Failed to initialize %s provider: %s", args.provider, e)
        sys.exit(1)

    # Configure CORS middleware for HTTP transports
    if transport in ["sse", "streamable-http"]:
        cors_allow_origins = get_cors_allow_origins_configuration(args)
        cors_allow_credentials = get_cors_allow_credentials_configuration(args)
        cors_allow_methods = get_cors_allow_methods_configuration(args)
        cors_allow_headers = get_cors_allow_headers_configuration(args)
        cors_expose_headers = get_cors_expose_headers_configuration(args)

        agent.configure_cors(
            allow_origins=cors_allow_origins,
            allow_credentials=cors_allow_credentials,
            allow_methods=cors_allow_methods,
            allow_headers=cors_allow_headers,
            expose_headers=cors_expose_headers,
        )

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
