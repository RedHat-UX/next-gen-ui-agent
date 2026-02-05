---
name: Per-DataType Prompt Customization
overview: Add support for customizing system prompts per data_type, allowing all AgentConfigPrompt fields (except components) to be overridden at the data_type level with proper precedence over global settings.
todos:
  - id: types-update
    content: Create AgentConfigPromptBase, refactor AgentConfigPrompt to inherit from it, and add prompt field to AgentConfigDataType in types.py
    status: completed
  - id: helper-function
    content: Create get_prompt_field() helper function in component_selection_common.py
    status: completed
  - id: onestep-updates
    content: Update one-step strategy prompt building to support data-type prompts in component_selection_llm_onestep.py
    status: completed
  - id: twostep-updates
    content: Update two-step strategy prompt building to support data-type prompts in component_selection_llm_twostep.py
    status: completed
  - id: new-tests
    content: Create comprehensive test file component_selection_pertype_prompts_test.py
    status: completed
  - id: existing-tests
    content: Add test cases to existing test files for per-data-type prompts
    status: completed
  - id: docs-configuration
    content: Update configuration.md with reference to per-data-type prompt field
    status: completed
  - id: docs-data-ui-blocks
    content: Update data_ui_blocks/index.md with detailed per-data-type prompt documentation
    status: completed
  - id: docs-llm
    content: Update llm.md to reference per-data-type prompt customization
    status: completed
isProject: false
---

# Per-Data-Type System Prompt Customization

## Overview

This plan adds support for customizing LLM system prompts on a per-data-type basis, allowing fine-grained control over how the agent behaves for different input data types. All fields from `AgentConfigPrompt` (except `components`) will be available at the data-type level as optional overrides.

## Key Changes

### 1. Type System Updates ([libs/next_gen_ui_agent/types.py](libs/next_gen_ui_agent/types.py))

**Use proper inheritance to avoid field duplication**:

- Create `AgentConfigPromptBase` class with all prompt fields EXCEPT `components`
- Make `AgentConfigPrompt` inherit from `AgentConfigPromptBase` and add the `components` field
- Use `AgentConfigPromptBase` type for `AgentConfigDataType.prompt` field

**Implementation approach**:

```python
class AgentConfigPromptBase(BaseModel):
    """Base prompt configuration (all fields except components)."""
    
    system_prompt_start: Optional[str] = Field(default=None, ...)
    twostep_step1select_system_prompt_start: Optional[str] = Field(default=None, ...)
    twostep_step2configure_system_prompt_start: Optional[str] = Field(default=None, ...)
    chart_instructions_template: Optional[str] = Field(default=None, ...)
    examples_normalcomponents: Optional[str] = Field(default=None, ...)
    examples_charts: Optional[str] = Field(default=None, ...)
    twostep_step1select_examples_normalcomponents: Optional[str] = Field(default=None, ...)
    twostep_step1select_examples_charts: Optional[str] = Field(default=None, ...)


class AgentConfigPrompt(AgentConfigPromptBase):
    """Global prompt configuration (inherits base fields and adds components)."""
    
    components: Optional[dict[str, AgentConfigPromptComponent]] = Field(
        default=None,
        description="Component metadata overrides...",
    )


class AgentConfigDataType(BaseModel):
    """Agent Configuration for the Data Type."""
    
    # ... existing fields ...
    
    prompt: Optional[AgentConfigPromptBase] = Field(
        default=None,
        description="Optional prompt configuration for this data type. Overrides global prompt settings.",
    )
```

### 2. Prompt Construction Logic Updates

**Update one-step strategy** ([libs/next_gen_ui_agent/component_selection_llm_onestep.py](libs/next_gen_ui_agent/component_selection_llm_onestep.py)):

Modify `_build_system_prompt()` (lines ~63-138) to accept `data_type` parameter:

- Add parameter: `data_type: Optional[str] = None`
- Use `get_prompt_field()` helper to resolve each prompt field with precedence: data-type > global > default
- Example: `system_prompt_start = get_prompt_field("system_prompt_start", self.config, data_type, DEFAULT_SYSTEM_PROMPT_START)`
- The helper function will handle looking up data-type config internally

Modify `_build_examples()` (lines ~140-230) similarly:

- Add `data_type: Optional[str] = None` parameter
- Use `get_prompt_field()` helper for examples fields
- Example: `examples_normalcomponents = get_prompt_field("examples_normalcomponents", self.config, data_type, DEFAULT_EXAMPLES_NORMALCOMPONENTS)`

Note: `_get_or_build_system_prompt()` already receives `data_type` parameter, so just pass it through to the build methods.

**Update two-step strategy** ([libs/next_gen_ui_agent/component_selection_llm_twostep.py](libs/next_gen_ui_agent/component_selection_llm_twostep.py)):

Apply same pattern to:

- `_build_step1select_system_prompt()` (lines ~86-154) - add `data_type` parameter, use `get_prompt_field()` helper
- `_build_step1select_examples()` (lines ~156-247) - add `data_type` parameter, use `get_prompt_field()` helper
- `_get_or_build_step1select_system_prompt()` already receives `data_type`, pass it through
- `inference_step2configure()` (lines ~484-556) - add `data_type` parameter, use `get_prompt_field()` for step2 prompts

