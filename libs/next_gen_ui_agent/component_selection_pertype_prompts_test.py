"""Tests for per-data-type prompt customization functionality."""

from next_gen_ui_agent import AgentConfig
from next_gen_ui_agent.types import (
    AgentConfigComponent,
    AgentConfigDataType,
    AgentConfigPrompt,
    AgentConfigPromptBase,
)

from .component_selection_llm_onestep import OnestepLLMCallComponentSelectionStrategy
from .component_selection_llm_twostep import TwostepLLMCallComponentSelectionStrategy


def test_onestep_pertype_system_prompt_override():
    """Test that data-type specific system prompt overrides global prompt in onestep strategy."""
    global_prompt = """You are a global assistant.

AVAILABLE UI COMPONENTS:"""

    datatype_prompt = """You are a data-type specific assistant.

AVAILABLE UI COMPONENTS:"""

    config = AgentConfig(
        prompt=AgentConfigPrompt(system_prompt_start=global_prompt),
        data_types={
            "test-data": AgentConfigDataType(
                prompt=AgentConfigPromptBase(system_prompt_start=datatype_prompt),
                components=[AgentConfigComponent(component="table")],
            )
        },
    )

    strategy = OnestepLLMCallComponentSelectionStrategy(config=config)

    # Get global prompt (data_type=None)
    global_system_prompt = strategy._get_or_build_system_prompt(data_type=None)
    assert "You are a global assistant" in global_system_prompt
    assert "You are a data-type specific assistant" not in global_system_prompt

    # Get data-type specific prompt
    datatype_system_prompt = strategy._get_or_build_system_prompt(data_type="test-data")
    assert "You are a data-type specific assistant" in datatype_system_prompt
    assert "You are a global assistant" not in datatype_system_prompt


def test_onestep_pertype_precedence_over_global():
    """Test precedence: data-type > global > default for onestep strategy."""
    config = AgentConfig(
        prompt=AgentConfigPrompt(
            system_prompt_start="Global prompt\n\nAVAILABLE UI COMPONENTS:"
        ),
        data_types={
            "with-override": AgentConfigDataType(
                prompt=AgentConfigPromptBase(
                    system_prompt_start="Data-type prompt\n\nAVAILABLE UI COMPONENTS:"
                ),
                components=[AgentConfigComponent(component="table")],
            ),
            "without-override": AgentConfigDataType(
                components=[AgentConfigComponent(component="table")]
            ),
        },
    )

    strategy = OnestepLLMCallComponentSelectionStrategy(config=config)

    # Data-type with override should use data-type prompt
    with_override_prompt = strategy._get_or_build_system_prompt(
        data_type="with-override"
    )
    assert "Data-type prompt" in with_override_prompt
    assert "Global prompt" not in with_override_prompt

    # Data-type without override should use global prompt
    without_override_prompt = strategy._get_or_build_system_prompt(
        data_type="without-override"
    )
    assert "Global prompt" in without_override_prompt
    assert "Data-type prompt" not in without_override_prompt

    # No data-type should use global prompt
    global_prompt = strategy._get_or_build_system_prompt(data_type=None)
    assert "Global prompt" in global_prompt


def test_onestep_pertype_examples_override():
    """Test that data-type specific examples override global examples in onestep strategy."""
    global_examples = """Global example for table:
{"component": "table", "title": "Global"}"""

    datatype_examples = """Data-type specific example for table:
{"component": "table", "title": "DataType"}"""

    config = AgentConfig(
        prompt=AgentConfigPrompt(examples_normalcomponents=global_examples),
        data_types={
            "test-data": AgentConfigDataType(
                prompt=AgentConfigPromptBase(
                    examples_normalcomponents=datatype_examples
                ),
                components=[AgentConfigComponent(component="table")],
            )
        },
    )

    strategy = OnestepLLMCallComponentSelectionStrategy(config=config)

    # Global prompt should use global examples
    global_prompt = strategy._get_or_build_system_prompt(data_type=None)
    assert "Global example for table" in global_prompt
    assert "Data-type specific example" not in global_prompt

    # Data-type prompt should use data-type examples
    datatype_prompt = strategy._get_or_build_system_prompt(data_type="test-data")
    assert "Data-type specific example" in datatype_prompt
    assert "Global example for table" not in datatype_prompt


