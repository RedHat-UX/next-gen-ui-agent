# Configuration

The Next Gen UI Agent can be configured in two ways: `programmatically` using Python dictionaries or `declaratively` using YAML configuration files.

[Agent configuration JSON Schema and how to use it to validate YAML files in IDE is described here](../spec/config.md).

## Configuration Options

### `component_system` [`str`, optional]

[UI Component system](renderer/index.md) for rendering (default: `"json"`)


### `data_transformer` [`str`, optional] 

Optional name of the [Input Data Transformer](input_data/transformation.md) used by the UI Agent. 
Can be overriden [per data type](#data_transformer-str-optional_1). Defaults to [JSON](./input_data/transformation.md#json-transformer).


### `enable_input_data_type_detection` [`bool`, optional]

Controls whether the agent automatically detects the appropriate [Input Data Transformer](./input_data/transformation.md) based on data structure when no transformer is explicitly configured (default: `True`).

More detailed information can be found in [Configuring data transformation auto detection](./input_data/transformation.md#configuring-data-transformation-auto-detection) section of our Input Data Transformation guide.


### `selectable_components` [`set[str]`, optional]

Set of components that can be selected by the agent's LLM for the input data visualization. If not set, all the components supported by the agent can be selected.
You can select from [all the supported dynamic components](./data_ui_blocks/dynamic_components.md) using their Component identification like  `one-card`, `image`, 
`video-player`, `table`, `set-of-cards`, `chart-bar`, `chart-line`, `chart-pie`, `chart-donut`, `chart-mirrored-bar`.


### `component_selection_strategy` [`str`, optional]

Strategy for LLM powered component selection and configuration step:

- `one_llm_call`: Uses single LLM inference call for component selection and configuration - default
- `two_llm_calls`: Uses two LLM inference calls - first selects component type, second configures it - *experimental feature!* 
  We haven't seen any gain in accuracy, processing time mostly doubles, but you can play with this approach if interrested.


### `input_data_json_wrapping` [`bool`, optional]

Whether to perform [automatic `InputData` JSON wrapping](input_data/structure.md#automatic-json-wrapping) if JSON structure is not good for LLM processing (default: `True`)


### `generate_all_fields` [`bool`, optional]

If `True`, the agent will generate all possible view Fields for the UI component into its output configuration `UIBlockComponentMetadata.fields_all`. 
It can be used in UI component to give user a chance to manually select/update which fields are shown.
If `False` then all fields aren't generated. Can be overriden for individual `data_types`. (default: `False`)


### `data_types` [`dict[str, AgentConfigDataType]`, optional]

Configurations for [`InputData.type`s](input_data/index.md#inputdata-object-fields), like:

* input data transformation
* list of components to render this data type

Key is `InputData.type` to configure, value is configuration object for that data type:

#### `data_transformer` [`str`, optional] 

Optional name of the [Input Data Transformer](input_data/transformation.md) to be used for this data type instead of [Agent's default one](#data_transformer-str-optional).

#### `generate_all_fields` [`bool`, optional]

If `True`, the agent will generate all possible view Fields for the UI component into its output configuration `UIBlockComponentMetadata.fields_all`. 
It can be used in UI component to give user a chance to manually select/update which fields are shown.
If `False` then all fields aren't generated, if not defined then [agent's default setting](#generate_all_fields-bool-optional) is used.
All fields are supported only for `table` and `set-of-cards` components.


#### `components` [`list[AgentConfigComponent]`, optional]

Optional list of components used to render this data type. See [description of the component selection process](data_ui_blocks/index.md#selection-and-configuration-process).

**Single component**: When one component is configured, it's used directly without the LLM processing. It has to be [Hand Build Component](./data_ui_blocks/hand_build_components.md) or [Dynamic component](./data_ui_blocks/dynamic_components.md) with pre-defined `configuration` provided.

**Multiple components**: When multiple components are configured, LLM selects the best one based on user prompt and data. Each component can be:

* [Dynamic component](./data_ui_blocks/dynamic_components.md) with pre-defined configuration (LLM selection only)
* [Dynamic component](./data_ui_blocks/dynamic_components.md) without configuration (LLM selection and configuration)

**Note**: [Hand Build Components](./data_ui_blocks/hand_build_components.md) cannot be mixed with other components now. This restriction will be removed in a future.


##### `component` [`str`, required]

Name of the UI component. Identification of the supported [Dynamic Component](./data_ui_blocks/dynamic_components.md) can be used here.
Other value is interpreted as [Hand Build Component](./data_ui_blocks/hand_build_components.md) name and HBC is rendered.


##### `llm_configure` [`bool`, optional]

Controls whether LLM generates component configuration. Defaults to `True`. Only applicable to Dynamic components.

- `True` (default): LLM generates configuration (fields). Pre-defined `configuration` is optional and ignored if provided for now (will be used as a base for LLM generation in the future).
- `False`: Pre-defined `configuration` must be provided and will be used. LLM only selects which component to use.

##### `configuration` [`AgentConfigDynamicComponentConfiguration`, optional]

Pre-defined configuration for Dynamic components. Required when `llm_configure=False` or for single dynamic component, optional otherwise.

###### `title` [`str`, required]

Title of the component to be rendered in UI.


###### `fields` [`list[DataField]`, required]

Fields of the UI component in the same format as generated by the LLM. Data transformation step is performed 
to pick-up Input Data values for UI rendering, so consult it for individual components specifics.

####### `name` [`str`, required]

Name of the field rendered in UI. Can be used as a name of column in the table, or name of the fact in the card.

####### `data_path` [`str`, required]

JSON Path pointer to [Input Data structure](./input_data/structure.md) to pick up values for UI rendering.


### `prompt` [`AgentConfigPrompt`, optional]

Configuration for customizing LLM system prompts used by the agent.

#### `components` [`dict[str, AgentConfigPromptComponent]`, optional]

This allows you to override component related parts of the prompt.
Dictionary mapping component names to their prompt part overrides. Keys must be valid component names, 
identification of the supported [Dynamic Component](./data_ui_blocks/dynamic_components.md) can be used here, e.g., `table`, `chart-bar`, `one-card`.
Only specified fields are overridden for the prompt, unspecified fields retain their default values.

##### `description` [`str`, optional]

Override the main component description for the component selection. This helps the LLM understand when to use this component.

##### `twostep_step2_example` [`str`, optional]

Override the example shown to the LLM during field selection when using `two_llm_calls` strategy. 
Provide a JSON example showing how fields should be selected for this component.

##### `twostep_step2_rules` [`str`, optional]

Override additional rules for field selection when using `two_llm_calls` strategy. 
Use this to provide component-specific guidance for field selection.

##### `chart_description` [`str`, optional]

Override the chart type description shown in chart selection prompts. Only applicable to chart components 
(`chart-bar`, `chart-line`, `chart-pie`, `chart-donut`, `chart-mirrored-bar`).

##### `chart_fields_spec` [`str`, optional]

Override the fields specification for chart component. Describes what fields the chart expects (e.g., `[category, metric]`).

##### `chart_rules` [`str`, optional]

Override chart-specific rule. Use this to add domain-specific guidance for chart usage.

##### `chart_inline_examples` [`str`, optional]

Override inline JSON examples for chart components. Provide examples specific to your data domain.


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
    "enable_input_data_type_detection": True  # Auto-detect input format (default)
}

agent = NextGenUIAgent(config=config)
```

### With Prompt Customization

```python
from next_gen_ui_agent import NextGenUIAgent, AgentConfig
from next_gen_ui_agent.types import AgentConfigPrompt, AgentConfigPromptComponent

# Create configuration with customized prompts
config = AgentConfig(
    prompt=AgentConfigPrompt(
        components={
            "table": AgentConfigPromptComponent(
                description="Display structured business data in tabular format",
                twostep_step2_rules="Always include ID, name, and date fields"
            ),
            "chart-bar": AgentConfigPromptComponent(
                chart_description="Compare sales metrics across products or regions",
                chart_rules="Show values in thousands"
            )
        }
    )
)

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
component_selection_strategy: default

# Auto-detect input data format (enabled by default)
enable_input_data_type_detection: true

data_types:
  movies:movie-detail: 
    components:
      - component: movies:movie-detail-view
  movies:movies-list:
    components:
      - component: movies:movies-list-view
```

### YAML with Prompt Customization

Customize component descriptions and rules for your domain:

```yaml
---
component_system: json

prompt:
  components:
    table:
      description: "Display structured business data in tabular format"
      twostep_step2_rules: "Always include ID, name, and date fields"
    
    chart-bar:
      description: "Bar chart is suitable for values comparison"
      chart_description: "Compare sales metrics across products or regions"
      chart_rules: "Show values in thousands"
    
    one-card:
      description: "Show detailed information for a single business entity"
      twostep_step2_rules: "Include key identifiers and status information"
```

### Multiple Component Configuration

Configure multiple components per data type with LLM-based selection:

```yaml
---
data_types:
  product-list:
    components:
      # Option 1: LLM selects and configures
      - component: table
        llm_configure: true  # default, can be omitted
      # Option 2: LLM selects, use pre-config
      - component: set-of-cards
        llm_configure: false
        configuration:
          title: "Products"
          fields:
            - name: "Name"
              data_path: "products[*].name"
            - name: "Price"
              data_path: "products[*].price"
  
  custom-data:
    components:
      # Hand-Build Component (no llm_configure or configuration)
      - component: my-custom-component
```

This configuration allows LLM to choose between table and cards for product lists based on user intent, while still controlling the exact fields shown in cards view.

### Loading YAML Configuration

You can load one or several YAML config files which are merged into one configuration where the last config has the highest precedense.
Field `data_types` is merged so having different keys in different yamls are merged into one `data_types` configuration.

#### From File Path

```python
from next_gen_ui_agent import NextGenUIAgent
from next_gen_ui_agent.agent_config import read_config_yaml_file

# Load configuration from files
config = read_config_yaml_file(["path/to/config.yaml", "/path/to/config2.yaml"])
agent = NextGenUIAgent(config=config)
```

#### From YAML String

```python
from next_gen_ui_agent import NextGenUIAgent

yaml_config = """
component_system: json
component_selection_strategy: two_llm_calls
"""

# Pass YAML string directly to constructor
agent = NextGenUIAgent(config=yaml_config)
```
