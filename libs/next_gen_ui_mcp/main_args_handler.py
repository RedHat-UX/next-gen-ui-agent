"""
MCP Server Main Arguments Handler.

This module provides argument parsing and configuration handling for the MCP server.
"""

import argparse
import os
from typing import cast

from next_gen_ui_agent.agent_config import add_agent_config_comandline_args
from next_gen_ui_agent.argparse_env_default_action import EnvDefault, EnvDefaultExtend
from next_gen_ui_agent.inference.inference_builder import add_inference_comandline_args

PROVIDER_MCP = "mcp"


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser for the MCP server.

    Returns:
        Configured ArgumentParser instance
    """
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

    # Add agent configuration arguments
    add_agent_config_comandline_args(parser)

    # Add inference arguments
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

    return parser


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
