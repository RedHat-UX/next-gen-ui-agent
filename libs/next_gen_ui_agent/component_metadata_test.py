"""Tests for component_metadata module."""

import pytest
from next_gen_ui_agent.component_metadata import (
    get_component_metadata,
    merge_component_metadata,
    validate_component_overrides,
)
from next_gen_ui_agent.component_selection_common import COMPONENT_METADATA
from next_gen_ui_agent.types import (
    AgentConfig,
    AgentConfigPrompt,
    AgentConfigPromptComponent,
)


def test_validate_component_overrides_valid_single_component():
    """Test validation succeeds for valid single component override."""
    overrides = {"table": {"description": "Custom table description"}}
    # Should not raise any exception
    validate_component_overrides(overrides)


def test_validate_component_overrides_valid_multiple_components():
    """Test validation succeeds for valid multiple component overrides."""
    overrides = {
        "table": {"description": "Custom table description"},
        "chart-bar": {"chart_description": "Custom bar chart"},
    }
    # Should not raise any exception
    validate_component_overrides(overrides)


def test_validate_component_overrides_invalid_component_name():
    """Test validation fails for invalid component name."""
    overrides = {"invalid-component": {"description": "Some description"}}
    with pytest.raises(ValueError) as exc_info:
        validate_component_overrides(overrides)

    assert "Invalid component name 'invalid-component'" in str(exc_info.value)
    assert "Valid component names are:" in str(exc_info.value)


def test_validate_component_overrides_typo_in_component_name():
    """Test validation catches typo in component name."""
    overrides = {"chart-barr": {"description": "Typo in component name"}}  # Extra 'r'
    with pytest.raises(ValueError) as exc_info:
        validate_component_overrides(overrides)

    assert "Invalid component name 'chart-barr'" in str(exc_info.value)


def test_validate_component_overrides_invalid_field_name():
    """Test validation fails for field name that doesn't exist in any component."""
    overrides = {"table": {"completely_invalid_field_xyz": "Some value"}}
    with pytest.raises(ValueError) as exc_info:
        validate_component_overrides(overrides)

    assert "Invalid field name 'completely_invalid_field_xyz'" in str(exc_info.value)
    assert "Valid field names are:" in str(exc_info.value)


def test_validate_component_overrides_empty():
    """Test validation succeeds for empty overrides."""
    # Should not raise any exception
    validate_component_overrides({})
    validate_component_overrides(None)


def test_validate_component_overrides_cross_component_fields():
    """Test that chart fields can be used on non-chart components and vice versa."""
    # Chart fields on non-chart component - should be allowed
    overrides = {"table": {"chart_description": "Some value"}}
    # Should not raise any exception
    validate_component_overrides(overrides)

    # Non-chart fields on chart component - should be allowed
    overrides2 = {"chart-bar": {"twostep_step2_example": "Some value"}}
    # Should not raise any exception
    validate_component_overrides(overrides2)


def test_merge_component_metadata_single_field():
    """Test merging single field override."""
    base = COMPONENT_METADATA
    overrides = {"table": {"description": "Custom table description"}}

    merged = merge_component_metadata(base, overrides)

    # Check that override was applied
    assert merged["table"]["description"] == "Custom table description"

    # Check that other fields remain unchanged
    assert (
        merged["table"]["twostep_step2_example"]
        == base["table"]["twostep_step2_example"]
    )

    # Check that other components remain unchanged
    assert merged["one-card"] == base["one-card"]

    # Ensure base was not modified
    assert base["table"]["description"] != "Custom table description"


def test_merge_component_metadata_multiple_components():
    """Test merging multiple component overrides."""
    base = COMPONENT_METADATA
    overrides = {
        "table": {"description": "Custom table description"},
        "chart-bar": {
            "chart_description": "Custom bar chart",
            "chart_rules": "Custom rules",
        },
    }

    merged = merge_component_metadata(base, overrides)

    # Check both overrides were applied
    assert merged["table"]["description"] == "Custom table description"
    assert merged["chart-bar"]["chart_description"] == "Custom bar chart"
    assert merged["chart-bar"]["chart_rules"] == "Custom rules"

    # Check unmodified fields remain
    assert (
        merged["chart-bar"]["chart_fields_spec"]
        == base["chart-bar"]["chart_fields_spec"]
    )


def test_merge_component_metadata_partial_override():
    """Test partial override preserves other fields."""
    base = COMPONENT_METADATA
    overrides = {"chart-line": {"chart_description": "Custom line chart"}}

    merged = merge_component_metadata(base, overrides)

    # Only one field should be overridden
    assert merged["chart-line"]["chart_description"] == "Custom line chart"

    # All other fields should remain unchanged
    assert merged["chart-line"]["description"] == base["chart-line"]["description"]
    assert (
        merged["chart-line"]["chart_fields_spec"]
        == base["chart-line"]["chart_fields_spec"]
    )
    assert merged["chart-line"]["chart_rules"] == base["chart-line"]["chart_rules"]
    assert (
        merged["chart-line"]["chart_inline_examples"]
        == base["chart-line"]["chart_inline_examples"]
    )


