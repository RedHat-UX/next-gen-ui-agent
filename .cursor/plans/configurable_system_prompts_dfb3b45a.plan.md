---
name: Configurable System Prompts
overview: Add configuration fields to `AgentConfigPrompt` that allow overriding the initial parts of system prompts for both one-step and two-step strategies (step1 and step2), while keeping the dynamically generated sections (component descriptions, examples) unchanged.
todos:
  - id: update_types
    content: Add system_prompt_* fields to AgentConfigPrompt in types.py
    status: completed
  - id: update_chart_instructions
    content: Add template parameter to build_chart_instructions() in component_selection_common.py
    status: completed
  - id: update_onestep
    content: Modify _build_system_prompt() in component_selection_llm_onestep.py to use config overrides
    status: completed
  - id: update_twostep_step1
    content: Modify _build_step1select_system_prompt() in component_selection_llm_twostep.py to use config override
    status: completed
  - id: validate_step2_placeholder
    content: Add validation in TwostepLLMCallComponentSelectionStrategy.__init__() to check {component} placeholder
    status: completed
  - id: update_twostep_step2
    content: Modify inference_step2configure() in component_selection_llm_twostep.py to use config override
    status: completed
  - id: add_tests
    content: Create comprehensive tests for custom system prompts
    status: completed
  - id: update_docs_configuration
    content: Add basic reference description of new prompt fields to configuration.md
    status: completed
  - id: update_docs_llm
    content: Add detailed prompt tuning chapter to llm.md
    status: completed
  - id: run_tests
    content: Run test suite and verify all tests pass
    status: completed
isProject: false
---

# Configurable System Prompts for Component Selection

## Overview

This feature allows users to override the initial (common) parts of system prompts for both one-step and two-step component selection strategies through the agent configuration file. This enables domain-specific customization of LLM behavior while keeping the dynamically generated portions (component descriptions, chart instructions, examples) unchanged.

## Motivation

Different use cases and domains may benefit from customized instructions to the LLM:

- Financial applications may need specific terminology and rules
- Medical applications may require HIPAA-compliant language
- Different organizations may have style preferences
- Testing and experimentation with prompt variations

## Architecture

### Current System Prompt Structure

System prompts have two main parts:

1. **Initial Section** (now configurable):
  - General instructions and rules
  - JSON requirements
  - JSONPath requirements
  - "AVAILABLE UI COMPONENTS:" heading
2. **Dynamic Section** (generated per-request):
  - Component descriptions
  - Chart-specific instructions
  - Response examples

### Configuration Points

The feature adds four main configuration points:

1. `system_prompt_onestep` - Initial prompt for one-step strategy
2. `system_prompt_twostep_step1select` - Initial prompt for two-step step1 (component selection)
3. `system_prompt_twostep_step2configure` - Initial prompt for two-step step2 (field configuration) - must contain `{component}` placeholder
4. `chart_instructions_template` - Template for chart-specific instructions with placeholders

## Implementation Plan

### 1. Update Type Definitions

**File:** `libs/next_gen_ui_agent/types.py`

Add four new optional fields to `AgentConfigPrompt` class:

```python
class AgentConfigPrompt(BaseModel):
    # ... existing fields ...
    
    system_prompt_onestep: Optional[str] = Field(
        default=None,
        description="Override the initial system prompt section for one-step strategy (including 'AVAILABLE UI COMPONENTS:' heading, before component descriptions and other per-component dynamically generated parts). If not set, uses default hardcoded prompt.",
    )
    """Override the initial system prompt section for one-step strategy."""

    system_prompt_twostep_step1select: Optional[str] = Field(
        default=None,
        description="Override the initial system prompt section for two-step strategy step1 (component selection, including 'AVAILABLE UI COMPONENTS:' heading, before component descriptions and other per-component dynamically generated parts). If not set, uses default hardcoded prompt.",
    )
    """Override the initial system prompt section for two-step strategy step1 (component selection)."""

    system_prompt_twostep_step2configure: Optional[str] = Field(
        default=None,
        description="Override the initial system prompt section for two-step strategy step2 (field configuration, before component-specific rules). MUST contain `{component}` placeholder which will be replaced with the selected component name. If not set, uses default hardcoded prompt.",
    )
    """Override the initial system prompt section for two-step strategy step2 (field configuration). Must contain {component} placeholder."""

    chart_instructions_template: Optional[str] = Field(
        default=None,
        description="Override the chart instructions template used in both strategies. Supports placeholders: {chart_types}, {fields_by_type}, {chart_rules}, {examples} which will be replaced with dynamically generated component-specific content. If not set, uses default hardcoded template (which includes common rule: '- Don\\'t add unrequested metrics').",
    )
    """Override the chart instructions template used in both strategies."""
```

