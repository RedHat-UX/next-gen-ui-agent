# Configuration

The Next Gen UI Agent can be configured in two ways: `programmatically` using Python dictionaries or `declaratively` using YAML configuration files.

## Configuration Options

### Core Settings

- **`inference`** (`InferenceBase`): The LLM inference engine to use for component selection and configuration
- **`component_system`** (`str`, optional): Component system for rendering (default: `"json"`)
- **`unsupported_components`** (`bool`, optional): Whether to allow unsupported UI components (default: `False`)
- **`component_selection_strategy`** (`str`, optional): Strategy for component selection (default: `"default"`)
- **`hand_build_components_mapping`** (`dict[str, str]`, optional): Mapping from input data types to hand-built component types

### Component Selection Strategies

- **`"default"` / `"one_llm_call"`**: Uses single LLM call for component selection and configuration
- **`"two_llm_calls"`**: Uses two-step LLM process - first selects component type, then configures it

## Programmatic Configuration

### Usage with Inference Configuration

```python
from next_gen_ui_agent import NextGenUIAgent, LangChainModelInference
from langchain_ollama import ChatOllama

# Configure LLM inference
llm = ChatOllama(model="llama3.2")
inference = LangChainModelInference(llm)

# Create configuration with inference
config = {
    "inference": inference,
    "component_system": "json",
    "component_selection_strategy": "default",
    "unsupported_components": True
}

agent = NextGenUIAgent(config)
```

### With Hand-Built Components

```python
config = {
    "component_system": "json",
    "hand_build_components_mapping": {
        "movies.movie-detail": "movies:movie-detail-view",
        "movies.movies-list": "movies:movies-list-view",
    }
}

agent = NextGenUIAgent(config)
```

## YAML Configuration

### Basic YAML Configuration

Create a YAML configuration file:

```yaml
---
component_system: json
unsupported_components: false
component_selection_strategy: default

hand_build_components_mapping:
  movies.movie-detail: movies:movie-detail-view
  movies.movies-list: movies:movies-list-view,
```

### Loading YAML Configuration

#### From File Path

```python
from next_gen_ui_agent import NextGenUIAgent
from next_gen_ui_agent.agent_config import read_config_yaml_file

# Load configuration from file
config = read_config_yaml_file("path/to/config.yaml")
agent = NextGenUIAgent(config)
```

#### From YAML String

```python
from next_gen_ui_agent import NextGenUIAgent

yaml_config = """
component_system: json
component_selection_strategy: two_llm_calls
unsupported_components: true

hand_build_components_mapping:
  namespace.list: namespace-table
  pod.details: pod-card
"""

# Pass YAML string directly to constructor
agent = NextGenUIAgent(yaml_config)
```
