"""
Inference builder from commandline arguments.
Used by all AI protocol servers.
"""

import argparse
import logging
import os
from typing import Optional

from next_gen_ui_agent.argparse_env_default_action import EnvDefault
from next_gen_ui_agent.inference.inference_base import InferenceBase
from next_gen_ui_agent.inference.langchain_inference import LangChainModelInference
from next_gen_ui_agent.inference.proxied_anthropic_vertexai_inference import (
    ProxiedAnthropicVertexAIInference,
)


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
        choices=["openai", "anthropic-vertexai"] + additional_providers,
        help=f"Inference provider to use (default: {default_provider}). Env variable NGUI_PROVIDER can be used.",
        default=default_provider,
        required=True,
        action=EnvDefault,
        envvar="NGUI_PROVIDER",
    )

    parser.add_argument(
        "--model",
        help="Model name to use. Required for `openai`, `anthropic-vertexai`. Env variable NGUI_MODEL can be used.",
        action=EnvDefault,
        envvar="NGUI_MODEL",
        required=False,
    )

    parser.add_argument(
        "--base-url",
        help="URL of the API endpoint. Env variable NGUI_PROVIDER_API_BASE_URL can be used. For `openai` defaults to OpenAI API, use eg. `http://localhost:11434/v1` for Ollama. Required for `anthropic-vertexai`",
        action=EnvDefault,
        envvar="NGUI_PROVIDER_API_BASE_URL",
        required=False,
    )

    parser.add_argument(
        "--api-key",
        help="API key for the LLM provider. Env variable NGUI_PROVIDER_API_KEY can be used (`openai` also uses OPENAI_API_KEY env var if not provided). Used by `openai`, `anthropic-vertexai`.",
        action=EnvDefault,
        envvar="NGUI_PROVIDER_API_KEY",
        required=False,
    )

    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Temperature for model inference (defaults to `0.0` for deterministic responses). Env variable NGUI_PROVIDER_TEMPERATURE can be used. Used by `openai`, `anthropic-vertexai`.",
        action=EnvDefault,
        envvar="NGUI_PROVIDER_TEMPERATURE",
        required=False,
    )

    parser.add_argument(
        "--anthropic-version",
        help="Anthropic version to use in API call (defaults to `vertex-2023-10-16`). Env variable NGUI_PROVIDER_ANTHROPIC_VERSION can be used. Used by `anthropic-vertexai`.",
        action=EnvDefault,
        envvar="NGUI_PROVIDER_ANTHROPIC_VERSION",
        required=False,
    )

    # MCP sampling specific arguments
    parser.add_argument(
        "--sampling-max-tokens",
        type=int,
        help="Maximum LLM generated tokens. Usage and default value differs per provider and model, see documentation. Env variable NGUI_SAMPLING_MAX_TOKENS can be used.",
        action=EnvDefault,
        envvar="NGUI_SAMPLING_MAX_TOKENS",
        required=False,
    )


def get_sampling_max_tokens_configuration(
    args: argparse.Namespace, default_max_tokens: int
) -> int:
    """
    Get maximum tokens produced by LLM configuration from commandline argument or environment variable.

    Args:
        args: parsed commandline arguments to construct inference provider from
        default_max_tokens: Default maximum tokens to use if not provided in commandline argument nor environment variable

    Returns:
        Maximum tokens produced by LLM
    """
    max_tokens_env = os.getenv("NGUI_PROVIDER_SAMPLING_MAX_TOKENS")
    max_tokens = args.sampling_max_tokens
    if not max_tokens and max_tokens_env and max_tokens_env.strip() != "":
        max_tokens = int(max_tokens_env)
    if not max_tokens:
        max_tokens = default_max_tokens
    return max_tokens  # type: ignore


def create_inference_from_arguments(
    parser: argparse.ArgumentParser,
    args: argparse.Namespace,
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

    model = args.model
    if args.provider in ["anthropic-vertexai", "openai"] and (
        not model or model.strip() == ""
    ):
        parser.error(
            f"--model argument or NGUI_MODEL environment variable is required when using {args.provider} provider."
        )

    base_url = args.base_url
    if provider == "anthropic-vertexai" and not base_url:
        parser.error(
            f"--base-url argument or NGUI_PROVIDER_API_BASE_URL environment variable is required when using {args.provider} provider."
        )

    api_key = args.api_key

    temperature = args.temperature

    # create provider specific inference instance
    if provider == "anthropic-vertexai":
        anthropic_version = args.anthropic_version
        if not anthropic_version or anthropic_version.strip() == "":
            anthropic_version = os.getenv("NGUI_PROVIDER_ANTHROPIC_VERSION")
        if not anthropic_version or anthropic_version.strip() == "":
            anthropic_version = "vertex-2023-10-16"
        logger.info(
            "Using Anthropic Vertex AI inference with model %s at url %s",
            model,
            base_url,
        )
        return ProxiedAnthropicVertexAIInference(
            model=model,
            api_key=api_key,
            temperature=temperature,
            base_url=base_url,
            anthropic_version=anthropic_version,
            max_tokens=get_sampling_max_tokens_configuration(args, 4096),
        )
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
