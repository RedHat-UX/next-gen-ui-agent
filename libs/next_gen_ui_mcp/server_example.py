#!/usr/bin/env python3
"""
Example MCP server using Next Gen UI Agent.

This script demonstrates how to run the Next Gen UI MCP server
that uses MCP sampling to leverage the client's LLM capabilities.

Usage:
    # Run with stdio transport (default)
    python server_example.py

    # Run with SSE transport (for HTTP clients)
    python server_example.py --transport sse --host 127.0.0.1 --port 8000

    # Run with streamable-http transport
    python server_example.py --transport streamable-http --host 127.0.0.1 --port 8000
"""

import argparse
import logging
import sys
from pathlib import Path

# Add libs to path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

from next_gen_ui_mcp.agent import NextGenUIMCPAgent  # noqa: E402


def create_agent() -> NextGenUIMCPAgent:
    """Create NextGenUIMCPAgent that uses MCP sampling.

    Returns:
        Configured NextGenUIMCPAgent that uses sampling
    """
    return NextGenUIMCPAgent(
        component_system="json", name="NextGenUI-MCP-Server"
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Next Gen UI MCP Server with Sampling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with stdio transport (default)
  python server_example.py

  # Run with SSE transport (for web clients)
  python server_example.py --transport sse --host 127.0.0.1 --port 8000

  # Run with streamable-http transport
  python server_example.py --transport streamable-http --host 127.0.0.1 --port 8000
        """,
    )

    # Transport arguments
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport protocol to use",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Starting Next Gen UI MCP Server with {args.transport} transport")
    logger.info("Using MCP sampling - will leverage client's LLM capabilities")

    # Create the agent (always uses sampling)
    agent = create_agent()

    # Run the server
    try:
        if args.transport == "stdio":
            logger.info("Server running on stdio - connect with MCP clients")
            agent.run(transport="stdio")
        elif args.transport == "sse":
            logger.info(f"Server running on http://{args.host}:{args.port}/sse")
            agent.run(transport="sse", host=args.host, port=args.port)
        elif args.transport == "streamable-http":
            logger.info(f"Server running on http://{args.host}:{args.port}")
            agent.run(transport="streamable-http", host=args.host, port=args.port)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