def test_onestep_pertype_chart_instructions_override():
    """Test that data-type specific chart instructions override global in onestep strategy."""
    global_chart_template = "GLOBAL CHART INSTRUCTIONS\n{charts_description}"
    datatype_chart_template = "DATATYPE CHART INSTRUCTIONS\n{charts_description}"

    config = AgentConfig(
        prompt=AgentConfigPrompt(chart_instructions_template=global_chart_template),
        data_types={
            "test-data": AgentConfigDataType(
                prompt=AgentConfigPromptBase(
                    chart_instructions_template=datatype_chart_template
                ),
                components=[AgentConfigComponent(component="chart-bar")],
            )
        },
    )

    strategy = OnestepLLMCallComponentSelectionStrategy(config=config)

    # Global prompt should use global chart template
    global_prompt = strategy._get_or_build_system_prompt(data_type=None)
    assert "GLOBAL CHART INSTRUCTIONS" in global_prompt

    # Data-type prompt should use data-type chart template
    datatype_prompt = strategy._get_or_build_system_prompt(data_type="test-data")
    assert "DATATYPE CHART INSTRUCTIONS" in datatype_prompt
    assert "GLOBAL CHART INSTRUCTIONS" not in datatype_prompt


def test_twostep_pertype_step1_system_prompt_override():
    """Test that data-type specific step1 prompt overrides global in twostep strategy."""
    global_prompt = """You are a global step1 assistant.

AVAILABLE UI COMPONENTS:"""

    datatype_prompt = """You are a data-type specific step1 assistant.

AVAILABLE UI COMPONENTS:"""

    config = AgentConfig(
        prompt=AgentConfigPrompt(twostep_step1select_system_prompt_start=global_prompt),
        data_types={
            "test-data": AgentConfigDataType(
                prompt=AgentConfigPromptBase(
                    twostep_step1select_system_prompt_start=datatype_prompt
                ),
                components=[AgentConfigComponent(component="table")],
            )
        },
    )

    strategy = TwostepLLMCallComponentSelectionStrategy(config=config)

    # Global prompt
    global_system_prompt = strategy._get_or_build_step1select_system_prompt(
        data_type=None
    )
    assert "You are a global step1 assistant" in global_system_prompt

    # Data-type specific prompt
    datatype_system_prompt = strategy._get_or_build_step1select_system_prompt(
        data_type="test-data"
    )
    assert "You are a data-type specific step1 assistant" in datatype_system_prompt
    assert "You are a global step1 assistant" not in datatype_system_prompt


def test_twostep_pertype_step1_examples_override():
    """Test that data-type specific step1 examples override global in twostep strategy."""
    global_examples = """Global step1 example:
{"component": "table", "title": "Global"}"""

    datatype_examples = """Data-type step1 example:
{"component": "table", "title": "DataType"}"""

    config = AgentConfig(
        prompt=AgentConfigPrompt(
            twostep_step1select_examples_normalcomponents=global_examples
        ),
        data_types={
            "test-data": AgentConfigDataType(
                prompt=AgentConfigPromptBase(
                    twostep_step1select_examples_normalcomponents=datatype_examples
                ),
                components=[AgentConfigComponent(component="table")],
            )
        },
    )

    strategy = TwostepLLMCallComponentSelectionStrategy(config=config)

    # Global prompt should use global examples
    global_prompt = strategy._get_or_build_step1select_system_prompt(data_type=None)
    assert "Global step1 example" in global_prompt

    # Data-type prompt should use data-type examples
    datatype_prompt = strategy._get_or_build_step1select_system_prompt(
        data_type="test-data"
    )
    assert "Data-type step1 example" in datatype_prompt
    assert "Global step1 example" not in datatype_prompt


