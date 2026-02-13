"""Debug tool for inspecting system prompts used by the Next Gen UI Agent.

This tool allows you to inspect the actual system prompts that would be used
at runtime for different configurations and data types. Useful for prompt tuning
and understanding how the agent behaves with different settings.

Usage:
    python -m next_gen_ui_agent.debug_system_prompt [options]

    or with pants:
    ./pants run libs/next_gen_ui_agent:debug_system_prompt -- [options]
"""

import argparse
import sys

from next_gen_ui_agent.agent_config import read_config_yaml_file
from next_gen_ui_agent.component_selection_llm_onestep import (
    OnestepLLMCallComponentSelectionStrategy,
)
from next_gen_ui_agent.component_selection_llm_strategy import (
    ComponentSelectionStrategy,
)
from next_gen_ui_agent.component_selection_llm_twostep import (
    TwostepLLMCallComponentSelectionStrategy,
)
from next_gen_ui_agent.types import AgentConfig


def create_argument_parser() -> argparse.ArgumentParser:
    """Create argument parser for debug tool."""
    parser = argparse.ArgumentParser(
        description="Debug tool for inspecting Next Gen UI Agent system prompts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Inspect default configuration
  python -m next_gen_ui_agent.debug_system_prompt

  # Inspect with custom config and data type
  python -m next_gen_ui_agent.debug_system_prompt --config-path config.yaml --data-type "k8s:deployment"

  # Inspect two-step strategy step2 prompt for specific component
  python -m next_gen_ui_agent.debug_system_prompt --strategy two_llm_calls --component chart-bar
        """,
    )

    parser.add_argument(
        "--config-path",
        action="append",
        help="Path to YAML config file (can be specified multiple times for config merging)",
    )

    parser.add_argument(
        "--strategy",
        choices=["one_llm_call", "two_llm_calls"],
        help="Component selection strategy (defaults to config value or 'one_llm_call')",
    )

    parser.add_argument(
        "--data-type",
        help="Optional data type for data-type-specific prompt inspection",
    )

    parser.add_argument(
        "--component",
        help="For two-step strategy: specific component name to show step2 prompt (e.g., 'table', 'chart-bar')",
    )

    parser.add_argument(
        "--selectable-components",
        nargs="+",
        help="Override which components are selectable (space-separated list)",
    )

    return parser


def print_separator(char: str = "=", length: int = 65) -> None:
    """Print a separator line."""
    print(char * length)


def print_section_header(title: str) -> None:
    """Print a section header."""
    print_separator()
    print(title)
    print_separator()
    print()


def format_allowed_components(components: set[str]) -> str:
    """Format allowed components as a comma-separated string."""
    return ", ".join(sorted(components))


def main() -> int:
    """Main entry point for debug tool."""
    parser = create_argument_parser()
    args = parser.parse_args()

    # Load configuration
    config: AgentConfig
    if args.config_path:
        try:
            config = read_config_yaml_file(args.config_path)
        except Exception as e:
            print(f"Error loading config file(s): {e}", file=sys.stderr)
            return 1
    else:
        # Use default empty config
        config = AgentConfig()

    # Override selectable_components if specified
    if args.selectable_components:
        config.selectable_components = set(args.selectable_components)

    # Determine strategy to use
    strategy_type = (
        args.strategy or config.component_selection_strategy or "one_llm_call"
    )

    # Override config strategy if specified via CLI
    if args.strategy:
        config.component_selection_strategy = args.strategy

    # Create strategy instance
    strategy: ComponentSelectionStrategy
    try:
        if strategy_type == "two_llm_calls":
            strategy = TwostepLLMCallComponentSelectionStrategy(config=config)
        else:
            strategy = OnestepLLMCallComponentSelectionStrategy(config=config)
    except Exception as e:
        print(f"Error creating strategy: {e}", file=sys.stderr)
        return 1

    # Get debug prompts
    data_type = args.data_type
    component_for_step2 = args.component

    try:
        prompts = strategy.get_debug_prompts(
            data_type=data_type, component_for_step2=component_for_step2
        )
    except Exception as e:
        print(f"Error getting debug prompts: {e}", file=sys.stderr)
        return 1

    # Display output
    print_separator()
    print("SYSTEM PROMPT DEBUG OUTPUT")
    print_separator()
    print()
    print(f"Strategy: {strategy_type}")
    if data_type:
        print(f"Data Type: {data_type}")
    else:
        print("Data Type: (none - using global config)")

    # Get and display allowed components
    allowed_components = strategy.get_allowed_components(data_type)
    print(f"Allowed Components: {format_allowed_components(allowed_components)}")
    print()

    # Display prompts based on strategy type
    if strategy_type == "one_llm_call":
        # One-step strategy - single prompt
        print_section_header("SYSTEM PROMPT")
        print(prompts.get("system_prompt", ""))
        print()
        print_separator()
    else:
        # Two-step strategy - step1 and step2 prompts
        print_section_header("STEP 1: COMPONENT SELECTION PROMPT")
        print(prompts.get("step1_system_prompt", ""))
        print()

        # Display step2 prompts
        step2_prompts = {k: v for k, v in prompts.items() if k.startswith("step2_")}
        for prompt_key in sorted(step2_prompts.keys()):
            component_name = prompt_key.replace("step2_system_prompt_", "")
            print_section_header(
                f"STEP 2: FIELD CONFIGURATION PROMPT (component: {component_name})"
            )
            print(step2_prompts[prompt_key])
            print()

        print_separator()

    return 0


if __name__ == "__main__":
    sys.exit(main())
