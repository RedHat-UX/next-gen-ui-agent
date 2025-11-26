"""
Inference builder from commandline arguments.
Used by all AI protocol servers.
"""

import argparse
import logging
from typing import Optional

from next_gen_ui_agent.inference.inference_base import InferenceBase
from next_gen_ui_agent.inference.langchain_inference import LangChainModelInference


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
            "pip install llama-stack-client==0.2.20"
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


def add_inference_comandline_args(
    parser: argparse.ArgumentParser,
    default_provider: str,
    additional_providers: list[str] = [],
):
    """
    Adds commandline definition for inference provider related arguments used in create_inference_from_arguments() function to the ArgumentParser instance.

    Args:
        parser: ArgumentParser instance to add arguments to.
        default_provider: Default inference provider to use, mandatory. Can be any of common providers or additional one.
        additional_providers: Additional server specific inference providers to use (default: []). Set of common providers is always used.

    Raises:
        ValueError: If default inference provider is not provided
    """

    if not default_provider:
        raise ValueError("Default inference provider is required")

    parser.add_argument(
        "--provider",
        choices=["mcp", "llamastack", "langchain"] + additional_providers,
        default=default_provider,
        help=f"Inference provider to use (default: {default_provider})",
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


def create_inference_from_arguments(
    parser: argparse.ArgumentParser, args: argparse.Namespace, logger: logging.Logger
) -> InferenceBase:
    """
    Create inference provider from parsed commandline arguments. Available arguments are defined in add_inference_comandline_args() function.

    Args:
        parser: ArgumentParser instance to use for error reporting
        args: parsed commandline arguments to construct inference provider from
        logger: Logger to use for logging

    Returns:
        Inference provider instance

    Raises:
        ValueError: If unknown inference provider is requested
        ImportError: If required dependencies are not installed for the inference provider
        RuntimeError: If initialization of the inference provider fails etc
    """

    # Validate arguments
    if args.provider in ["llamastack", "langchain"] and not args.model:
        parser.error(f"--model is required when using {args.provider} provider")

    if args.provider == "llamastack":
        logger.info(
            "Using LlamaStack inference with model %s at %s",
            args.model,
            args.llama_url,
        )
        return create_llamastack_inference(args.model, args.llama_url)
    elif args.provider == "langchain":
        logger.info("Using LangChain inference with model %s", args.model)
        if args.base_url:
            logger.info("Using custom base URL: %s", args.base_url)
        return create_langchain_inference(
            model=args.model,
            base_url=args.base_url,
            api_key=args.api_key,
            temperature=args.temperature,
        )
    else:
        raise ValueError(f"Unknown Inference provider: {args.provider}")