### 2. Update Chart Instructions Builder

**File:** `libs/next_gen_ui_agent/component_selection_common.py`

Modify `build_chart_instructions()` to accept an optional template parameter:

```python
def build_chart_instructions(
    allowed_chart_components: set[str],
    metadata: dict,
    template: str | None = None,
) -> str:
    """
    Build chart instructions section for system prompt.
    
    Args:
        allowed_chart_components: Set of allowed chart component names
        metadata: Component metadata dictionary
        template: Optional template string with placeholders. If None, uses default template.
    
    Returns:
        Formatted string with chart instructions
    """
    if not allowed_chart_components:
        return ""
    
    # Build dynamic content
    chart_types = build_chart_types_description(allowed_chart_components, metadata)
    fields_by_type = build_chart_fields_description(allowed_chart_components, metadata)
    chart_rules = build_chart_rules(allowed_chart_components, metadata)
    examples = build_chart_examples(allowed_chart_components, metadata)
    
    # Use custom template or default
    if template:
        return template.format(
            chart_types=chart_types,
            fields_by_type=fields_by_type,
            chart_rules=chart_rules,
            examples=examples,
        )
    
    # Default template (includes common rule: "- Don't add unrequested metrics")
    return f"""CHART TYPES (count ONLY metrics user requests):
{chart_types}

FIELDS BY CHART TYPE:
{fields_by_type}

CHART RULES:
- Don't add unrequested metrics
{chart_rules}

CHART EXAMPLES:
{examples}"""
```

### 3. Update One-Step Strategy

**File:** `libs/next_gen_ui_agent/component_selection_llm_onestep.py`

Modify `_build_system_prompt()` to check for custom initial section:

```python
def _build_system_prompt(
    self, allowed_components: set[str], metadata: dict
) -> str:
    """Build system prompt for one-step strategy."""
    
    # Check for custom initial section
    if (
        self.config.prompt
        and self.config.prompt.system_prompt_onestep
    ):
        initial_section = self.config.prompt.system_prompt_onestep
    else:
        # Default initial section
        initial_section = """You are a UI design assistant. Select the best UI component to visualize the Data based on User query.

RULES:
- Generate JSON only
- If user explicitly requests a component type ("table", "chart", "cards"), USE IT if present in the list of AVAILABLE UI COMPONENTS, unless data structure prevents it
- Select one component into "component" field. It MUST BE named in the AVAILABLE UI COMPONENTS!
- Provide "title", "reasonForTheComponentSelection", "confidenceScore" (percentage)
- Select relevant Data fields based on User query
- Each field must have "name" and "data_path"
- Do not use formatting or calculations in "data_path"

JSONPATH REQUIREMENTS:
- Analyze actual Data structure carefully
- If fields are nested (e.g., items[*].movie.title), include full path
- Do NOT skip intermediate objects
- Use [*] for array access

AVAILABLE UI COMPONENTS:"""
    
    # Build components description
    components_description = build_components_description(allowed_components, metadata)
    
    # Build chart instructions with optional template
    chart_instructions = build_chart_instructions(
        allowed_charts,
        metadata,
        self.config.prompt.chart_instructions_template
        if self.config.prompt
        else None,
    )
    
    # Combine sections
    system_prompt = f"""{initial_section}
{components_description}

{chart_instructions}"""
    
    # Add examples
    response_examples = build_onestep_examples(allowed_components)
    if response_examples:
        system_prompt += f"""

{response_examples}"""
    
    return system_prompt
```

### 4. Update Two-Step Strategy - Step1

**File:** `libs/next_gen_ui_agent/component_selection_llm_twostep.py`

Modify `_build_step1select_system_prompt()` to check for custom initial section:

