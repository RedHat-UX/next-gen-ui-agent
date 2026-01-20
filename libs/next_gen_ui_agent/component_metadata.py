"""Component metadata validation and merging for prompt customization.

This module provides functionality to override COMPONENT_METADATA fields through
AgentConfig, with validation and optimized runtime access.
"""

from copy import deepcopy
from typing import Any

from next_gen_ui_agent.component_selection_common import (
    ALL_COMPONENTS,
    COMPONENT_METADATA,
)
from next_gen_ui_agent.types import AgentConfig


def validate_component_overrides(overrides: dict[str, Any]) -> None:
    """Validate component metadata overrides.

    Args:
        overrides: Dictionary mapping component names to field overrides

    Raises:
        ValueError: If component name is invalid or field names don't exist in COMPONENT_METADATA
    """
    if not overrides:
        return

    # Check each component name is valid
    for component_name in overrides.keys():
        if component_name not in ALL_COMPONENTS:
            raise ValueError(
                f"Invalid component name '{component_name}' in prompt.components override. "
                f"Valid component names are: {', '.join(sorted(ALL_COMPONENTS))}"
            )

    # Collect all possible field names from all components in COMPONENT_METADATA
    # This allows any field to be used on any component (even if it doesn't make sense)
    all_possible_fields: set[Any] = set()
    for component_metadata in COMPONENT_METADATA.values():
        all_possible_fields.update(component_metadata.keys())

    # Validate field names exist somewhere in COMPONENT_METADATA
    for component_name, component_overrides in overrides.items():
        for field_name in component_overrides.keys():
            if field_name not in all_possible_fields:
                raise ValueError(
                    f"Invalid field name '{field_name}' for component '{component_name}' "
                    f"in prompt.components override. Valid field names are: "
                    f"{', '.join(sorted(all_possible_fields))}"
                )


def merge_component_metadata(
    base: dict[str, dict[str, Any]], overrides: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    """Merge component metadata overrides into base metadata.

    Args:
        base: Base COMPONENT_METADATA dictionary
        overrides: Dictionary mapping component names to field overrides

    Returns:
        New dictionary with overrides applied (does not modify base)
    """
    # Start with deep copy to avoid modifying the original
    merged = deepcopy(base)

    # Apply overrides for each component
    for component_name, component_overrides in overrides.items():
        if component_name in merged:
            # Update only the specified fields
            for field_name, field_value in component_overrides.items():
                if field_value is not None:  # Only apply non-None values
                    merged[component_name][field_name] = field_value

    return merged


def get_component_metadata(config: AgentConfig) -> dict[str, dict[str, Any]]:
    """Get component metadata with overrides applied from config.

    Args:
        config: AgentConfig with optional prompt.components overrides

    Returns:
        Component metadata dictionary (base or merged with overrides)

    Raises:
        ValueError: If overrides contain invalid component or field names
    """
    # Return base metadata if no overrides
    if not config.prompt or not config.prompt.components:
        return COMPONENT_METADATA

    # Convert Pydantic models to dict for processing
    overrides_dict = {}
    for component_name, component_config in config.prompt.components.items():
        # Convert AgentConfigPromptComponents to dict, excluding None values
        component_dict = component_config.model_dump(exclude_none=True)
        if component_dict:  # Only include if there are actual overrides
            overrides_dict[component_name] = component_dict

    # Validate overrides
    validate_component_overrides(overrides_dict)

    # Merge and return
    return merge_component_metadata(COMPONENT_METADATA, overrides_dict)
