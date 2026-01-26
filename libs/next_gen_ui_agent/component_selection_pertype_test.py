"""Tests for component_selection_pertype module."""

import pytest
from next_gen_ui_agent.component_selection_pertype import (
    init_pertype_components_mapping,
)
from next_gen_ui_agent.types import (
    AgentConfig,
    AgentConfigComponent,
    AgentConfigDataType,
    AgentConfigPromptComponent,
)


class TestInitPertypeValidation:
    """Tests for validation in init_pertype_components_mapping."""

    def test_multi_component_with_hbc_without_description_raises_error(self):
        """Test that multi-component with HBC without description raises ValueError."""
        config = AgentConfig(
            data_types={
                "test-type": AgentConfigDataType(
                    components=[
                        AgentConfigComponent(component="table"),
                        AgentConfigComponent(
                            component="custom:hbc",  # HBC without prompt
                        ),
                    ]
                )
            }
        )

        with pytest.raises(ValueError) as exc_info:
            init_pertype_components_mapping(config)

        assert "HBC 'custom:hbc'" in str(exc_info.value)
        assert "prompt.description" in str(exc_info.value)
        assert "multiple components" in str(exc_info.value)

    def test_multi_component_with_hbc_with_description_succeeds(self):
        """Test that multi-component with HBC with description succeeds."""
        config = AgentConfig(
            data_types={
                "test-type": AgentConfigDataType(
                    components=[
                        AgentConfigComponent(component="table"),
                        AgentConfigComponent(
                            component="custom:hbc",
                            prompt=AgentConfigPromptComponent(
                                description="Custom HBC description"
                            ),
                        ),
                    ]
                )
            }
        )

        # Should not raise any exception
        init_pertype_components_mapping(config)

    def test_single_hbc_without_description_succeeds(self):
        """Test that single HBC without description succeeds (no validation needed)."""
        config = AgentConfig(
            data_types={
                "test-type": AgentConfigDataType(
                    components=[
                        AgentConfigComponent(component="custom:hbc"),
                    ]
                )
            }
        )

        # Should not raise any exception (single component doesn't need LLM)
        init_pertype_components_mapping(config)

    def test_multiple_hbcs_with_descriptions_succeeds(self):
        """Test that multiple HBCs with descriptions succeeds."""
        config = AgentConfig(
            data_types={
                "test-type": AgentConfigDataType(
                    components=[
                        AgentConfigComponent(
                            component="custom:hbc1",
                            prompt=AgentConfigPromptComponent(
                                description="First HBC description"
                            ),
                        ),
                        AgentConfigComponent(
                            component="custom:hbc2",
                            prompt=AgentConfigPromptComponent(
                                description="Second HBC description"
                            ),
                        ),
                    ]
                )
            }
        )

        # Should not raise any exception
        init_pertype_components_mapping(config)

    def test_hbc_mixed_with_dynamic_components_succeeds(self):
        """Test that HBC mixed with dynamic components succeeds (restriction lifted)."""
        config = AgentConfig(
            data_types={
                "test-type": AgentConfigDataType(
                    components=[
                        AgentConfigComponent(component="table"),
                        AgentConfigComponent(
                            component="custom:hbc",
                            prompt=AgentConfigPromptComponent(
                                description="Custom HBC description"
                            ),
                        ),
                        AgentConfigComponent(component="set-of-cards"),
                    ]
                )
            }
        )

        # Should not raise any exception (mixing now allowed)
        init_pertype_components_mapping(config)

    def test_hbc_with_chart_and_twostep_fields_not_validated(self):
        """Test that chart and twostep fields in HBC prompt are accepted (not validated)."""
        config = AgentConfig(
            data_types={
                "test-type": AgentConfigDataType(
                    components=[
                        AgentConfigComponent(component="table"),
                        AgentConfigComponent(
                            component="custom:hbc",
                            prompt=AgentConfigPromptComponent(
                                description="Custom HBC description",
                                chart_description="This should be accepted",
                                chart_rules="This too",
                                twostep_step2_example="This as well",
                                twostep_step2_rules="And this",
                            ),
                        ),
                    ]
                )
            }
        )

        # Should not raise any exception - fields accepted but not used for HBC
        init_pertype_components_mapping(config)
