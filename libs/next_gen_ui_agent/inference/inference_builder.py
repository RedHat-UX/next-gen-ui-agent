"""
Inference builder from commandline arguments.
Used by all AI protocol servers.
"""

import argparse
import logging
import os
from typing import Optional, cast

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


PROVIDER_OPENAI = "openai"
PROVIDER_ANTHROPIC_VERTEXAI = "anthropic-vertexai"


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
        default="vertex-2023-10-16",
        required=False,
    )

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


def get_sampling_hints_configuration(
    args: argparse.Namespace,
) -> list[str] | None:
    """
    Get model hints configuration for use with MCP sampling from commandline argument or environment variable.

    Args:
        args: parsed commandline arguments to construct inference provider from

    Returns:
        List of model hint names, or None if not provided
    """
    hints_env = os.getenv("NGUI_SAMPLING_HINTS")
    hints_str = args.sampling_hints
    if not hints_str and hints_env and hints_env.strip() != "":
        hints_str = hints_env
    if not hints_str:
        return None
    # Parse comma-separated string and strip whitespace
    return [hint.strip() for hint in hints_str.split(",") if hint.strip()]


def get_sampling_cost_priority_configuration(
    args: argparse.Namespace,
) -> float | None:
    """
    Get cost priority configuration for use with MCP sampling from commandline argument or environment variable.

    Args:
        args: parsed commandline arguments to construct inference provider from

    Returns:
        Cost priority value (0.0-1.0), or None if not provided
    """
    cost_priority_env = os.getenv("NGUI_SAMPLING_COST_PRIORITY")
    cost_priority: float | None = cast(float | None, args.sampling_cost_priority)
    if cost_priority is None and cost_priority_env and cost_priority_env.strip() != "":
        cost_priority = float(cost_priority_env)
    return cost_priority


def get_sampling_speed_priority_configuration(
    args: argparse.Namespace,
) -> float | None:
    """
    Get speed priority configuration for use with MCP sampling from commandline argument or environment variable.

    Args:
        args: parsed commandline arguments to construct inference provider from

    Returns:
        Speed priority value (0.0-1.0), or None if not provided
    """
    speed_priority_env = os.getenv("NGUI_SAMPLING_SPEED_PRIORITY")
    speed_priority: float | None = cast(float | None, args.sampling_speed_priority)
    if (
        speed_priority is None
        and speed_priority_env
        and speed_priority_env.strip() != ""
    ):
        speed_priority = float(speed_priority_env)
    return speed_priority


def get_sampling_intelligence_priority_configuration(
    args: argparse.Namespace,
) -> float | None:
    """
    Get intelligence priority configuration for use with MCP sampling from commandline argument or environment variable.

    Args:
        args: parsed commandline arguments to construct inference provider from

    Returns:
        Intelligence priority value (0.0-1.0), or None if not provided
    """
    intelligence_priority_env = os.getenv("NGUI_SAMPLING_INTELLIGENCE_PRIORITY")
    intelligence_priority: float | None = cast(
        float | None, args.sampling_intelligence_priority
    )
    if (
        intelligence_priority is None
        and intelligence_priority_env
        and intelligence_priority_env.strip() != ""
    ):
        intelligence_priority = float(intelligence_priority_env)
    return intelligence_priority


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
        max_tokens = get_sampling_max_tokens_configuration(args, 4096)
        logger.info(
            "Using Anthropic Vertex AI inference with model %s, anthropic version %s, temperature %s, max tokens %s, at base URL: %s.",
            model,
            anthropic_version,
            temperature,
            max_tokens,
            base_url,
        )
        return ProxiedAnthropicVertexAIInference(
            model=model,
            api_key=api_key,
            temperature=temperature,
            base_url=base_url,
            anthropic_version=anthropic_version,
            max_tokens=max_tokens,
        )
    elif provider == "openai":
        logger.info(
            "Using OpenAI inference with model %s, temperature %s", model, temperature
        )
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
