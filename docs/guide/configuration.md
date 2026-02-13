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

* [Dynamic component](./data_ui_blocks/dynamic_components.md) with or without pre-defined configuration 
* [Hand Build Component](./data_ui_blocks/hand_build_components.md) with `prompt.description` defined

**Note**: When using [Hand Build Components](./data_ui_blocks/hand_build_components.md) in multi-component configuration, each HBC must have `prompt.description` defined for LLM selection. HBCs can be mixed with dynamic components.


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


##### `prompt` [`AgentConfigPromptComponent`, optional]

Customize LLM prompts for this specific component when it's used in multi-component selection.
Has the same fields as global [`prompt.components`](#components-dictstr-agentconfigpromptcomponent-optional).
Overrides global prompt configuration for this component in this data_type context.

Per-component prompt overrides take the highest precedence during prompt construction. This allows you to provide data_type-specific guidance for component selection.

For detailed explanation of how prompt construction works and field descriptions, see [Data UI Blocks - Prompt Customization](data_ui_blocks/index.md#prompt-customization-for-component-selection).

**Note for Hand-Build Components (HBCs)**: 
- **Required in multi-component**: At least `description` field must be defined when multiple components are configured
- **Used fields**: Only `description` is used for LLM component selection
- **Accepted but not used**: `chart_*` and `twostep_step2_*` fields are accepted in configuration but not used for HBCs


#### `prompt` [`AgentConfigPromptBase`, optional]

Optional prompt configuration for this data type. Overrides global prompt settings from `AgentConfig.prompt`. 

All fields from `AgentConfigPromptBase` are available (system prompts, examples, chart instructions) and take precedence over global configuration. This allows different data types (typically from different tools or data sources) to use customized LLM prompts.

See [Prompt Tuning](llm/prompt_tuning.md) and [Per-Data-Type Prompt Customization](data_ui_blocks/index.md#per-data-type-prompt-customization) for detailed information and examples.

**Available fields**: All fields from global `prompt` configuration except `components`:
- `system_prompt_start`
- `twostep_step1select_system_prompt_start`
- `twostep_step2configure_system_prompt_start`
- `chart_instructions_template`
- `examples_normalcomponents`
- `examples_charts`
- `twostep_step1select_examples_normalcomponents`
- `twostep_step1select_examples_charts`


### `prompt` [`AgentConfigPrompt`, optional]

Configuration for customizing LLM system prompts used by the agent.

#### `components` [`dict[str, AgentConfigPromptComponent]`, optional]

This allows you to override component related parts of the prompt.
Dictionary mapping component names to their prompt part overrides. Keys must be valid component names, 
identification of the supported [Dynamic Component](./data_ui_blocks/dynamic_components.md) can be used here, e.g., `table`, `chart-bar`, `one-card`.
Only specified fields are overridden for the prompt, unspecified fields retain their default values.

##### `description` [`str`, optional]

Override the main component description for the component selection. This helps the LLM understand when to use this component.

##### `twostep_step2configure_example` [`str`, optional]

Override the example shown to the LLM during component configuration when using `two_llm_calls` strategy. 
Provide a JSON example showing how fields should be selected for this component.

##### `twostep_step2configure_rules` [`str`, optional]

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


#### `system_prompt_start` [`str`, optional]

Override the initial system prompt section for the one-step strategy (used when `component_selection_strategy` is `one_llm_call`). 

The custom prompt should include the `AVAILABLE UI COMPONENTS:` heading at the end - the component list, examples and chart instructions will be automatically appended after this heading.

If not set, uses the default hardcoded prompt. For detailed information and examples, see [Prompt Tuning](llm/prompt_tuning.md).


#### `chart_instructions_template` [`str`, optional]

Override the chart instructions template used in both strategies when chart components are available.

Supports placeholders that will be replaced with dynamically generated component-specific content:
- `{charts_description}` - Chart type descriptions
- `{charts_fields_spec}` - Required fields for each chart type  
- `{charts_rules}` - Component-specific rules
- `{charts_inline_examples}` - Chart configuration examples

If not set, uses the default hardcoded template. For detailed information and examples, see [Prompt Tuning](llm/prompt_tuning.md).


#### `examples_normalcomponents` [`str`, optional]

Override the normal component examples (table, cards, image) for one-step strategy.

If not set, uses default hardcoded examples. For detailed information, see [Prompt Tuning - Examples Customization](llm/prompt_tuning.md).


#### `examples_charts` [`str`, optional]

Override the chart component examples for one-step strategy.

If not set, uses default hardcoded examples. For detailed information, see [Prompt Tuning - Examples Customization](llm/prompt_tuning.md#examples-customization).


#### `twostep_step1select_system_prompt_start` [`str`, optional]

Override the initial system prompt section for two-step strategy's first step (component selection, used when `component_selection_strategy` is `two_llm_calls`). Works like `system_prompt_start`.

If not set, uses the default hardcoded prompt.


#### `twostep_step2configure_system_prompt_start` [`str`, optional]

Override the initial system prompt section for two-step strategy's second step (field configuration, used when `component_selection_strategy` is `two_llm_calls`). Must contain `{component}` placeholder.

If not set, uses the default hardcoded prompt.


#### `twostep_step1select_examples_normalcomponents` [`str`, optional]

Override normal component examples (table, cards, image) for two-step strategy's first step (used when `component_selection_strategy` is `two_llm_calls`). Works like `examples_normalcomponents`.

If not set, uses default hardcoded examples.


#### `twostep_step1select_examples_charts` [`str`, optional]

Override chart component examples for two-step strategy's first step (used when `component_selection_strategy` is `two_llm_calls`). Works like `examples_charts`.

If not set, uses default hardcoded examples.


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
                twostep_step2configure_rules="Always include ID, name, and date fields"
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
      twostep_step2configure_rules: "Always include ID, name, and date fields"
    
    chart-bar:
      description: "Bar chart is suitable for values comparison"
      chart_description: "Compare sales metrics across products or regions"
      chart_rules: "Show values in thousands"
    
    one-card:
      description: "Show detailed information for a single business entity"
      twostep_step2configure_rules: "Include key identifiers and status information"
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
      # Hand-Build Component with required description
      - component: my-custom-component
        prompt:
          description: "Use custom component for special data format"
```

This configuration allows LLM to choose between table and cards for product lists based on user intent, while still controlling the exact fields shown in cards view.

### Per-Component Prompt Customization

Customize LLM prompts at the component level within data_types for fine-grained control:

```yaml
---
# Global prompt (applies to all data types by default)
prompt:
  components:
    table:
      description: "Generic table description"

data_types:
  product-data:
    components:
      # Dynamic component with per-component prompt override
      - component: table
        prompt:
          description: "Use table for structured product listings with many items"
      
      # HBC with required description (multi-component scenario)
      - component: products:listing-with-parameters
        prompt:
          description: "Use this listing if user also wants to see products parameters"
      
      # Chart with custom prompt
      - component: chart-bar
        llm_configure: true
        prompt:
          description: "Use bar chart for product category comparisons"
          chart_description: "Product sales by category"
  
  movie-data:
    components:
      # Same table component, different prompt for movies
      - component: table
        prompt:
          description: "Use table for movie listings with ratings and genres"
```

Per-component prompts override global prompts, allowing different selection behavior per data_type.

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
