---
name: System Prompt Debug Tool
overview: Add system prompt debugging capability integrated into strategy classes with a CLI tool that allows users to inspect the actual prompts used by the agent for different configurations and data types.
todos:
  - id: add-base-debug-method
    content: Add abstract get_debug_prompts() method to ComponentSelectionStrategy base class
    status: completed
  - id: implement-onestep-debug
    content: Implement get_debug_prompts() in OnestepLLMCallComponentSelectionStrategy
    status: completed
  - id: refactor-twostep-step2
    content: Refactor step2 prompt generation in TwostepLLMCallComponentSelectionStrategy into _build_step2configure_system_prompt() method
    status: completed
  - id: implement-twostep-debug
    content: Implement get_debug_prompts() in TwostepLLMCallComponentSelectionStrategy using refactored method
    status: completed
  - id: create-debug-tool
    content: Create debug_system_prompt.py CLI tool with argument parsing, strategy instantiation, and entry point
    status: completed
  - id: add-tests
    content: Add comprehensive tests for debug functionality
    status: completed
  - id: update-readme
    content: Update README.md with debug tool documentation
    status: completed
isProject: false
---

# System Prompt Tuning Debug Tool

## Overview

Add debugging capability to expose system prompts used by both one-step and two-step strategies, with a command-line tool for easy inspection during prompt tuning.

## Architecture

### 1. Strategy Enhancement

**Files to modify:**

- `[libs/next_gen_ui_agent/component_selection_llm_strategy.py](libs/next_gen_ui_agent/component_selection_llm_strategy.py)` - Add abstract debug method to base class
- `[libs/next_gen_ui_agent/component_selection_llm_onestep.py](libs/next_gen_ui_agent/component_selection_llm_onestep.py)` - Implement debug method
- `[libs/next_gen_ui_agent/component_selection_llm_twostep.py](libs/next_gen_ui_agent/component_selection_llm_twostep.py)` - Refactor step2 prompt generation + implement debug method

**Changes:**

Add to `ComponentSelectionStrategy` base class:

```python
def get_debug_prompts(
    self, 
    data_type: Optional[str] = None,
    component_for_step2: Optional[str] = None
) -> dict[str, str]:
    """Get all system prompts for debugging/inspection.
    
    Returns dict with keys like 'system_prompt', 'step1_system_prompt', 
    'step2_system_prompt_<component>', etc.
    """
```

**One-step strategy** returns:

- `system_prompt` - The complete system prompt for given data_type

**Two-step strategy** returns:

- `step1_system_prompt` - Step 1 (component selection) prompt
- `step2_system_prompt_<component>` - Step 2 prompt for specified component(s)
  - If `component_for_step2` is specified, only that component's prompt
  - If None, generate prompts for all dynamic components (table, set-of-cards, all chart types)

**Important refactoring for two-step strategy:**

Current `inference_step2configure()` method builds the step2 system prompt inline (lines 512-528). This logic must be extracted into a dedicated private method:

```python
def _build_step2configure_system_prompt(
    self,
    component: str,
    metadata: dict,
    data_type: Optional[str] = None
) -> str:
    """Build step2configure system prompt for a given component.
    
    Args:
        component: Selected component name
        metadata: Component metadata dictionary
        data_type: Optional data type for data-type-specific prompt customization
        
    Returns:
        Complete step2 system prompt string
        
    This method contains the exact prompt generation logic used at runtime.
    """
```

**Keep existing data_type support**: The current implementation supports data-type-specific overrides for `twostep_step2configure_system_prompt_start`. We preserve this functionality so users can customize step2 prompts per data type if needed.

Then:

1. `inference_step2configure()` calls this method to get the prompt (passing data_type)
2. `get_debug_prompts()` calls this method to get the prompt (passing data_type)
3. Zero code duplication - identical prompts guaranteed
4. Debug tool can show step2 prompts for different data types

### 2. CLI Debug Tool

**New file:** `libs/next_gen_ui_agent/debug_system_prompt.py`

**Key features:**

