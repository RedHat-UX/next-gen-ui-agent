"""Tests for debug_system_prompt module."""

from next_gen_ui_agent import AgentConfig
from next_gen_ui_agent.component_selection_llm_onestep import (
    OnestepLLMCallComponentSelectionStrategy,
)
from next_gen_ui_agent.component_selection_llm_twostep import (
    TwostepLLMCallComponentSelectionStrategy,
)
from next_gen_ui_agent.types import AgentConfigDataType, AgentConfigPrompt


def test_onestep_get_debug_prompts_default_config():
    """Test get_debug_prompts() for one-step strategy with default config."""
    config = AgentConfig()
    strategy = OnestepLLMCallComponentSelectionStrategy(config=config)

    prompts = strategy.get_debug_prompts()

    assert "system_prompt" in prompts
    assert isinstance(prompts["system_prompt"], str)
    assert len(prompts["system_prompt"]) > 0
    # Should contain component descriptions
    assert "AVAILABLE UI COMPONENTS" in prompts["system_prompt"]


def test_onestep_get_debug_prompts_with_data_type():
    """Test get_debug_prompts() for one-step strategy with data_type."""
    config = AgentConfig(
        data_types={
            "test:type": AgentConfigDataType(
                data_transformer="json",
                prompt=AgentConfigPrompt(
                    system_prompt_start="Custom prompt for test:type"
                ),
            )
        }
    )
    strategy = OnestepLLMCallComponentSelectionStrategy(config=config)

    prompts = strategy.get_debug_prompts(data_type="test:type")

    assert "system_prompt" in prompts
    assert "Custom prompt for test:type" in prompts["system_prompt"]


def test_onestep_get_debug_prompts_with_custom_examples():
    """Test get_debug_prompts() with custom examples in config."""
    custom_examples = "Custom example: {component: 'table'}"
    config = AgentConfig(
        prompt=AgentConfigPrompt(examples_normalcomponents=custom_examples)
    )
    strategy = OnestepLLMCallComponentSelectionStrategy(config=config)

    prompts = strategy.get_debug_prompts()

    assert "system_prompt" in prompts
    assert custom_examples in prompts["system_prompt"]


def test_twostep_get_debug_prompts_default_config():
    """Test get_debug_prompts() for two-step strategy with default config."""
    config = AgentConfig()
    strategy = TwostepLLMCallComponentSelectionStrategy(config=config)

    prompts = strategy.get_debug_prompts()

    # Should have step1 prompt
    assert "step1_system_prompt" in prompts
    assert isinstance(prompts["step1_system_prompt"], str)
    assert len(prompts["step1_system_prompt"]) > 0
    assert "AVAILABLE UI COMPONENTS" in prompts["step1_system_prompt"]

    # Should have step2 prompts for dynamic components
    step2_keys = [k for k in prompts.keys() if k.startswith("step2_")]
    assert len(step2_keys) > 0

    # Verify step2 prompts exist for expected components
    assert "step2_system_prompt_table" in prompts
    assert "step2_system_prompt_one-card" in prompts
    assert "step2_system_prompt_chart-bar" in prompts


def test_twostep_get_debug_prompts_with_specific_component():
    """Test get_debug_prompts() for two-step strategy with specific component."""
    config = AgentConfig()
    strategy = TwostepLLMCallComponentSelectionStrategy(config=config)

    prompts = strategy.get_debug_prompts(component_for_step2="table")

    # Should have step1 prompt
    assert "step1_system_prompt" in prompts

    # Should only have step2 prompt for table
    step2_keys = [k for k in prompts.keys() if k.startswith("step2_")]
    assert len(step2_keys) == 1
    assert "step2_system_prompt_table" in prompts
    assert "{component}" not in prompts["step2_system_prompt_table"]
    assert "table" in prompts["step2_system_prompt_table"]


def test_twostep_get_debug_prompts_with_data_type():
    """Test get_debug_prompts() for two-step strategy with data_type."""
    config = AgentConfig(
        data_types={
            "test:type": AgentConfigDataType(
                data_transformer="json",
                prompt=AgentConfigPrompt(
                    twostep_step1select_system_prompt_start="Custom step1 for test:type",
                    twostep_step2configure_system_prompt_start="Custom step2 for {component} in test:type",
                ),
            )
        }
    )
    strategy = TwostepLLMCallComponentSelectionStrategy(config=config)

    prompts = strategy.get_debug_prompts(
        data_type="test:type", component_for_step2="table"
    )

    # Step1 should use custom prompt
    assert "step1_system_prompt" in prompts
    assert "Custom step1 for test:type" in prompts["step1_system_prompt"]

    # Step2 should use custom prompt with component substitution
    assert "step2_system_prompt_table" in prompts
    assert "Custom step2 for table in test:type" in prompts["step2_system_prompt_table"]