def test_twostep_pertype_chart_examples_override():
    """Test that data-type specific chart examples override global in twostep strategy."""
    global_chart_examples = """Global chart example:
{"component": "chart-bar", "title": "Global"}"""

    datatype_chart_examples = """Data-type chart example:
{"component": "chart-bar", "title": "DataType"}"""

    config = AgentConfig(
        prompt=AgentConfigPrompt(
            twostep_step1select_examples_charts=global_chart_examples
        ),
        data_types={
            "test-data": AgentConfigDataType(
                prompt=AgentConfigPromptBase(
                    twostep_step1select_examples_charts=datatype_chart_examples
                ),
                components=[AgentConfigComponent(component="chart-bar")],
            )
        },
    )

    strategy = TwostepLLMCallComponentSelectionStrategy(config=config)

    # Global prompt should use global chart examples
    global_prompt = strategy._get_or_build_step1select_system_prompt(data_type=None)
    assert "Global chart example" in global_prompt

    # Data-type prompt should use data-type chart examples
    datatype_prompt = strategy._get_or_build_step1select_system_prompt(
        data_type="test-data"
    )
    assert "Data-type chart example" in datatype_prompt
    assert "Global chart example" not in datatype_prompt


def test_onestep_pertype_caching_isolation():
    """Test that caching correctly isolates prompts for different data types in onestep."""
    config = AgentConfig(
        data_types={
            "type-a": AgentConfigDataType(
                prompt=AgentConfigPromptBase(
                    system_prompt_start="Type A prompt\n\nAVAILABLE UI COMPONENTS:"
                ),
                components=[AgentConfigComponent(component="table")],
            ),
            "type-b": AgentConfigDataType(
                prompt=AgentConfigPromptBase(
                    system_prompt_start="Type B prompt\n\nAVAILABLE UI COMPONENTS:"
                ),
                components=[AgentConfigComponent(component="one-card")],
            ),
        }
    )

    strategy = OnestepLLMCallComponentSelectionStrategy(config=config)

    # Build prompts for different types
    prompt_a1 = strategy._get_or_build_system_prompt(data_type="type-a")
    prompt_b1 = strategy._get_or_build_system_prompt(data_type="type-b")
    prompt_a2 = strategy._get_or_build_system_prompt(data_type="type-a")

    # Verify correct content
    assert "Type A prompt" in prompt_a1
    assert "Type B prompt" in prompt_b1
    assert "Type A prompt" in prompt_a2

    # Verify isolation (type-a should not have type-b content)
    assert "Type B prompt" not in prompt_a1
    assert "Type A prompt" not in prompt_b1

    # Verify caching (same instance for same data_type)
    assert prompt_a1 is prompt_a2


def test_twostep_pertype_caching_isolation():
    """Test that caching correctly isolates prompts for different data types in twostep."""
    config = AgentConfig(
        data_types={
            "type-a": AgentConfigDataType(
                prompt=AgentConfigPromptBase(
                    twostep_step1select_system_prompt_start="Type A prompt\n\nAVAILABLE UI COMPONENTS:"
                ),
                components=[AgentConfigComponent(component="table")],
            ),
            "type-b": AgentConfigDataType(
                prompt=AgentConfigPromptBase(
                    twostep_step1select_system_prompt_start="Type B prompt\n\nAVAILABLE UI COMPONENTS:"
                ),
                components=[AgentConfigComponent(component="one-card")],
            ),
        }
    )

    strategy = TwostepLLMCallComponentSelectionStrategy(config=config)

    # Build prompts for different types
    prompt_a1 = strategy._get_or_build_step1select_system_prompt(data_type="type-a")
    prompt_b1 = strategy._get_or_build_step1select_system_prompt(data_type="type-b")
    prompt_a2 = strategy._get_or_build_step1select_system_prompt(data_type="type-a")

    # Verify correct content
    assert "Type A prompt" in prompt_a1
    assert "Type B prompt" in prompt_b1
    assert "Type A prompt" in prompt_a2

    # Verify isolation
    assert "Type B prompt" not in prompt_a1
    assert "Type A prompt" not in prompt_b1

    # Verify caching
    assert prompt_a1 is prompt_a2