### 3. Prompt Precedence Helper Function

Create utility function in [libs/next_gen_ui_agent/component_selection_common.py](libs/next_gen_ui_agent/component_selection_common.py):

```python
def get_prompt_field(
    field_name: str,
    config: AgentConfig,
    data_type: Optional[str],
    default: Any
) -> Any:
    """Get prompt field with precedence: data_type > global > default.
    
    Args:
        field_name: Name of the prompt field to retrieve
        config: Agent configuration containing both global and data-type configs
        data_type: Optional data type to look up data-type-specific config
        default: Default value if not found in configs
        
    Returns:
        The prompt field value following precedence order
    """
    # Look up data-type-specific prompt if data_type provided
    data_type_prompt = None
    if data_type and config.data_types and data_type in config.data_types:
        data_type_prompt = config.data_types[data_type].prompt
    
    # Check data-type level first
    if data_type_prompt:
        value = getattr(data_type_prompt, field_name, None)
        if value is not None:
            return value
    
    # Check global level
    if config.prompt:
        value = getattr(config.prompt, field_name, None)
        if value is not None:
            return value
    
    # Return default
    return default
```

### 4. System Prompt Caching Validation

**Verify caching still works correctly**:

- Current cache key is `data_type` (or `None`) - this is perfect for per-data-type prompts
- No changes needed to caching mechanism
- Cache isolation already exists between different data_types
- Add tests to verify cache works with data-type-specific prompts

### 5. Comprehensive Testing

**Note**: JSON schemas in `spec/` directory are auto-generated from Python Pydantic models, so no manual schema updates needed.

**New test file**: `libs/next_gen_ui_agent/component_selection_pertype_prompts_test.py`

Test cases:

1. Per-data-type `system_prompt_start` override (onestep)
2. Per-data-type `twostep_step1select_system_prompt_start` override
3. Per-data-type `twostep_step2configure_system_prompt_start` override
4. Per-data-type chart instructions template
5. Per-data-type examples (normalcomponents and charts)
6. Precedence: data-type > global > default
7. Multiple data_types with different prompt configs
8. Caching works correctly with per-data-type prompts
9. Data-type prompts work with per-component overrides

**Update existing tests**:

- Add test cases to [libs/next_gen_ui_agent/component_selection_llm_onestep_test.py](libs/next_gen_ui_agent/component_selection_llm_onestep_test.py)
- Add test cases to [libs/next_gen_ui_agent/component_selection_llm_twostep_test.py](libs/next_gen_ui_agent/component_selection_llm_twostep_test.py)

### 6. Documentation Updates

**[docs/guide/configuration.md](docs/guide/configuration.md)**:

- Add `prompt` field under `data_types` section (around line 76)
- Brief description: "Optional prompt configuration for this data type. Overrides global prompt settings. See [Prompt Customization](llm.md#prompt-tuning) for details."
- Reference the detailed documentation in data_ui_blocks/index.md

**[docs/guide/data_ui_blocks/index.md](docs/guide/data_ui_blocks/index.md)**:

- Add new subsection under "Prompt Customization for Component Selection" (after line 105)
- Title: "Per-Data-Type Prompt Customization"
- Detailed explanation of:
  - Available fields (all from AgentConfigPrompt except components)
  - Precedence order: data-type > global > default
  - Configuration examples (YAML)
  - Use cases: different system prompts for different tools/data sources
- Update precedence list (currently line 95-99) to include data-type level

**[docs/guide/llm.md](docs/guide/llm.md)**:

- Update "Prompt Tuning" section (line 65+) to mention per-data-type customization
- Add cross-reference to data_ui_blocks/index.md for details

## Precedence Order (Updated)

The final precedence order for prompt construction will be:

1. **Base prompts**: Default hardcoded in `COMPONENT_METADATA`
2. **Global prompt overrides**: From `config.prompt` fields
3. **Per-data-type prompt overrides**: From `config.data_types[type].prompt` fields (NEW)
4. **Per-component prompt overrides**: From `config.data_types[type].components[].prompt.components` (existing, for component descriptions only)

Note: Per-component overrides only affect component-specific fields (description, chart_*, twostep_step2configure_*), while per-data-type overrides affect system prompt structure and examples.

## Validation & Edge Cases

- Validate that per-data-type prompt config is properly parsed from YAML
- Ensure None values don't override lower-precedence settings
- Test with missing data_type (fallback to global)
- Test with empty/null prompt config at data-type level
- Verify step2 `{component}` placeholder still works with data-type overrides

## Success Criteria

✅ All AgentConfigPrompt fields (except components) available at data-type level
✅ Proper precedence: data-type > global > default
✅ System prompt caching works correctly
✅ All tests pass (existing + new)
✅ Documentation is comprehensive and accurate
✅ JSON schemas auto-generate correctly from updated Pydantic models