from next_gen_ui_agent import AgentConfig
from next_gen_ui_agent.component_selection_common import (
    CHART_COMPONENTS,
    COMPONENT_METADATA,
)

from .component_selection_llm_twostep import TwostepLLMCallComponentSelectionStrategy


class TestBuildStep1SystemPrompt:
    """Test _build_step1_system_prompt method."""

    def test_all_components_when_none(self):
        """Test that all components are included when selectable_components is None."""
        config = AgentConfig(selectable_components=None)
        strategy = TwostepLLMCallComponentSelectionStrategy(config)
        prompt = strategy._build_step1_system_prompt(None)

        # Should include all components
        for component in COMPONENT_METADATA.keys():
            assert component in prompt

        # Should include chart instructions
        assert "CHART TYPES" in prompt

        # Should include examples
        assert "Response example" in prompt

    def test_basic_components_only(self):
        """Test with only basic (non-chart) components."""
        basic_components = {"one-card", "table", "set-of-cards"}
        config = AgentConfig(selectable_components=basic_components)
        strategy = TwostepLLMCallComponentSelectionStrategy(config)
        prompt = strategy._build_step1_system_prompt(basic_components)

        # Should include selected basic components
        assert "one-card" in prompt
        assert "table" in prompt
        assert "set-of-cards" in prompt

        # Should NOT include chart components
        for chart_comp in CHART_COMPONENTS:
            assert chart_comp not in prompt

        # Should NOT include chart instructions
        assert "CHART TYPES" not in prompt

        # Should include examples for basic components
        assert "Response example" in prompt

    def test_with_chart_components(self):
        """Test with chart components included."""
        components_with_charts = {"table", "chart-bar", "chart-line"}
        config = AgentConfig(selectable_components=components_with_charts)
        strategy = TwostepLLMCallComponentSelectionStrategy(config)
        prompt = strategy._build_step1_system_prompt(components_with_charts)

        # Should include selected components
        assert "table" in prompt
        assert "chart-bar" in prompt
        assert "chart-line" in prompt

        # Should include chart instructions
        assert "CHART TYPES" in prompt
        assert "FIELDS BY CHART TYPE" in prompt

        # Should NOT include chart components that weren't selected
        assert "chart-pie" not in prompt
        assert "chart-donut" not in prompt

        # Should include examples
        assert "Response example" in prompt

    def test_with_component_metadata_overrides(self):
        """Test that component metadata overrides are applied to system prompt."""
        from next_gen_ui_agent.types import (
            AgentConfigPrompt,
            AgentConfigPromptComponent,
        )

        # Create config with overrides
        config = AgentConfig(
            prompt=AgentConfigPrompt(
                components={
                    "table": AgentConfigPromptComponent(
                        description="CUSTOM_TABLE_DESCRIPTION for twostep testing"
                    ),
                    "chart-bar": AgentConfigPromptComponent(
                        chart_description="CUSTOM_BAR_CHART_DESCRIPTION for twostep testing"
                    ),
                }
            )
        )

        # Create strategy with overrides
        strategy = TwostepLLMCallComponentSelectionStrategy(config)

        # Get the step 1 system prompt
        prompt = strategy.get_system_prompt()

        # Verify custom descriptions are in the prompt
        assert "CUSTOM_TABLE_DESCRIPTION for twostep testing" in prompt
        assert "CUSTOM_BAR_CHART_DESCRIPTION for twostep testing" in prompt

        # Verify original descriptions are NOT in the prompt
        assert COMPONENT_METADATA["table"]["description"] not in prompt
        assert COMPONENT_METADATA["chart-bar"]["chart_description"] not in prompt