```python
def _build_step1select_system_prompt(
    self, allowed_components: set[str], metadata: dict
) -> str:
    """Build system prompt for step1 (component selection)."""
    
    # Check for custom initial section
    if (
        self.config.prompt
        and self.config.prompt.system_prompt_twostep_step1select
    ):
        initial_section = self.config.prompt.system_prompt_twostep_step1select
    else:
        # Default initial section
        initial_section = """You are a UI design assistant. Select the best UI component to visualize the Data based on User query.

RULES:
- Generate JSON only
- Select one component into "component" field. It MUST BE named in the AVAILABLE UI COMPONENTS!
- Provide "title", "reasonForTheComponentSelection", "confidenceScore" (percentage)
- If user explicitly requests a component type ("table", "chart", "cards"), USE IT if present in the list of AVAILABLE UI COMPONENTS, unless data structure prevents it

AVAILABLE UI COMPONENTS:"""
    
    # Build dynamic sections
    components_description = build_components_description(allowed_components, metadata)
    chart_instructions = build_chart_instructions(
        allowed_charts,
        metadata,
        self.config.prompt.chart_instructions_template
        if self.config.prompt
        else None,
    )
    
    system_prompt = f"""{initial_section}
{components_description}

{chart_instructions}"""
    
    # Add examples
    response_examples = build_twostep_step1select_examples(allowed_components)
    if response_examples:
        system_prompt += f"""

{response_examples}"""
    
    return system_prompt
```

### 5. Update Two-Step Strategy - Step2

**File:** `libs/next_gen_ui_agent/component_selection_llm_twostep.py`

#### 5.1 Add Validation in `__init__()`

```python
def __init__(self, config: AgentConfig):
    """Initialize two-step strategy with validation."""
    super().__init__(config)
    
    # Validate that step2 custom prompt contains {component} placeholder if provided
    if (
        config.prompt
        and config.prompt.system_prompt_twostep_step2configure
        and "{component}" not in config.prompt.system_prompt_twostep_step2configure
    ):
        raise ValueError(
            "system_prompt_twostep_step2configure must contain {component} placeholder"
        )
```

#### 5.2 Modify `inference_step2configure()`

```python
def inference_step2configure(
    self, component: str, input_data: dict, user_query: str, metadata: dict
) -> InferenceResult:
    """Run step2 inference to configure fields for selected component."""
    
    # Check for custom initial section
    if (
        self.config.prompt
        and self.config.prompt.system_prompt_twostep_step2configure
    ):
        initial_section = self.config.prompt.system_prompt_twostep_step2configure.format(
            component=component
        )
    else:
        # Default initial section
        initial_section = f"""Configure the fields for the {component} component to visualize the Data based on User query.

RULES:
- Generate JSON only
- Provide "title" and "fields"
- Each field must have "name" and "data_path"
- Do not use formatting or calculations in "data_path"

JSONPATH REQUIREMENTS:
- Analyze actual Data structure carefully
- If fields are nested (e.g., items[*].movie.title), include full path
- Do NOT skip intermediate objects
- Use [*] for array access"""
    
    # Build remaining prompt sections
    component_rules = build_twostep_step2configure_rules(component, metadata)
    component_example = build_twostep_step2configure_example(component, metadata)
    
    system_prompt = f"""{initial_section}

{component_rules}

{component_example}"""
    
    # Continue with inference...
```

### 6. Create Comprehensive Tests

**File:** `libs/next_gen_ui_agent/component_selection_custom_prompts_test.py`

Create test file with coverage for:

- Custom one-step prompt
- Custom two-step step1 prompt
- Custom two-step step2 prompt (with `{component}` placeholder)
- Custom chart instructions template
- Combined custom prompts
- Validation of `{component}` placeholder
- Backward compatibility (defaults)

