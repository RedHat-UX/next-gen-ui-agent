---
name: Add UI Agent Config Loading
overview: Add support for loading UI Agent YAML config files in eval.py to configure component selection strategy and selectable components from config instead of hardcoded constants.
todos:
  - id: update-eval-utils-args
    content: Add -a argument to load_args() in eval_utils.py
    status: pending
  - id: load-config-files
    content: Add config file loading logic in eval.py main block
    status: pending
  - id: update-component-selection
    content: Update component selection and printing logic with config support
    status: pending
  - id: update-strategy-instantiation
    content: Replace TWO_STEP_COMPONENT_SELECTION with config-based strategy selection
    status: pending
  - id: update-readme-docs
    content: Document new -a argument in README.md
    status: pending
isProject: false
---

# Add UI Agent Config Loading to [eval.py](http://eval.py)

## Overview

Enhance the evaluation script to support loading UI Agent YAML configuration files via a new `-a` command line argument. This will allow configuration of component selection strategy and selectable components from config files rather than hardcoded constants.

## Files to Modify

### 1. `[tests/ai_eval_components/eval_utils.py](tests/ai_eval_components/eval_utils.py)`

**Function: `load_args()**` (lines 14-84)

- Add new command line argument `-a` (can be specified multiple times) to accept paths to UI Agent YAML config files
- Update the `getopt.getopt()` call to include `-a:` in the options string
- Store config file paths in a list variable `arg_config_files`
- Update help text to document the new `-a` argument
- Return `arg_config_files` as an additional value in the return tuple

### 2. `[tests/ai_eval_components/eval.py](tests/ai_eval_components/eval.py)`

**Import statements** (lines 39-70)

- Add import for config loading functions:
  ```python
  from next_gen_ui_agent.agent_config import read_config_yaml_file
  ```

**Main execution block** (line 307)

- Update the unpacking of `load_args()` return value to include `arg_config_files`

**Config loading logic** (after line 317, before inference initialization)

- Add logic to load config files if `arg_config_files` is provided:
  ```python
  config = None
  config_loaded = False
  if arg_config_files and len(arg_config_files) > 0:
      config = read_config_yaml_file(arg_config_files)
      config_loaded = True
      print(f"Loaded UI Agent config from: {arg_config_files}")
  ```

**Component selection configuration** (lines 389-395)

- Before the existing `selectable_components` logic:
  - If config was loaded and `-p` flag is set, override `config.selectable_components = set(run_components)`
- Update the print messages to handle three cases:
  1. If `-p` flag is set: "UI Agent selects only from enabled components: {run_components}"
  2. If config was loaded and `-p` not set: "UI Agent selects from components defined in UI Agent config file"
  3. Otherwise: "UI Agent selects from all supported components"
- Keep `selectable_components` variable for backward compatibility when no config is loaded

**Strategy instantiation** (lines 397-414)

- Replace the `TWO_STEP_COMPONENT_SELECTION` constant check with logic based on config:
  - If config is loaded, check `config.component_selection_strategy` field:
    - If `"two_llm_calls"`: instantiate `TwostepLLMCallComponentSelectionStrategy`
    - Otherwise: instantiate `OnestepLLMCallComponentSelectionStrategy` (default)
  - If no config loaded: instantiate `OnestepLLMCallComponentSelectionStrategy` (default)
- When config is not loaded but `-p` flag is set, create a minimal `AgentConfig` with only `selectable_components` set (maintain current behavior)
- Pass the full `config` object to the strategy constructors when available
- Update the print messages to change "System prompt from the" to "Default system prompt from the" in both the Onestep and Twostep strategy print statements

### 3. `[tests/ai_eval_components/README.md](tests/ai_eval_components/README.md)`

**Command line arguments section** (around lines 61-71)

- Add documentation for the new `-a` argument:
  ```
  - `-a <config-file-path>` to load UI Agent YAML configuration file(s), can be specified multiple times to load and merge multiple config files
  ```
- Add a brief explanation that when `-a` is provided:
  - Component selection strategy is determined by the config file's `component_selection_strategy` field
  - Selectable components are taken from the config file's `selectable_components` field (unless `-p` is used to override)

## Implementation Details

### Config Override Logic

When both `-a` (config file) and `-p` (select only from enabled) are specified:

- The config file is loaded first
- Then `config.selectable_components` is overridden with `run_components`
- This ensures the `-p` flag takes precedence

### Component Selection Strategy Priority

1. If `-a` is provided: use `config.component_selection_strategy` (defaults to "one_llm_call" if not specified)
2. If `-a` is not provided: always use "one_llm_call" (Onestep strategy)

### Backward Compatibility

- If no `-a` argument is provided, behavior remains unchanged (Onestep strategy with optional component filtering via `-p`)
- The `TWO_STEP_COMPONENT_SELECTION` constant can remain in place but will be ignored when config is loaded

## Testing Considerations

Per user requirements, no tests are needed for this change.