def test_twostep_step2_prompt_contains_component_rules():
    """Test that step2 prompts contain component-specific rules."""
    config = AgentConfig()
    strategy = TwostepLLMCallComponentSelectionStrategy(config=config)

    prompts = strategy.get_debug_prompts(component_for_step2="one-card")

    step2_prompt = prompts["step2_system_prompt_one-card"]
    # Should contain JSONPATH REQUIREMENTS or similar sections
    assert "JSONPATH" in step2_prompt or "data_path" in step2_prompt


def test_twostep_build_step2configure_system_prompt_method():
    """Test _build_step2configure_system_prompt() method directly."""
    config = AgentConfig()
    strategy = TwostepLLMCallComponentSelectionStrategy(config=config)

    # Get metadata
    _, metadata = strategy._resolve_allowed_components_and_metadata(data_type=None)

    # Build step2 prompt for table
    prompt = strategy._build_step2configure_system_prompt("table", metadata, None)

    assert isinstance(prompt, str)
    assert len(prompt) > 0
    assert "table" in prompt
    assert "{component}" not in prompt  # Should be substituted


def test_onestep_vs_twostep_different_prompts():
    """Test that one-step and two-step strategies produce different prompts."""
    config = AgentConfig()
    onestep_strategy = OnestepLLMCallComponentSelectionStrategy(config=config)
    twostep_strategy = TwostepLLMCallComponentSelectionStrategy(config=config)

    onestep_prompts = onestep_strategy.get_debug_prompts()
    twostep_prompts = twostep_strategy.get_debug_prompts()

    # One-step has single prompt
    assert "system_prompt" in onestep_prompts
    assert "step1_system_prompt" not in onestep_prompts

    # Two-step has step1 and step2 prompts
    assert "step1_system_prompt" in twostep_prompts
    assert "system_prompt" not in twostep_prompts


def test_debug_prompts_cache_consistency():
    """Test that debug prompts match cached prompts used at runtime."""
    config = AgentConfig()
    strategy = OnestepLLMCallComponentSelectionStrategy(config=config)

    # Get debug prompt
    debug_prompts = strategy.get_debug_prompts(data_type=None)

    # Get runtime prompt (which uses cache)
    runtime_prompt = strategy.get_system_prompt(data_type=None)

    # Should be identical
    assert debug_prompts["system_prompt"] == runtime_prompt


def test_twostep_debug_prompts_match_runtime():
    """Test that two-step debug prompts match what would be used at runtime."""
    config = AgentConfig()
    strategy = TwostepLLMCallComponentSelectionStrategy(config=config)

    # Get debug prompts
    debug_prompts = strategy.get_debug_prompts(data_type=None)

    # Get runtime step1 prompt
    runtime_step1 = strategy.get_system_prompt(data_type=None)

    # Step1 should match
    assert debug_prompts["step1_system_prompt"] == runtime_step1

    # Test step2 prompt matches the refactored method
    _, metadata = strategy._resolve_allowed_components_and_metadata(data_type=None)
    runtime_step2_table = strategy._build_step2configure_system_prompt(
        "table", metadata, None
    )

    # Should match debug output
    assert debug_prompts["step2_system_prompt_table"] == runtime_step2_table


def test_selectable_components_filtering():
    """Test that selectable_components config affects debug prompts."""
    config = AgentConfig(selectable_components={"table", "one-card"})
    strategy = TwostepLLMCallComponentSelectionStrategy(config=config)

    prompts = strategy.get_debug_prompts()

    # Should only have step2 prompts for selected components
    assert "step2_system_prompt_table" in prompts
    assert "step2_system_prompt_one-card" in prompts
    # Should not have chart prompts if not selected
    assert "step2_system_prompt_chart-bar" not in prompts


def test_component_for_step2_not_used_in_onestep():
    """Test that component_for_step2 parameter is ignored in one-step strategy."""
    config = AgentConfig()
    strategy = OnestepLLMCallComponentSelectionStrategy(config=config)

    # Should work without error even though parameter is provided
    prompts = strategy.get_debug_prompts(component_for_step2="table")

    # Should still return single system prompt
    assert "system_prompt" in prompts
    assert len(prompts) == 1
