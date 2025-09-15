#!/usr/bin/env python3
"""
Example MCP server using Next Gen UI Agent.

This script demonstrates how to run the Next Gen UI MCP server
that can use MCP sampling (default) or external LLM providers.

Usage:
    # Run with MCP sampling (default - leverages client's LLM)
    python server_example.py

    # Run with LlamaStack inference
    python server_example.py --provider llamastack --model llama3.2-3b --llama-url http://localhost:5001

    # Run with BeeAI inference
    python server_example.py --provider beeai --model granite3.3-8b

    # Run with SSE transport (for HTTP clients)
    python server_example.py --transport sse --host 127.0.0.1 --port 8000

    # Run with streamable-http transport
    python server_example.py --transport streamable-http --host 127.0.0.1 --port 8000

    # Run with patternfly component system
    python server_example.py --component-system patternfly
"""

import argparse
import logging
import sys
from pathlib import Path

# Add libs to path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

from next_gen_ui_agent.model import InferenceBase  # noqa: E402
from next_gen_ui_mcp.agent import NextGenUIMCPAgent  # noqa: E402


def create_llamastack_inference(model: str, llama_url: str) -> InferenceBase:
    """Create LlamaStack inference provider with dynamic import.

    Args:
        model: Model name to use
        llama_url: URL of the LlamaStack server

    Returns:
        LlamaStack inference instance

    Raises:
        ImportError: If llama-stack-client is not installed
        RuntimeError: If connection to LlamaStack fails
    """
    try:
        from llama_stack_client import LlamaStackClient
        from next_gen_ui_llama_stack.llama_stack_inference import (
            LlamaStackAgentInference,
        )
    except ImportError as e:
        raise ImportError(
            "LlamaStack dependencies not found. Install with: "
            "pip install llama-stack-client>=0.1.9,<=0.2.15"
        ) from e

    try:
        client = LlamaStackClient(base_url=llama_url)
        return LlamaStackAgentInference(client, model)
    except Exception as e:
        raise RuntimeError(
            f"Failed to connect to LlamaStack at {llama_url}: {e}"
        ) from e


def create_beeai_inference(model: str) -> InferenceBase:
    """Create BeeAI inference provider with dynamic import.

    Args:
        model: Model name to use

    Returns:
        BeeAI inference instance

    Raises:
        ImportError: If beeai-framework is not installed
        RuntimeError: If model initialization fails
    """
    try:
        from next_gen_ui_beeai.beeai_inference import BeeAIInference
    except ImportError as e:
        raise ImportError(
            "BeeAI dependencies not found. Install with: " "pip install beeai-framework"
        ) from e

    try:
        return BeeAIInference(model)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize BeeAI model {model}: {e}") from e


def create_agent(component_system: str = "json", inference: InferenceBase = None) -> NextGenUIMCPAgent:
    """Create NextGenUIMCPAgent with optional external inference provider.

    Args:
        component_system: Component system to use (json, patternfly, rhds)
        inference: External inference provider (if None, uses MCP sampling)

    Returns:
        Configured NextGenUIMCPAgent
    """
    return NextGenUIMCPAgent(
        component_system=component_system, inference=inference, name="NextGenUI-MCP-Server"
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Next Gen UI MCP Server with Sampling or External LLM Providers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with MCP sampling (default - leverages client's LLM)
  python server_example.py

  # Run with LlamaStack inference
  python server_example.py --provider llamastack --model llama3.2-3b --llama-url http://localhost:5001

  # Run with BeeAI inference
  python server_example.py --provider beeai --model granite3.3-8b


  # Run with SSE transport (for web clients)
  python server_example.py --transport sse --host 127.0.0.1 --port 8000

  # Run with streamable-http transport
  python server_example.py --transport streamable-http --host 127.0.0.1 --port 8000

  # Run with patternfly component system
  python server_example.py --component-system rhds

  # Run with rhds component system via SSE transport
  python server_example.py --transport sse --component-system rhds --port 8000
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
    parser.add_argument(
        "--component-system",
        choices=["json", "patternfly", "rhds"],
        default="json",
        help="Component system to use for rendering (default: json)"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    # Inference provider arguments
    parser.add_argument(
        "--provider",
        choices=["mcp", "llamastack", "beeai"],
        default="mcp",
        help="Inference provider to use (default: mcp - uses MCP sampling)",
    )
    parser.add_argument(
        "--model", help="Model name to use (required for llamastack and beeai)"
    )

    # LlamaStack specific arguments
    parser.add_argument(
        "--llama-url",
        default="http://localhost:5001",
        help="LlamaStack server URL (default: http://localhost:5001)",
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Starting Next Gen UI MCP Server with {args.transport} transport")
    logger.info(f"Using component system: {args.component_system}")

    # Validate arguments
    if args.provider in ["llamastack", "beeai"] and not args.model:
        parser.error(f"--model is required when using {args.provider} provider")

    # Create inference provider
    inference = None
    try:
        if args.provider == "mcp":
            logger.info("Using MCP sampling - will leverage client's LLM capabilities")
            # inference remains None for MCP sampling
        elif args.provider == "llamastack":
            logger.info(
                f"Using LlamaStack inference with model {args.model} at {args.llama_url}"
            )
            inference = create_llamastack_inference(args.model, args.llama_url)
        elif args.provider == "beeai":
            logger.info(f"Using BeeAI inference with model {args.model}")
            inference = create_beeai_inference(args.model)
        else:
            raise ValueError(f"Unknown provider: {args.provider}")

        # Create the agent
        agent = create_agent(component_system=args.component_system, inference=inference)

    except (ImportError, RuntimeError) as e:
        logger.error(f"Failed to initialize {args.provider} provider: {e}")
        sys.exit(1)

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