- Loads AgentConfig from YAML file(s) specified via `--config-path`
- Optional `--selectable-components` to override which components are allowed
- Strategy selection via `--strategy` (one_llm_call or two_llm_calls)
- Optional `--data-type` to test data-type-specific prompts
- For two-step strategy: `--component` to specify which component's step2 prompt to show
- Plain text output with clear section headers
- Minimal metadata - focus on prompts themselves

**Command-line arguments:**

```bash
python -m next_gen_ui_agent.debug_system_prompt \
  --config-path config.yaml \
  [--config-path config2.yaml] \
  [--strategy {one_llm_call,two_llm_calls}] \
  [--data-type TYPE] \
  [--component COMPONENT] \
  [--selectable-components COMP1 COMP2 ...]
```

**Output format:**

```
=================================================================
SYSTEM PROMPT DEBUG OUTPUT
=================================================================

Strategy: one_llm_call
Data Type: my:custom:type
Allowed Components: table, chart-bar, chart-line, set-of-cards

=================================================================
SYSTEM PROMPT
=================================================================
<actual prompt content here>

=================================================================
```

For two-step with `--component table`:

```
=================================================================
STEP 1: COMPONENT SELECTION PROMPT
=================================================================
<step1 prompt>

=================================================================
STEP 2: FIELD CONFIGURATION PROMPT (component: table)
=================================================================
<step2 prompt for table>
```

### 3. Module Entry Point

The `debug_system_prompt.py` file will include a `if __name__ == "__main__":` block at the end, making it directly invokable as: `python -m next_gen_ui_agent.debug_system_prompt`

No separate `__main__.py` file needed.

### 4. Argument Handling

Create custom argument parser that accepts:

