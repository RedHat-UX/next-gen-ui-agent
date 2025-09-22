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
from typing import Optional

from next_gen_ui_agent.types import AgentConfig

# Add libs to path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

from next_gen_ui_agent.model import InferenceBase, LangChainModelInference  # noqa: E402
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
        from llama_stack_client import LlamaStackClient  # pants: no-infer-dep
        from next_gen_ui_llama_stack.llama_stack_inference import (
            LlamaStackAgentInference,  # pants: no-infer-dep
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


def create_langchain_inference(
    model: str,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: float = 0.0,
) -> InferenceBase:
    """Create LangChain inference provider with ChatOpenAI.

    Args:
        model: Model name to use (e.g., 'gpt-4', 'gpt-3.5-turbo', 'llama3.2')
        base_url: Optional base URL for custom OpenAI-compatible endpoints
        api_key: Optional API key (uses OPENAI_API_KEY env var if not provided)
        temperature: Temperature for the model (default: 0.0 for deterministic responses)

    Returns:
        LangChain inference instance

    Raises:
        ImportError: If langchain-openai is not installed
        RuntimeError: If model initialization fails
    """
    try:
        from langchain_openai import ChatOpenAI  # pants: no-infer-dep
    except ImportError as e:
        raise ImportError(
            "LangChain OpenAI dependencies not found. Install with: "
            "pip install langchain-openai"
        ) from e

    try:
        llm_settings = {
            "model": model,
            "temperature": temperature,
            "disable_streaming": True,
        }

        # Add optional parameters if provided
        if base_url:
            llm_settings["base_url"] = base_url
        if api_key:
            llm_settings["api_key"] = api_key

        llm = ChatOpenAI(**llm_settings)  # type: ignore
        return LangChainModelInference(llm)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize LangChain model {model}: {e}") from e


def create_agent(
    config: AgentConfig = AgentConfig(component_system="json"),
    sampling_max_tokens: int = 2048,
) -> NextGenUIMCPAgent:
    """Create NextGenUIMCPAgent with optional external inference provider.

    Args:
        config: AgentConfig to use for the agent
        sampling_max_tokens: Maximum tokens for MCP sampling inference

    Returns:
        Configured NextGenUIMCPAgent
    """
    return NextGenUIMCPAgent(
        config=config,
        sampling_max_tokens=sampling_max_tokens,
        name="NextGenUI-MCP-Server",
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Next Gen UI MCP Server with Sampling or External LLM Providers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
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

  # Run with SSE transport (for web clients)
  python -m next_gen_ui_mcp --transport sse --host 127.0.0.1 --port 8000

  # Run with streamable-http transport
  python -m next_gen_ui_mcp --transport streamable-http --host 127.0.0.1 --port 8000

  # Run with patternfly component system
  python -m next_gen_ui_mcp --component-system rhds

  # Run with rhds component system via SSE transport
  python -m next_gen_ui_mcp --transport sse --component-system rhds --port 8000
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
        help="Component system to use for rendering (default: json)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    # Inference provider arguments
    parser.add_argument(
        "--provider",
        choices=["mcp", "llamastack", "langchain"],
        default="mcp",
        help="Inference provider to use (default: mcp - uses MCP sampling)",
    )
    parser.add_argument(
        "--model", help="Model name to use (required for llamastack and langchain)"
    )

    # LlamaStack specific arguments
    parser.add_argument(
        "--llama-url",
        default="http://localhost:5001",
        help="LlamaStack server URL (default: http://localhost:5001)",
    )

    # LangChain specific arguments
    parser.add_argument(
        "--base-url",
        help="Base URL for OpenAI-compatible API (e.g., http://localhost:11434/v1 for Ollama)",
    )
    parser.add_argument(
        "--api-key",
        help="API key for the LLM provider (uses OPENAI_API_KEY env var if not provided)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Temperature for LangChain model (default: 0.0 for deterministic responses)",
    )

    # MCP sampling specific arguments
    parser.add_argument(
        "--sampling-max-tokens",
        type=int,
        default=2048,
        help="Maximum tokens for MCP sampling inference (default: 2048)",
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger = logging.getLogger(__name__)
    logger.info("Starting Next Gen UI MCP Server with %s transport", args.transport)
    logger.info("Using component system: %s", args.component_system)

    # Validate arguments
    if args.provider in ["llamastack", "langchain"] and not args.model:
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
        elif args.provider == "langchain":
            logger.info("Using LangChain inference with model %s", args.model)
            if args.base_url:
                logger.info("Using custom base URL: %s", args.base_url)
            inference = create_langchain_inference(
                model=args.model,
                base_url=args.base_url,
                api_key=args.api_key,
                temperature=args.temperature,
            )
        else:
            raise ValueError(f"Unknown provider: {args.provider}")

        # Create the agent
        agent = create_agent(
            config=AgentConfig(
                component_system=args.component_system, inference=inference
            ),
            sampling_max_tokens=args.sampling_max_tokens,
        )

    except (ImportError, RuntimeError) as e:
        logger.exception("Failed to initialize %s provider: %s", args.provider, e)
        sys.exit(1)

    # Run the server
    try:
        if args.transport == "stdio":
            logger.info("Server running on stdio - connect with MCP clients")
            agent.run(transport="stdio")
        elif args.transport == "sse":
            logger.info("Server running on http://%s:%s/sse", args.host, args.port)
            agent.run(transport="sse", host=args.host, port=args.port)
        elif args.transport == "streamable-http":
            logger.info("Server running on http://%s:%s/mcp", args.host, args.port)
            agent.run(transport="streamable-http", host=args.host, port=args.port)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.exception("Server error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
