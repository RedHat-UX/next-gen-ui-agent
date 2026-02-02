"""Tests for custom system prompts functionality."""

import pytest
from next_gen_ui_agent import AgentConfig
from next_gen_ui_agent.types import AgentConfigPrompt

from .component_selection_llm_onestep import OnestepLLMCallComponentSelectionStrategy
from .component_selection_llm_twostep import TwostepLLMCallComponentSelectionStrategy


def test_onestep_custom_system_prompt():
    """Test that one-step strategy uses custom system prompt."""
    custom_prompt = """You are a custom assistant.

AVAILABLE UI COMPONENTS:"""

    config = AgentConfig(prompt=AgentConfigPrompt(system_prompt_onestep=custom_prompt))

    strategy = OnestepLLMCallComponentSelectionStrategy(config=config)
    system_prompt = strategy.get_system_prompt()

    # Custom prompt should be used
    assert "You are a custom assistant" in system_prompt
    # Component descriptions should still be generated
    assert "one-card" in system_prompt


def test_onestep_default_system_prompt():
    """Test that one-step strategy uses default prompt when no custom provided."""
    config = AgentConfig()

    strategy = OnestepLLMCallComponentSelectionStrategy(config=config)
    system_prompt = strategy.get_system_prompt()

    # Default prompt should be used
    assert "You are a UI design assistant" in system_prompt
    assert "RULES:" in system_prompt
    assert "JSONPATH REQUIREMENTS:" in system_prompt


def test_twostep_custom_step1_system_prompt():
    """Test that two-step strategy step1 uses custom system prompt."""
    custom_prompt = """You are a custom component selector.

AVAILABLE UI COMPONENTS:"""

    config = AgentConfig(
        prompt=AgentConfigPrompt(system_prompt_twostep_step1select=custom_prompt)
    )

    strategy = TwostepLLMCallComponentSelectionStrategy(config=config)
    system_prompt = strategy.get_system_prompt()

    # Custom prompt should be used
    assert "You are a custom component selector" in system_prompt
    # Component descriptions should still be generated
    assert "one-card" in system_prompt


def test_twostep_default_step1_system_prompt():
    """Test that two-step strategy step1 uses default prompt when no custom provided."""
    config = AgentConfig()

    strategy = TwostepLLMCallComponentSelectionStrategy(config=config)
    system_prompt = strategy.get_system_prompt()

    # Default prompt should be used
    assert "You are a UI design assistant" in system_prompt
    assert "RULES:" in system_prompt


def test_twostep_step2_validation_missing_placeholder():
    """Test that ValueError is raised when step2 prompt missing {component} placeholder."""
    custom_prompt_without_placeholder = """You are a field selector.

Select the best fields."""

    config = AgentConfig(
        prompt=AgentConfigPrompt(
            system_prompt_twostep_step2configure=custom_prompt_without_placeholder
        )
    )

    with pytest.raises(ValueError) as exc_info:
        TwostepLLMCallComponentSelectionStrategy(config=config)

    assert "{component}" in str(exc_info.value)
    assert "placeholder" in str(exc_info.value).lower()


def test_twostep_step2_validation_with_placeholder():
    """Test that no error is raised when step2 prompt contains {component} placeholder."""
    custom_prompt_with_placeholder = """You are a field selector for {component}.

Select the best fields."""

    config = AgentConfig(
        prompt=AgentConfigPrompt(
            system_prompt_twostep_step2configure=custom_prompt_with_placeholder
        )
    )

    # Should not raise an error
    strategy = TwostepLLMCallComponentSelectionStrategy(config=config)
    assert strategy is not None


def test_custom_chart_instructions_template():
    """Test that custom chart instructions template is used."""
    custom_template = """CUSTOM CHART SECTION:

Types: {chart_types}

Fields: {fields_by_type}

Rules: {chart_rules}

Examples: {examples}"""

    config = AgentConfig(
        selectable_components=["chart-bar", "chart-line"],
        prompt=AgentConfigPrompt(chart_instructions_template=custom_template),
    )

    strategy = OnestepLLMCallComponentSelectionStrategy(config=config)
    system_prompt = strategy.get_system_prompt()

    # Custom template should be used
    assert "CUSTOM CHART SECTION" in system_prompt
    # Chart components should still be generated
    assert "chart-bar" in system_prompt or "bar" in system_prompt.lower()


def test_default_chart_instructions_template():
    """Test that default chart instructions template is used when no custom provided."""
    config = AgentConfig(
        selectable_components=["chart-bar", "chart-line"],
    )

    strategy = OnestepLLMCallComponentSelectionStrategy(config=config)
    system_prompt = strategy.get_system_prompt()

    # Default template should be used
    assert "CHART TYPES" in system_prompt
    assert "FIELDS BY CHART TYPE" in system_prompt
    assert "CHART RULES" in system_prompt
    assert "CHART EXAMPLES" in system_prompt


def test_combined_custom_prompts():
    """Test using multiple custom prompts together."""
    custom_initial = """You are a financial data expert.

AVAILABLE UI COMPONENTS:"""

    custom_chart_template = """FINANCIAL CHARTS:

{chart_types}

{fields_by_type}"""

    config = AgentConfig(
        selectable_components=["table", "chart-bar"],
        prompt=AgentConfigPrompt(
            system_prompt_onestep=custom_initial,
            chart_instructions_template=custom_chart_template,
        ),
    )

    strategy = OnestepLLMCallComponentSelectionStrategy(config=config)
    system_prompt = strategy.get_system_prompt()

    # Both custom prompts should be used
    assert "You are a financial data expert" in system_prompt
    assert "FINANCIAL CHARTS" in system_prompt
    # Generated content should still be present
    assert "table" in system_prompt


def test_backward_compatibility():
    """Test that existing code without custom prompts continues to work."""
    config = AgentConfig()

    # Should work without any issues
    onestep_strategy = OnestepLLMCallComponentSelectionStrategy(config=config)
    assert onestep_strategy.get_system_prompt() is not None

    twostep_strategy = TwostepLLMCallComponentSelectionStrategy(config=config)
    assert twostep_strategy.get_system_prompt() is not None