```python
"""Tests for configurable custom system prompts."""

import pytest
from next_gen_ui_agent import AgentConfig
from next_gen_ui_agent.types import AgentConfigPrompt

from .component_selection_llm_onestep import OnestepLLMCallComponentSelectionStrategy
from .component_selection_llm_twostep import TwostepLLMCallComponentSelectionStrategy


class TestOnestepCustomPrompt:
    """Test one-step strategy custom prompt."""
    
    def test_custom_system_prompt(self):
        """Test custom initial system prompt for one-step strategy."""
        custom_prompt = """CUSTOM INITIAL PROMPT
AVAILABLE UI COMPONENTS:"""
        
        config = AgentConfig(
            prompt=AgentConfigPrompt(system_prompt_onestep=custom_prompt)
        )
        strategy = OnestepLLMCallComponentSelectionStrategy(config=config)
        system_prompt = strategy.get_system_prompt()
        
        assert "CUSTOM INITIAL PROMPT" in system_prompt
        assert "AVAILABLE UI COMPONENTS:" in system_prompt


class TestTwostepCustomPrompts:
    """Test two-step strategy custom prompts."""
    
    def test_custom_step1_prompt(self):
        """Test custom step1 prompt."""
        custom_prompt = """CUSTOM STEP1 PROMPT
AVAILABLE UI COMPONENTS:"""
        
        config = AgentConfig(
            prompt=AgentConfigPrompt(
                system_prompt_twostep_step1select=custom_prompt
            )
        )
        strategy = TwostepLLMCallComponentSelectionStrategy(config=config)
        system_prompt = strategy.get_system_prompt()
        
        assert "CUSTOM STEP1 PROMPT" in system_prompt
    
    def test_custom_step2_prompt_with_placeholder(self):
        """Test custom step2 prompt with {component} placeholder."""
        custom_prompt = """Configure fields for {component} component.
RULES:
- Custom rule 1"""
        
        config = AgentConfig(
            prompt=AgentConfigPrompt(
                system_prompt_twostep_step2configure=custom_prompt
            )
        )
        strategy = TwostepLLMCallComponentSelectionStrategy(config=config)
        
        # Should not raise validation error
        assert strategy is not None
    
    def test_step2_prompt_missing_placeholder_raises_error(self):
        """Test that step2 prompt without {component} raises ValueError."""
        custom_prompt = """Configure fields for component.
RULES:
- Missing placeholder"""
        
        with pytest.raises(ValueError, match="must contain {component} placeholder"):
            config = AgentConfig(
                prompt=AgentConfigPrompt(
                    system_prompt_twostep_step2configure=custom_prompt
                )
            )
            TwostepLLMCallComponentSelectionStrategy(config=config)


class TestChartInstructionsTemplate:
    """Test custom chart instructions template."""
    
    def test_custom_chart_instructions(self):
        """Test custom chart instructions template."""
        custom_template = """CUSTOM CHART SECTION
Types: {chart_types}
Fields: {fields_by_type}
Rules: {chart_rules}
Examples: {examples}"""
        
        config = AgentConfig(
            selectable_components=["chart-bar"],
            prompt=AgentConfigPrompt(
                chart_instructions_template=custom_template
            ),
        )
        strategy = OnestepLLMCallComponentSelectionStrategy(config=config)
        system_prompt = strategy.get_system_prompt()
        
        assert "CUSTOM CHART SECTION" in system_prompt
        assert "Types:" in system_prompt
        assert "Fields:" in system_prompt


class TestBackwardCompatibility:
    """Test that existing code without custom prompts still works."""
    
    def test_default_prompts_work(self):
        """Test default prompts when no custom prompts configured."""
        config = AgentConfig()
        
        onestep = OnestepLLMCallComponentSelectionStrategy(config=config)
        assert onestep.get_system_prompt() is not None
        
        twostep = TwostepLLMCallComponentSelectionStrategy(config=config)
        assert twostep.get_system_prompt() is not None
```

### 7. Update Documentation - configuration.md

**File:** `docs/guide/configuration.md`

Add sections under the `prompt` key:

```markdown
#### `system_prompt_onestep` [`str`, optional]

Override the initial system prompt section for one-step strategy (including 'AVAILABLE UI COMPONENTS:' heading, before component descriptions and examples).

If not set, uses the default hardcoded prompt. For detailed information and examples, see [Prompt Tuning](llm.md#prompt-tuning).


#### `system_prompt_twostep_step1select` [`str`, optional]

Override the initial system prompt section for two-step strategy's first step (component selection).

Must include 'AVAILABLE UI COMPONENTS:' heading. If not set, uses default hardcoded prompt. For detailed information, see [Prompt Tuning](llm.md#prompt-tuning).


#### `system_prompt_twostep_step2configure` [`str`, optional]

Override the initial system prompt section for two-step strategy's second step (field configuration).

MUST contain `{component}` placeholder which will be replaced with the selected component name. If not set, uses default hardcoded prompt. For detailed information, see [Prompt Tuning](llm.md#prompt-tuning).


#### `chart_instructions_template` [`str`, optional]

Override the chart instructions template used in both strategies when chart components are available.

Supports placeholders that will be replaced with dynamically generated component-specific content:
- `{chart_types}` - Chart type descriptions
- `{fields_by_type}` - Required fields for each chart type  
- `{chart_rules}` - Component-specific rules
- `{examples}` - Chart configuration examples

If not set, uses the default hardcoded template. For detailed information and examples, see [Prompt Tuning](llm.md#prompt-tuning).
```