- `--config-path` (can be repeated for multiple files)
- `--strategy` (defaults to what's in config, or `one_llm_call`)
- `--data-type` (optional, to test data-type-specific prompts)
- `--component` (optional, for two-step strategy's step2 prompt)
- `--selectable-components` (optional override, space-separated list)

Note: We don't reuse `add_agent_config_comandline_args()` because it includes `--component-system` which is irrelevant for prompt debugging.

### 5. Testing Strategy

**New test file:** `libs/next_gen_ui_agent/debug_system_prompt_test.py`

Test cases:

- One-step strategy with default config
- One-step strategy with custom data_type
- Two-step strategy step1 prompt
- Two-step strategy step2 prompt with specific component
- Two-step strategy step2 prompt for all components
- Config with prompt overrides (system_prompt_start, examples, etc.)
- Multiple config files (merging)

## Implementation Details

### Prompt Versioning

Each strategy's debug output will naturally show "its version" because:

- One-step has different prompt structure than two-step
- System prompt content is built by strategy's `_build_system_prompt()` methods
- No explicit version numbers needed - the strategy type itself identifies the version

### Component Metadata for Step 2

For two-step strategy's step2 prompts, we refactor to avoid duplication:

**Current state:** `inference_step2configure()` (lines 487-551) builds prompt inline with:

- Gets initial section from config with precedence: data_type > global > default
- Formats `{component}` placeholder
- Calls `build_twostep_step2configure_rules(component, metadata)`
- Calls `build_twostep_step2configure_example(component, metadata)`

**Refactored approach:**

1. Extract prompt building logic into `_build_step2configure_system_prompt(component, metadata, data_type)`
2. Keep `data_type` parameter to preserve existing per-data-type customization support
3. `inference_step2configure()` calls this method (passing data_type from step1)
4. `get_debug_prompts()` calls this same method (passing data_type parameter)
5. For debug, need to pass metadata - get via `self._resolve_components_metadata(data_type)`

This ensures runtime and debug use **identical code** for step2 prompt generation, including full support for data-type-specific step2 prompt customization.

### Config Precedence Visibility

The prompts shown will reflect the actual precedence:

1. Data-type-specific config (highest priority)
2. Global config from YAML
3. Hardcoded defaults (lowest priority)

This happens automatically through `get_prompt_field()` function.

## Usage Examples

**Example 1: Debug default configuration**

```bash
./pants run libs/next_gen_ui_agent:debug_system_prompt
```

**Example 2: Debug with custom config and data type**

```bash
./pants run libs/next_gen_ui_agent:debug_system_prompt -- \
  --config-path my-agent-config.yaml \
  --data-type "k8s:deployment" \
  --strategy two_llm_calls
```

**Example 3: Inspect step2 prompt for specific component**

```bash
./pants run libs/next_gen_ui_agent:debug_system_prompt -- \
  --config-path my-agent-config.yaml \
  --strategy two_llm_calls \
  --component chart-bar
```

**Example 4: Multiple configs merged**

```bash
./pants run libs/next_gen_ui_agent:debug_system_prompt -- \
  --config-path base-config.yaml \
  --config-path overrides.yaml \
  --data-type "custom:type"
```

## Files to Create/Modify

**New files:**

1. `libs/next_gen_ui_agent/debug_system_prompt.py` - Main debug tool implementation with entry point
2. `libs/next_gen_ui_agent/debug_system_prompt_test.py` - Tests

**Modified files:**

1. `libs/next_gen_ui_agent/component_selection_llm_strategy.py` - Add abstract debug method
2. `libs/next_gen_ui_agent/component_selection_llm_onestep.py` - Implement debug method
3. `libs/next_gen_ui_agent/component_selection_llm_twostep.py` - Refactor step2 prompt into `_build_step2configure_system_prompt()` + implement debug method
4. `libs/next_gen_ui_agent/README.md` - Add documentation for debug tool

## Benefits

1. **Integrated Design**: Debug methods are part of strategy classes, ensuring they stay in sync with actual prompt generation
2. **Flexibility**: Supports all config options (YAML, data types, prompt overrides)
3. **Simplicity**: Plain text output, focused on what matters (the prompts)
4. **Reusability**: Can be used in CI/CD for prompt regression testing
5. **No Inference Needed**: Pure prompt inspection, no LLM calls required

## Documentation Updates

Update `[libs/next_gen_ui_agent/README.md](libs/next_gen_ui_agent/README.md)`:

### 1. Add to "## Provides" section

Add new bullet point after the LLM inference section:

```markdown
* System prompt debugging tool for tuning and inspecting LLM prompts
```

### 2. Add new section "## System Prompt Debugging"

Add new section after "## Installation" section:

```markdown
## System Prompt Debugging

The `debug_system_prompt` tool allows you to inspect the actual system prompts used by the agent for different configurations and data types. This is useful for prompt tuning and understanding how the agent behaves with different settings.

### Usage

**Basic usage:**
```bash
./pants run libs/next_gen_ui_agent:debug_system_prompt
```

**With configuration file:**

```bash
./pants run libs/next_gen_ui_agent:debug_system_prompt -- --config-path my-config.yaml
```

### Command-line Arguments

- `--config-path PATH` - Path to YAML config file (can be specified multiple times for config merging)
- `--strategy {one_llm_call,two_llm_calls}` - Component selection strategy (defaults to config value or `one_llm_call`)
- `--data-type TYPE` - Optional data type for data-type-specific prompt inspection
- `--component COMPONENT` - For two-step strategy: specific component name to show step2 prompt (e.g., `table`, `chart-bar`)
- `--selectable-components COMP1 COMP2 ...` - Override which components are selectable

### Examples

**Inspect one-step strategy with custom data type:**

```bash
./pants run libs/next_gen_ui_agent:debug_system_prompt -- \
  --config-path config.yaml \
  --data-type "k8s:deployment"
```

**Inspect two-step strategy step2 prompt for a specific component:**

```bash
./pants run libs/next_gen_ui_agent:debug_system_prompt -- \
  --strategy two_llm_calls \
  --component chart-bar \
  --data-type "metrics:timeseries"
```

**Test merged configurations:**

```bash
./pants run libs/next_gen_ui_agent:debug_system_prompt -- \
  --config-path base-config.yaml \
  --config-path overrides.yaml
```

```

```