def test_merge_component_metadata_none_values_ignored():
    """Test that None values in overrides are ignored."""
    base = COMPONENT_METADATA
    overrides = {
        "table": {
            "description": "Custom description",
            "twostep_step2_example": None,  # Should be ignored
        }
    }

    merged = merge_component_metadata(base, overrides)

    # Non-None override should be applied
    assert merged["table"]["description"] == "Custom description"

    # None override should be ignored, keeping base value
    assert (
        merged["table"]["twostep_step2_example"]
        == base["table"]["twostep_step2_example"]
    )


def test_get_component_metadata_no_overrides():
    """Test get_component_metadata returns base when no overrides."""
    config = AgentConfig()

    metadata = get_component_metadata(config)

    # Should return base metadata
    assert metadata == COMPONENT_METADATA


def test_get_component_metadata_with_none_prompt():
    """Test get_component_metadata with None prompt."""
    config = AgentConfig(prompt=None)

    metadata = get_component_metadata(config)

    # Should return base metadata
    assert metadata == COMPONENT_METADATA


def test_get_component_metadata_with_none_components():
    """Test get_component_metadata with None components."""
    config = AgentConfig(prompt=AgentConfigPrompt(components=None))

    metadata = get_component_metadata(config)

    # Should return base metadata
    assert metadata == COMPONENT_METADATA


def test_get_component_metadata_with_valid_overrides():
    """Test get_component_metadata with valid overrides."""
    config = AgentConfig(
        prompt=AgentConfigPrompt(
            components={
                "table": AgentConfigPromptComponent(
                    description="Custom table description",
                    twostep_step2_rules="Custom rules",
                )
            }
        )
    )

    metadata = get_component_metadata(config)

    # Check overrides were applied
    assert metadata["table"]["description"] == "Custom table description"
    assert metadata["table"]["twostep_step2_rules"] == "Custom rules"

    # Check other fields remain
    assert (
        metadata["table"]["twostep_step2_example"]
        == COMPONENT_METADATA["table"]["twostep_step2_example"]
    )


def test_get_component_metadata_with_invalid_component():
    """Test get_component_metadata raises error for invalid component."""
    config = AgentConfig(
        prompt=AgentConfigPrompt(
            components={
                "invalid-component": AgentConfigPromptComponent(
                    description="Some description"
                )
            }
        )
    )

    with pytest.raises(ValueError) as exc_info:
        get_component_metadata(config)

    assert "Invalid component name 'invalid-component'" in str(exc_info.value)


def test_get_component_metadata_with_empty_overrides():
    """Test get_component_metadata with components that have all None fields."""
    config = AgentConfig(
        prompt=AgentConfigPrompt(
            components={"table": AgentConfigPromptComponent()}  # All fields None
        )
    )

    metadata = get_component_metadata(config)

    # Should return base metadata since all overrides are None
    assert metadata["table"] == COMPONENT_METADATA["table"]


def test_get_component_metadata_chart_components():
    """Test get_component_metadata with chart component overrides."""
    config = AgentConfig(
        prompt=AgentConfigPrompt(
            components={
                "chart-bar": AgentConfigPromptComponent(
                    description="Custom bar chart description",
                    chart_description="Custom chart type description",
                    chart_fields_spec="Custom fields spec",
                    chart_rules="Custom rules",
                    chart_inline_examples="Custom examples",
                )
            }
        )
    )

    metadata = get_component_metadata(config)

    # Check all overrides were applied
    assert metadata["chart-bar"]["description"] == "Custom bar chart description"
    assert metadata["chart-bar"]["chart_description"] == "Custom chart type description"
    assert metadata["chart-bar"]["chart_fields_spec"] == "Custom fields spec"
    assert metadata["chart-bar"]["chart_rules"] == "Custom rules"
    assert metadata["chart-bar"]["chart_inline_examples"] == "Custom examples"


def test_get_component_metadata_multiple_components():
    """Test get_component_metadata with multiple component overrides."""
    config = AgentConfig(
        prompt=AgentConfigPrompt(
            components={
                "table": AgentConfigPromptComponent(description="Custom table"),
                "chart-bar": AgentConfigPromptComponent(chart_description="Custom bar"),
                "one-card": AgentConfigPromptComponent(
                    twostep_step2_rules="Custom card rules"
                ),
            }
        )
    )

    metadata = get_component_metadata(config)

    # Check all overrides were applied
    assert metadata["table"]["description"] == "Custom table"
    assert metadata["chart-bar"]["chart_description"] == "Custom bar"
    assert metadata["one-card"]["twostep_step2_rules"] == "Custom card rules"

    # Check unmodified components remain unchanged
    assert metadata["image"] == COMPONENT_METADATA["image"]
