---
name: Rename twostep strategy steps
overview: Rename step1 to step1select and step2 to step2configure throughout the twostep strategy implementation, including code, configuration, tests, and documentation.
todos:
  - id: update-common
    content: "Update component_selection_common.py: rename constants, functions, and metadata keys"
    status: completed
  - id: update-twostep
    content: "Update component_selection_llm_twostep.py: rename methods, variables, imports, and comments"
    status: completed
  - id: update-types
    content: "Update types.py: rename fields in AgentConfigPromptComponent class"
    status: completed
  - id: update-schemas
    content: "Update JSON schema files: agent_config.schema.json, a2a_agent_config.schema.json, mcp_agent_config.schema.json"
    status: completed
  - id: update-common-tests
    content: "Update component_selection_common_test.py: rename test classes and update function calls"
    status: completed
  - id: update-twostep-tests
    content: "Update component_selection_llm_twostep_test.py: rename test classes, methods, and variable references"
    status: completed
  - id: update-docs
    content: "Update documentation: configuration.md and data_ui_blocks/index.md"
    status: completed
  - id: verify-tests
    content: Run tests to verify all changes work correctly
    status: completed
isProject: false
---

# Rename Twostep Strategy Steps

## Overview

Rename the steps in the two-step component selection strategy for better clarity:

- `step1` → `step1select` (component selection step)
- `step2` → `step2configure` (component configuration step)

This is a comprehensive refactoring that touches code, configuration types, tests, JSON schemas, and documentation.

## Changes Required

### 1. Core Implementation Files

#### `[libs/next_gen_ui_agent/component_selection_common.py](libs/next_gen_ui_agent/component_selection_common.py)`

Rename constants and function names:

- `TWOSTEP_STEP1_PROMPT_RULES` → `TWOSTEP_STEP1SELECT_PROMPT_RULES`
- `TWOSTEP_STEP2_PROMPT_RULES` → `TWOSTEP_STEP2CONFIGURE_PROMPT_RULES`
- `build_twostep_step1_examples()` → `build_twostep_step1select_examples()`
- `build_twostep_step2_example()` → `build_twostep_step2configure_example()`
- `build_twostep_step2_rules()` → `build_twostep_step2configure_rules()`

Update metadata keys in `COMPONENT_METADATA` dictionary (lines 131-196):

- `"twostep_step2_example"` → `"twostep_step2configure_example"`
- `"twostep_step2_rules"` → `"twostep_step2configure_rules"`

#### `[libs/next_gen_ui_agent/component_selection_llm_twostep.py](libs/next_gen_ui_agent/component_selection_llm_twostep.py)`

Rename methods, variables, and update imports:

- Import names from `component_selection_common`
- `_system_prompt_step1_cache` → `_system_prompt_step1select_cache` (line 59)
- `_step1_system_prompt` → `_step1select_system_prompt` (line 62)
- `_build_step1_system_prompt()` → `_build_step1select_system_prompt()` (line 72)
- `_get_or_build_step1_system_prompt()` → `_get_or_build_step1select_system_prompt()` (line 121)
- `inference_step_1()` → `inference_step1select()` (line 309)
- `inference_step_2()` → `inference_step2configure()` (line 354)
- Update all method calls and references
- Update comments mentioning "step 1" and "step 2" (lines 58, 62, 121, 246, etc.)

### 2. Type Definitions

#### `[libs/next_gen_ui_agent/types.py](libs/next_gen_ui_agent/types.py)`

Update `AgentConfigPromptComponent` class (lines 130-156):

- Field name: `twostep_step2_example` → `twostep_step2configure_example`
- Field name: `twostep_step2_rules` → `twostep_step2configure_rules`
- Update docstring (line 135)
- Update Field descriptions

### 3. JSON Schema Files

Update three schema files with identical changes to property names and descriptions:

#### `[spec/config/agent_config.schema.json](spec/config/agent_config.schema.json)`

#### `[spec/a2a/a2a_agent_config.schema.json](spec/a2a/a2a_agent_config.schema.json)`

#### `[spec/mcp/mcp_agent_config.schema.json](spec/mcp/mcp_agent_config.schema.json)`

For each file, update:

- Property name: `"twostep_step2_example"` → `"twostep_step2configure_example"`
- Property name: `"twostep_step2_rules"` → `"twostep_step2configure_rules"`
- Description text mentioning these field names

### 4. Test Files

#### `[libs/next_gen_ui_agent/component_selection_common_test.py](libs/next_gen_ui_agent/component_selection_common_test.py)`

Rename test classes and update function calls (lines 240-320):

- Class: `TestBuildTwostepStep1Examples` → `TestBuildTwostepStep1selectExamples`
- Class: `TestBuildTwostepStep2Example` → `TestBuildTwostepStep2configureExample`
- Class: `TestBuildTwostepStep2Rules` → `TestBuildTwostepStep2configureRules`
- Update all function imports and calls

#### `[libs/next_gen_ui_agent/component_selection_llm_twostep_test.py](libs/next_gen_ui_agent/component_selection_llm_twostep_test.py)`

Rename test classes and methods:

- Class: `TestBuildStep1SystemPrompt` → `TestBuildStep1selectSystemPrompt`
- Class: `TestSystemPromptCachingTwostep` → update cache variable references
- Update method names: `_build_step1_system_prompt` → `_build_step1select_system_prompt`
- Update variable names: `_system_prompt_step1_cache` → `_system_prompt_step1select_cache`
- Update all comments referring to "step 1" and "step 2" throughout the file

### 5. Documentation Files

#### `[docs/guide/configuration.md](docs/guide/configuration.md)`

Update field names in configuration examples (lines 158-166, 220, 282, 291):

- `twostep_step2_example` → `twostep_step2configure_example`
- `twostep_step2_rules` → `twostep_step2configure_rules`

Update both YAML and Python examples.

#### `[docs/guide/data_ui_blocks/index.md](docs/guide/data_ui_blocks/index.md)`

Update field names in documentation (lines 121, 137, 141):

- `twostep_step2_example` → `twostep_step2configure_example`
- `twostep_step2_rules` → `twostep_step2configure_rules`
- Update bullet point text (line 137)

## Implementation Notes

- This is a breaking change for existing configurations using `twostep_step2_example` and `twostep_step2_rules` fields
- All changes maintain backward compatibility in behavior, only names change
- The JSON schemas will need regeneration after type changes
- Test files should be updated to reflect new names while maintaining test coverage
- Comments and docstrings should be updated to use "step1select" and "step2configure" terminology consistently