### 8. Update Documentation - llm.md

**File:** `docs/guide/llm.md`

Add new "Prompt Tuning" chapter with detailed information:

```markdown
## Prompt Tuning

The agent's LLM inference uses system prompts to guide the component selection and configuration process. You can customize these prompts to match your domain, use case, or organizational style.

### Understanding System Prompt Structure

System prompts consist of two main parts:

1. **Initial Section** (configurable): General instructions, rules, and component list heading
2. **Dynamic Section** (generated): Component descriptions, chart instructions, and examples

### Customization Points

#### One-Step Strategy

Customize the initial prompt for the one-step strategy:

```yaml
prompt:
  system_prompt_onestep: |
    You are a financial data visualization assistant. Select the best UI component.
    
    RULES:
    - Generate JSON only
    - Prioritize tables for transaction data
    - Use charts for trend analysis
    
    AVAILABLE UI COMPONENTS:
```

**Important:** Always include `AVAILABLE UI COMPONENTS:` at the end, as this is where component descriptions are inserted.

#### Two-Step Strategy - Step 1 (Component Selection)

```yaml
prompt:
  system_prompt_twostep_step1select: |
    You are a medical data assistant. Select appropriate visualization component.
    
    RULES:
    - Generate JSON only
    - Comply with HIPAA requirements
    - Prioritize privacy in component selection
    
    AVAILABLE UI COMPONENTS:
```

#### Two-Step Strategy - Step 2 (Field Configuration)

```yaml
prompt:
  system_prompt_twostep_step2configure: |
    Configure fields for the {component} component for medical data visualization.
    
    RULES:
    - Do not include PII in field names
    - Follow HIPAA naming conventions
    - Generate JSON only
```

**Critical:** This prompt MUST contain the `{component}` placeholder, which will be replaced with the selected component name at runtime. The agent validates this on startup.

#### Chart Instructions Template

Customize how chart-specific instructions are presented:

```yaml
prompt:
  chart_instructions_template: |
    FINANCIAL CHART GUIDELINES:
    
    Available Chart Types:
    {chart_types}
    
    Required Fields Per Type:
    {fields_by_type}
    
    Business Rules:
    - Focus on fiscal year alignment
    - Use appropriate currency formatting
    {chart_rules}
    
    Examples:
    {examples}
