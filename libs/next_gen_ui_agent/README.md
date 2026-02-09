# Next Gen UI Core Functionality

This module is part of the [Next Gen UI Agent project](https://github.com/RedHat-UX/next-gen-ui-agent).

[![Module Category](https://img.shields.io/badge/Module%20Category-Core-blue)](https://github.com/RedHat-UX/next-gen-ui-agent)
[![Module Status](https://img.shields.io/badge/Module%20Status-Supported-green)](https://github.com/RedHat-UX/next-gen-ui-agent)

This module contains UI Agent Core functionality and frameworks.

## Provides

* `NextGenUIAgent` providing agent configuration and methods for individual processing steps
* `NextGenUIAgent` produced *UI Data Blocks*
    * [LLM selected and configured dynamic components](https://redhat-ux.github.io/next-gen-ui-agent/guide/data_ui_blocks/dynamic_components/)
        * Supported components: `one-card`, `image`, `video-player`, `set-of-cards`, `table`, `chart-bar`, `chart-line`, `chart-pie`, `chart-donut`, `chart-mirrored-bar`
    * [Hand Build Components](https://redhat-ux.github.io/next-gen-ui-agent/guide/data_ui_blocks/hand_build_components/)
    * Extensible framework for "data transformation" step per dynamic component
* Plugable ["UI renderer"](https://redhat-ux.github.io/next-gen-ui-agent/guide/renderer/implementing_serverside/) framework for UI components rendering
    * Default `json` renderer used to send definitions to client-side renderers
* Pluggable and configurable ["Input Data Transformation"](https://redhat-ux.github.io/next-gen-ui-agent/guide/input_data/transformation/) framework
    * Provided transformers: `json`, `yaml`, `csv-comma`, `csv-semicolon`, `csv-tab`, `fwctable`, `noop`
* Abstraction of the [LLM inference](https://redhat-ux.github.io/next-gen-ui-agent/guide/llm/)
    * `InferenceBase` inference interface used by UI Agent
    * `LangChainModelInference` inference implementation using LangChain `chat_models`
    * `ProxiedAnthropicVertexAIInference`  inference implementation to call Anthropic/Claude models from proxied Google Vertex AI API endpoint
    * reusable inference provider builder from commandline arguments/env variables, used by all AI protocol servers
* System prompt debugging tool for tuning and inspecting LLM prompts

## Installation

```sh
pip install -U next_gen_ui_agent
```

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

### Interface usage

```py
from next_gen_ui_agent import NextGenUIAgent

inference = # any AI framework inference

agent = NextGenUIAgent(
    inference=LlamaStackInference(model="ollama:llama3.2"),
)

# API is not very friendly ATM, as you have to call methods for individual processing steps. We plan to improve it iit the near future.

```

## Links

* [Documentation](https://redhat-ux.github.io/next-gen-ui-agent/guide/ai_apps_binding/pythonlib/)
* [Source Codes](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs/next_gen_ui_agent)
* [Contributing](https://redhat-ux.github.io/next-gen-ui-agent/development/contributing/)
