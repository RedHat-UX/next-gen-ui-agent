"""Tests for configurable examples templates."""

from next_gen_ui_agent import AgentConfig
from next_gen_ui_agent.types import AgentConfigPrompt

from .component_selection_llm_onestep import OnestepLLMCallComponentSelectionStrategy
from .component_selection_llm_twostep import TwostepLLMCallComponentSelectionStrategy


class TestOnestepExamples:
    """Test one-step strategy examples customization."""

    def test_default_examples_all_components(self):
        """Test default examples when all components allowed."""
        config = AgentConfig()
        strategy = OnestepLLMCallComponentSelectionStrategy(config=config)
        system_prompt = strategy.get_system_prompt()

        # Should include both normal and chart examples
        assert "table" in system_prompt
        assert "one-card" in system_prompt
        assert "chart-bar" in system_prompt
        assert "chart-mirrored-bar" in system_prompt

    def test_default_examples_only_normalcomponents(self):
        """Test default examples with only normal components."""
        config = AgentConfig(selectable_components=["table", "one-card"])
        strategy = OnestepLLMCallComponentSelectionStrategy(config=config)
        system_prompt = strategy.get_system_prompt()

        # Should include only normal component examples
        assert "table" in system_prompt
        assert "one-card" in system_prompt
        assert "chart-bar" not in system_prompt

    def test_default_examples_only_charts(self):
        """Test default examples with only chart components."""
        config = AgentConfig(selectable_components=["chart-bar", "chart-line"])
        strategy = OnestepLLMCallComponentSelectionStrategy(config=config)
        system_prompt = strategy.get_system_prompt()

        # Should include only chart examples
        assert "chart-bar" in system_prompt
        # Check that table/one-card examples are not included (not just the word in rules)
        assert '"component": "table"' not in system_prompt
        assert '"component": "one-card"' not in system_prompt
        assert "Orders" not in system_prompt  # From table example
        assert "Order CA565" not in system_prompt  # From one-card example

    def test_custom_normalcomponents_examples(self):
        """Test custom normal component examples."""
        custom_normalcomponents = """Custom table example:
{
    "component": "table",
    "title": "Custom Table"
}"""

        config = AgentConfig(
            prompt=AgentConfigPrompt(
                examples_onestep_normalcomponents=custom_normalcomponents
            )
        )
        strategy = OnestepLLMCallComponentSelectionStrategy(config=config)
        system_prompt = strategy.get_system_prompt()

        # Should use custom normal component examples
        assert "Custom table example" in system_prompt
        assert "Custom Table" in system_prompt

    def test_custom_chart_examples(self):
        """Test custom chart examples."""
        custom_chart = """Custom chart example:
{
    "component": "chart-bar",
    "title": "Custom Chart"
}"""

        config = AgentConfig(
            selectable_components=["chart-bar"],
            prompt=AgentConfigPrompt(examples_onestep_charts=custom_chart),
        )
        strategy = OnestepLLMCallComponentSelectionStrategy(config=config)
        system_prompt = strategy.get_system_prompt()

        # Should use custom chart examples
        assert "Custom chart example" in system_prompt
        assert "Custom Chart" in system_prompt

    def test_combined_custom_examples(self):
        """Test using both custom normalcomponents and charts examples together."""
        custom_normalcomponents = """Custom normal example:
{
    "component": "table",
    "title": "Custom Table"
}"""

        custom_charts = """Custom chart example:
{
    "component": "chart-bar",
    "title": "Custom Chart"
}"""

        config = AgentConfig(
            prompt=AgentConfigPrompt(
                examples_onestep_normalcomponents=custom_normalcomponents,
                examples_onestep_charts=custom_charts,
            )
        )
        strategy = OnestepLLMCallComponentSelectionStrategy(config=config)
        system_prompt = strategy.get_system_prompt()

        # Should use both custom examples
        assert "Custom normal example" in system_prompt
        assert "Custom Table" in system_prompt
        assert "Custom chart example" in system_prompt
        assert "Custom Chart" in system_prompt


class TestTwostepStep1Examples:
    """Test two-step step1 examples customization."""

    def test_default_examples_all_components(self):
        """Test default examples when all components allowed."""
        config = AgentConfig()
        strategy = TwostepLLMCallComponentSelectionStrategy(config=config)
        system_prompt = strategy.get_system_prompt()

        # Should include both normal and chart examples
        assert "table" in system_prompt
        assert "one-card" in system_prompt
        assert "image" in system_prompt
        assert "chart-bar" in system_prompt

    def test_custom_normalcomponents_examples(self):
        """Test custom normal component examples for step1."""
        custom_normalcomponents = """Custom step1 example:
{
    "component": "table",
    "title": "Custom Step1 Table"
}"""

        config = AgentConfig(
            prompt=AgentConfigPrompt(
                examples_twostep_step1select_normalcomponents=custom_normalcomponents
            )
        )
        strategy = TwostepLLMCallComponentSelectionStrategy(config=config)
        system_prompt = strategy.get_system_prompt()

        # Should use custom examples
        assert "Custom step1 example" in system_prompt
        assert "Custom Step1 Table" in system_prompt

    def test_custom_chart_examples(self):
        """Test custom chart examples for step1."""
        custom_chart = """Custom step1 chart:
{
    "component": "chart-line",
    "title": "Custom Chart"
}"""

        config = AgentConfig(
            selectable_components=["chart-line"],
            prompt=AgentConfigPrompt(examples_twostep_step1select_charts=custom_chart),
        )
        strategy = TwostepLLMCallComponentSelectionStrategy(config=config)
        system_prompt = strategy.get_system_prompt()

        # Should use custom chart examples
        assert "Custom step1 chart" in system_prompt

    def test_combined_custom_examples(self):
        """Test using both custom normalcomponents and charts examples together."""
        custom_normalcomponents = """Custom step1 normal:
{
    "component": "table",
    "title": "Custom Table"
}"""

        custom_charts = """Custom step1 chart:
{
    "component": "chart-line",
    "title": "Custom Chart"
}"""

        config = AgentConfig(
            prompt=AgentConfigPrompt(
                examples_twostep_step1select_normalcomponents=custom_normalcomponents,
                examples_twostep_step1select_charts=custom_charts,
            )
        )
        strategy = TwostepLLMCallComponentSelectionStrategy(config=config)
        system_prompt = strategy.get_system_prompt()

        # Should use both custom examples
        assert "Custom step1 normal" in system_prompt
        assert "Custom step1 chart" in system_prompt


class TestBackwardCompatibility:
    """Test backward compatibility."""

    def test_no_custom_examples_works(self):
        """Test that existing code without custom examples continues to work."""
        config = AgentConfig()

        onestep = OnestepLLMCallComponentSelectionStrategy(config=config)
        assert onestep.get_system_prompt() is not None

        twostep = TwostepLLMCallComponentSelectionStrategy(config=config)
        assert twostep.get_system_prompt() is not None