```

**Placeholders:**

- `{chart_types}` - Generated descriptions of available chart types
- `{fields_by_type}` - Required field structure for each chart type
- `{chart_rules}` - Component-specific rules from metadata
- `{examples}` - Chart usage examples from metadata

#### Component-Specific Prompt Customization

In addition to customizing the initial system prompt sections (described above), you can also customize component-specific metadata that appears in the generated section of the prompt:

- **Component descriptions**: How each component is described to the LLM
- **Chart-specific instructions**: Fields, rules, and examples for chart components
- **Step 2 configuration rules and examples**: For the two-step strategy's field configuration phase

These customizations can be applied globally (via `config.prompt.components`) or per-data-type (via `data_types[type].components[component].prompt`), providing fine-grained control over how the LLM perceives each component.

For detailed information about component-specific prompt customization, including precedence rules and configuration examples, see [Prompt Customization for Component Selection](data_ui_blocks/index.md#prompt-customization-for-component-selection).

### Best Practices

#### 1. Start with Defaults

Before customizing, review the default prompts by inspecting the system prompt output or reading the strategy source code.

#### 2. Maintain Structure

Keep the essential structure:

- Clear rules section
- `AVAILABLE UI COMPONENTS:` heading (for step1 prompts)
- `{component}` placeholder (for step2 prompts)
- Placeholder syntax for chart templates

#### 3. Test Iteratively

Test prompt changes with representative queries:

1. Start with small modifications
2. Test with diverse queries
3. Monitor confidence scores and component selection quality
4. Iterate based on results

#### 4. Domain-Specific Language

Use terminology familiar to your domain:

- Financial: "transactions", "fiscal", "revenue"
- Medical: "patient", "diagnosis", "treatment"
- E-commerce: "orders", "products", "customers"

#### 5. Caching Compatibility

Custom prompts work seamlessly with the built-in system prompt caching. The cache key includes the configuration, so different prompt configurations maintain separate caches.

### Complete Example

```yaml
prompt:
  # One-step strategy prompt
  system_prompt_onestep: |
    You are a financial reporting assistant. Select the optimal UI component for financial data visualization.
    
    RULES:
    - Generate JSON only
    - Prioritize regulatory compliance
    - Use tables for detailed transaction records
    - Use charts for trend analysis and KPIs
    
    JSONPATH REQUIREMENTS:
    - Use precise paths to financial fields
    - Handle nested account structures
    
    AVAILABLE UI COMPONENTS:
  
  # Two-step strategy prompts
  system_prompt_twostep_step1select: |
    Financial Data Visualization - Component Selection
    
    Select the most appropriate component for the financial data.
    RULES:
    - Comply with financial reporting standards
    - Consider data sensitivity
    
    AVAILABLE UI COMPONENTS:
  
  system_prompt_twostep_step2configure: |
    Configure fields for {component} to display financial data.
    
    RULES:
    - Include relevant financial metrics only
    - Use standard accounting field names
    - Ensure audit trail compatibility
  
  # Chart instructions
  chart_instructions_template: |
    FINANCIAL CHARTS:
    
    Chart Types Available:
    {chart_types}
    
    Required Field Structure:
    {fields_by_type}
    
    Financial Reporting Rules:
    - Align with fiscal periods
    - Use consistent time series granularity
    - Include comparative periods when relevant
    {chart_rules}
    
    Chart Examples:
    {examples}
```

### Troubleshooting

**Issue:** LLM selects wrong components after customization

- **Solution:** Ensure your custom rules don't contradict component capabilities. Review component descriptions in the dynamic section.

**Issue:** Step2 validation error

- **Solution:** Verify `system_prompt_twostep_step2configure` contains `{component}` placeholder.

**Issue:** Chart instructions not appearing

- **Solution:** Ensure at least one chart component is in `selectable_components`.

**Issue:** Template placeholders not replaced

- **Solution:** Check placeholder names match exactly: `{chart_types}`, `{fields_by_type}`, `{chart_rules}`, `{examples}`.

```

## Benefits

1. **Domain Adaptation**: Tailor prompts to specific industries (finance, healthcare, e-commerce)
2. **Compliance**: Add compliance-specific instructions (HIPAA, GDPR, SOX)
3. **Brand Consistency**: Match organizational tone and terminology
4. **Experimentation**: A/B test different prompt strategies
5. **Localization**: Adapt prompts for different languages or regions
6. **Performance Tuning**: Optimize for specific LLM models or versions

## Backward Compatibility

- All configuration fields are optional with `Optional[str]` type
- When no custom prompts are provided, default hardcoded prompts are used
- Existing code without prompt customization continues to work unchanged
- System prompt caching works correctly with custom prompts (separate cache per config)

## Testing Strategy

Comprehensive test coverage includes:
- Custom prompt integration for each strategy step
- Placeholder validation and substitution
- Chart instructions templating
- Combined custom prompts (multiple fields)
- Backward compatibility (defaults)
- Error cases (missing placeholder)

## Files Modified

1. `libs/next_gen_ui_agent/types.py` - Added 4 configuration fields
2. `libs/next_gen_ui_agent/component_selection_common.py` - Added template parameter
3. `libs/next_gen_ui_agent/component_selection_llm_onestep.py` - Custom prompt support
4. `libs/next_gen_ui_agent/component_selection_llm_twostep.py` - Custom prompt support + validation
5. `libs/next_gen_ui_agent/component_selection_custom_prompts_test.py` - New test file
6. `docs/guide/configuration.md` - Reference documentation
7. `docs/guide/llm.md` - Detailed prompt tuning guide

## Implementation Notes

- The `AVAILABLE UI COMPONENTS:` heading is intentionally included in the configurable section to allow users full control over prompt structure
- The `{component}` placeholder validation happens at agent initialization to fail fast
- Chart instructions use `.format()` for placeholder substitution
- Default templates explicitly include the `"- Don't add unrequested metrics"` rule
- System prompt caching automatically handles different configurations
```