def test_onestep_pertype_all_fields_override():
    """Test that all AgentConfigPromptBase fields can be overridden at data-type level for onestep."""
    config = AgentConfig(
        prompt=AgentConfigPrompt(
            system_prompt_start="Global start\n\nAVAILABLE UI COMPONENTS:",
            chart_instructions_template="Global chart: {charts_description}",
            examples_normalcomponents="Global normal examples",
            examples_charts="Global chart examples",
        ),
        data_types={
            "test-data": AgentConfigDataType(
                prompt=AgentConfigPromptBase(
                    system_prompt_start="DataType start\n\nAVAILABLE UI COMPONENTS:",
                    chart_instructions_template="DataType chart: {charts_description}",
                    examples_normalcomponents="DataType normal examples",
                    examples_charts="DataType chart examples",
                ),
                components=[
                    AgentConfigComponent(component="table"),
                    AgentConfigComponent(component="chart-bar"),
                ],
            )
        },
    )

    strategy = OnestepLLMCallComponentSelectionStrategy(config=config)

    datatype_prompt = strategy._get_or_build_system_prompt(data_type="test-data")

    # All data-type fields should be present
    assert "DataType start" in datatype_prompt
    assert "DataType chart:" in datatype_prompt
    assert "DataType normal examples" in datatype_prompt
    assert "DataType chart examples" in datatype_prompt

    # Global fields should not be present
    assert "Global start" not in datatype_prompt
    assert "Global chart:" not in datatype_prompt
    assert "Global normal examples" not in datatype_prompt
    assert "Global chart examples" not in datatype_prompt


def test_twostep_pertype_all_step1_fields_override():
    """Test that all step1 fields can be overridden at data-type level for twostep."""
    config = AgentConfig(
        prompt=AgentConfigPrompt(
            twostep_step1select_system_prompt_start="Global start\n\nAVAILABLE UI COMPONENTS:",
            chart_instructions_template="Global chart: {charts_description}",
            twostep_step1select_examples_normalcomponents="Global normal examples",
            twostep_step1select_examples_charts="Global chart examples",
        ),
        data_types={
            "test-data": AgentConfigDataType(
                prompt=AgentConfigPromptBase(
                    twostep_step1select_system_prompt_start="DataType start\n\nAVAILABLE UI COMPONENTS:",
                    chart_instructions_template="DataType chart: {charts_description}",
                    twostep_step1select_examples_normalcomponents="DataType normal examples",
                    twostep_step1select_examples_charts="DataType chart examples",
                ),
                components=[
                    AgentConfigComponent(component="table"),
                    AgentConfigComponent(component="chart-bar"),
                ],
            )
        },
    )

    strategy = TwostepLLMCallComponentSelectionStrategy(config=config)

    datatype_prompt = strategy._get_or_build_step1select_system_prompt(
        data_type="test-data"
    )

    # All data-type fields should be present
    assert "DataType start" in datatype_prompt
    assert "DataType chart:" in datatype_prompt
    assert "DataType normal examples" in datatype_prompt
    assert "DataType chart examples" in datatype_prompt

    # Global fields should not be present
    assert "Global start" not in datatype_prompt
    assert "Global chart:" not in datatype_prompt
    assert "Global normal examples" not in datatype_prompt
    assert "Global chart examples" not in datatype_prompt


def test_pertype_fallback_to_default():
    """Test that default prompts are used when neither global nor data-type prompts are provided."""
    config = AgentConfig(
        data_types={
            "test-data": AgentConfigDataType(
                components=[AgentConfigComponent(component="table")]
            )
        }
    )

    strategy = OnestepLLMCallComponentSelectionStrategy(config=config)

    datatype_prompt = strategy._get_or_build_system_prompt(data_type="test-data")

    # Should contain default prompt content
    assert "You are a UI design assistant" in datatype_prompt
    assert "RULES:" in datatype_prompt
    assert "JSONPATH REQUIREMENTS:" in datatype_prompt
