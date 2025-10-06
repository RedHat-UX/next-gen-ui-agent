# Configuration

The Next Gen UI Agent can be configured in two ways: `programmatically` using Python dictionaries or `declaratively` using YAML configuration files.

## Configuration Options

### `inference` [`InferenceBase`, required]
The LLM inference engine to use for component selection and configuration.

The `inference` parameter accepts any class that extends `InferenceBase`. The Next Gen UI Agent provides the following built-in inference implementations:

- `next_gen_ui_agent.model.LangChainModelInference`: Wrapper for LangChain-compatible language models. Supports any LangChain LLM implementation including ChatOllama, ChatOpenAI, ChatAnthropic, and other LangChain model providers.
- `next_gen_ui_llama_stack.LlamaStackAgentInference`: Integration with Standalone Llama Stack
- `next_gen_ui_llama_stack_embedded.LlamaStackEmbeddedAsyncAgentInference`: Integration with Embedded Llama Stack


### `component_system` [`str`, optional]

[UI Component system](renderer/index.md) for rendering (default: `"json"`)

### `unsupported_components` [`bool`, optional]

Whether to allow unsupported/Tech Preview [dynamic UI components](data_ui_blocks/dynamic_components.md) to be selected by LLM (default: `False`)

### `component_selection_strategy` [`str`, optional]

Strategy for component selection

- `one_llm_call` / `default`: Uses single LLM call for component selection and configuration
- `two_llm_calls`: Uses two-step LLM process - first selects component type, second configures it - *highly experimental feature!*

### `input_data_json_wrapping` [`bool`, optional]

Whether to perform [automatic `InputData` JSON wrapping](input_data/structure.md#automatic-json-wrapping) if JSON structure is not good for LLM processing (default: `True`)

### `data_types` [`dict[str, AgentConfigDataType]`, optional]

Configurations for [`InputData.type`s](input_data/index.md#inputdata-object-fields), like:

* input data transformation
* list of components to render this data type

Key is `InputData.type` to configure, value is configuration object for that data type:

#### `data_transformer` [`str`, optional] 

Optional name of the [Input Data Transformer](input_data/transformation.md) to be used for this data type. JSON format is expected by default.

#### `components` [`list[AgentConfigComponent]`, optional]

Optional list of components used to render this data type. 

For now only one component can be defined here, and it is always interpreted as [Hand Build Component](./data_ui_blocks/hand_build_components.md).

We plan to implement more variants of this configuration in the future, like one preconfigured dymanic component, or 
even LLM powered selection from more components (dynamic with or without preconfiguration, or HBC).

##### `component` [`str`, required]

Name of the UI component. For now it is always interpreted as [Hand Build Component](./data_ui_blocks/hand_build_components.md) name 
so HBC is used to render this data type.

## Programmatic Configuration

### Usage with Inference Configuration

```python
from next_gen_ui_agent import NextGenUIAgent, LangChainModelInference
from langchain_ollama import ChatOllama

# Configure LLM inference
llm = ChatOllama(model="llama3.2")
inference = LangChainModelInference(llm)

# Create configuration
config = {
    "component_system": "json",
    "component_selection_strategy": "default",
    "unsupported_components": True
}

agent = NextGenUIAgent(config=config)
```

### With Hand-Built Components

```python
config = {
    "component_system": "json",
    "data_types": {
        "movies:movie-detail": { components : [{ componnet: "movies:movie-detail-view"}]},
        "movies:movies-list":  { components : [{ componnet: "movies:movies-list-view"}]},
    }
}

agent = NextGenUIAgent(config=config)
```

## YAML Configuration

### Basic YAML Configuration

Create a YAML configuration file:

```yaml
---
component_system: json
unsupported_components: false
component_selection_strategy: default

data_types:
  movies:movie-detail: 
    components:
      - component: movies:movie-detail-view
  movies:movies-list:
    components:
      - component: movies:movies-list-view
```

### Loading YAML Configuration

You can load one or several YAML config files which are merged into one configuration where the last config has the highest precedense.
Field `data_types` is merged so having different keys in different yamls are merged into one `data_types` configuration.

#### From File Path

```python
from next_gen_ui_agent import NextGenUIAgent
from next_gen_ui_agent.agent_config import read_config_yaml_file

# Load configuration from file
config = read_config_yaml_file("path/to/config.yaml")
agent = NextGenUIAgent(config=config)
```

#### From YAML String

```python
from next_gen_ui_agent import NextGenUIAgent
from next_gen_ui_agent.agent_config import parse_config_yaml

yaml_config = """
component_system: json
component_selection_strategy: two_llm_calls
unsupported_components: true
"""

# Pass YAML string directly
config = read_config_yaml_file(yaml_config)
agent = NextGenUIAgent(config=config)
```
