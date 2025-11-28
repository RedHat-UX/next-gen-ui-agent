"""
Inference builder from commandline arguments.
Used by all AI protocol servers.
"""

import argparse
import logging
import os
from typing import Optional

from next_gen_ui_agent.inference.inference_base import InferenceBase
from next_gen_ui_agent.inference.langchain_inference import LangChainModelInference


def create_llamastack_inference(
    model: str, llama_url: str, api_key: Optional[str] = None
) -> InferenceBase:
    """Create Remote LlamaStack server inference provider with dynamic import.

    Args:
        model: Model name to use
        llama_url: URL of the LlamaStack server
        api_key: API key for the LlamaStack server
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
            "LlamaStack Client dependencies not found. Install version from https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/libs/3rdparty/python/llama-stack-client-constraints.txt: "
            "pip install llama-stack-client==x.y.z"
        ) from e

    try:
        client = LlamaStackClient(base_url=llama_url, api_key=api_key)
        return LlamaStackAgentInference(client, model)
    except Exception as e:
        raise RuntimeError(
            f"Failed to connect to remote LlamaStack server at {llama_url}: {e}"
        ) from e


def create_langchain_openai_inference(
    model: str,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: float = 0.0,
) -> InferenceBase:
    """Create LangChain OpenAI API inference provider.

    Args:
        model: Model name to use (e.g., 'gpt-4', 'gpt-3.5-turbo', 'llama3.2')
        base_url: Optional base URL for custom OpenAI API compatible endpoints
        api_key: Optional API key (uses OPENAI_API_KEY env var if not provided)
        temperature: Temperature for the model (default: 0.0 for deterministic responses)

    Returns:
        LangChain OpenAI API inference instance

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
        default_provider: Default inference provider to use in help message, mandatory. Can be any of common providers or additional one.
        additional_providers: Additional server specific inference providers to use (default: []). Set of common providers is always used.

    Raises:
        ValueError: If default inference provider is not provided
    """

    if not default_provider:
        raise ValueError("Default inference provider is required")

    parser.add_argument(
        "--provider",
        choices=["llamastack", "openai"] + additional_providers,
        help=f"Inference provider to use (default: {default_provider}). Env variable NGUI_PROVIDER can be used.",
    )

    parser.add_argument(
        "--model",
        help="Model name to use. Required for `openai`, `llamastack`. Env variable NGUI_MODEL can be used.",
    )

    parser.add_argument(
        "--base-url",
        help="URL of the API endpoint. Env variable NGUI_PROVIDER_API_BASE_URL can be used. For `openai` defaults to OpenAI API, use eg. `http://localhost:11434/v1` for Ollama. For `llamastack` defaults to `http://localhost:5001`.",
    )

    parser.add_argument(
        "--api-key",
        help="API key for the LLM provider. Env variable NGUI_PROVIDER_API_KEY can be used (`openai` also uses OPENAI_API_KEY env var if not provided). Used by `openai`, `llamastack`.",
    )

    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Temperature for model inference (default to `0.0` for deterministic responses). Env variable NGUI_PROVIDER_API_TEMPERATURE can be used. Used by `openai`.",
    )


def create_inference_from_arguments(
    parser: argparse.ArgumentParser,
    args: argparse.Namespace,
    default_provider: str,
    logger: logging.Logger,
) -> InferenceBase:
    """
    Create inference provider from parsed commandline arguments or environment variables.
    Available arguments are defined in add_inference_comandline_args() function.
    Environment variables are prefixed with NGUI_PROVIDER_.
    Arguments have higher priority than environment variables.

    Args:
        parser: ArgumentParser instance to use for error reporting
        args: parsed commandline arguments to construct inference provider from
        default_provider: Default inference provider to use if not provided in commandline argument nor environment variable.
        logger: Logger to use for logging

    Returns:
        Inference provider instance

    Exits program with error if required arguments/environment variables
    are not provided (`parser.error()` is called).

    Raises:
        ValueError: If unknown inference provider is requested
        ImportError: If required dependencies are not installed for the inference provider
        RuntimeError: If initialization of the inference provider fails etc
    """

    provider = args.provider
    if not provider or provider.strip() == "":
        provider = os.getenv("NGUI_PROVIDER")
    if not provider or provider.strip() == "":
        provider = default_provider
    if not provider or provider.strip() == "":
        parser.error(
            "--provider argument or NGUI_PROVIDER environment variable is required."
        )

    model = args.model
    if not model or model.strip() == "":
        model = os.getenv("NGUI_MODEL")

    # Validate arguments
    if args.provider in ["llamastack", "openai"] and not model:
        parser.error(
            f"--model argument or NGUI_MODEL environment variable is required when using {args.provider} provider."
        )

    base_url = args.base_url
    if not base_url or base_url.strip() == "":
        base_url = os.getenv("NGUI_PROVIDER_API_BASE_URL")

    api_key = args.api_key
    if not api_key or api_key.strip() == "":
        api_key = os.getenv("NGUI_PROVIDER_API_KEY")

    temperature = args.temperature
    temperature_env = os.getenv("NGUI_PROVIDER_API_TEMPERATURE")
    if not temperature and temperature_env:
        temperature = float(temperature_env)

    # create provider specific inference instance
    if provider == "llamastack":
        if not base_url or base_url.strip() == "":
            base_url = "http://localhost:5001"
        logger.info(
            "Using LlamaStack inference with model %s at url %s",
            model,
            base_url,
        )
        return create_llamastack_inference(model, base_url, api_key)
    elif provider == "openai":
        logger.info("Using OpenAI inference with model %s", model)
        if base_url:
            logger.info("Using custom OpenAI API base URL: %s", base_url)
        return create_langchain_openai_inference(
            model=model,
            base_url=base_url,
            api_key=api_key,
            temperature=temperature,
        )
    else:
        raise ValueError(f"Unknown Inference provider: {provider}")
