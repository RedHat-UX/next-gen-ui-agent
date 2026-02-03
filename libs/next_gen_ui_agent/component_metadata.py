"""Component metadata validation and merging for prompt customization.

This module provides functionality to override COMPONENT_METADATA fields through
AgentConfig, with validation and optimized runtime access.
"""

from typing import Any

from next_gen_ui_agent.component_selection_common import (
    ALL_COMPONENTS,
    COMPONENT_METADATA,
)
from next_gen_ui_agent.types import (
    AgentConfig,
    AgentConfigComponent,
    AgentConfigPromptComponent,
)


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
        # Get all non-None fields from the Pydantic model
        all_possible_fields.update(
            component_metadata.model_dump(exclude_none=True).keys()
        )

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
    base: dict[str, AgentConfigPromptComponent], overrides: dict[str, Any]
) -> dict[str, AgentConfigPromptComponent]:
    """Merge component metadata overrides into base metadata.

    Args:
        base: Base COMPONENT_METADATA dictionary with AgentConfigPromptComponent values
        overrides: Dictionary mapping component names to field overrides

    Returns:
        New dictionary with overrides applied (as AgentConfigPromptComponent instances)
    """
    # Create a deep copy of base metadata
    merged: dict[str, AgentConfigPromptComponent] = {}

    for component_name, component_meta in base.items():
        # Get dict representation
        meta_dict = component_meta.model_dump()

        # Apply overrides for this component if any
        if component_name in overrides:
            for field_name, field_value in overrides[component_name].items():
                if field_value is not None:  # Only apply non-None values
                    meta_dict[field_name] = field_value

        # Create new AgentConfigPromptComponent with merged values
        merged[component_name] = AgentConfigPromptComponent(**meta_dict)

    return merged


def merge_per_component_prompt_overrides(
    base_metadata: dict[str, AgentConfigPromptComponent],
    components_list: list[AgentConfigComponent],
) -> dict[str, AgentConfigPromptComponent]:
    """Merge per-component prompt overrides into metadata.

    Args:
        base_metadata: Base metadata (already includes global overrides)
        components_list: List of components with potential prompt overrides

    Returns:
        Metadata with per-component overrides applied
    """
    # Start with base metadata
    merged: dict[str, AgentConfigPromptComponent] = {}

    # First copy all base metadata
    for component_name, component_meta in base_metadata.items():
        merged[component_name] = component_meta

    # Iterate through components and apply per-component prompt overrides
    for component in components_list:
        if component.prompt:
            component_name = component.component
            # Convert prompt to dict, excluding None values
            prompt_dict = component.prompt.model_dump(exclude_none=True)
            if prompt_dict and component_name in merged:
                # Get existing metadata as dict and apply overrides
                meta_dict = merged[component_name].model_dump()
                for field_name, field_value in prompt_dict.items():
                    meta_dict[field_name] = field_value
                # Create new instance with overrides
                merged[component_name] = AgentConfigPromptComponent(**meta_dict)

    return merged


def get_component_metadata(
    config: AgentConfig,
) -> dict[str, AgentConfigPromptComponent]:
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
