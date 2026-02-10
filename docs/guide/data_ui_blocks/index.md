# Data UI Blocks

Next Gen UI Agent produces UI components for `InputData` passed to it, to visualize the data the best as possible. We call this output *Data UI Blocks*.

Different types of *Data UI Blocks* can be used, depending on how are UI components selected and configured. For now these types are available:

* [Dynamic components](dynamic_components.md) - fully dynamic components we provide [UI rendering code](../renderer/index.md) for
* [Hand build components](hand_build_components.md) - you have to provide own UI rendering code


## Selection and Configuration process

UI Agent provides flexible and highly configurable UI component selection and configuration process to serve distinct use cases.
It ranges from fully LLM powered selection and configuration to tightly, per input data type, configured components, without LLM need.

The process goes over these steps in this order:

1. [Hand Build Component requested in `InputData`](./hand_build_components.md#requested-in-inputdatahand_build_component_type) - no LLM required
2. When `InputData.type` is set, component can be defined for it in the [agent config](../configuration.md#components-listagentconfigcomponent-optional):
      1. **Single component configured**:
          - [Hand Build Component](./hand_build_components.md#mapping-from-inputdatatype) - no LLM required
          - [pre-configured Dynamic Component](./dynamic_components.md) - no LLM required
      2. **Multiple components configured** - LLM selects best option:
          - LLM powered selection from configured Dynamic Components (with or without pre-configuration)
          - HBCs can be mixed with other components (each HBC must have `prompt.description` defined)
          - Configuration generation for Dynamic Components is controlled by `llm_configure` flag:
              - `llm_configure=true` (default): LLM selects component AND generates configuration
              - `llm_configure=false`: LLM only selects component, uses pre-defined configuration
          - LLM System prompt contains only configured components for focused selection
          - Each component can have custom `prompt` configuration to override default one for better LLM fine-tuning.
3. Fully LLM selected and configured [Dynamic Component](./dynamic_components.md) - LLM selects from all available components

If only *"no LLM required"* use cases are used in your deployment (step 1 and 2.1), the *UI Agent* can be instantiated without LLM (without LLM Inference provider).

*UI Agent* by default selects from all the supported Dynamic Components in step `3`, but you can narrow choice to the components suitable for your application
[in the configuration](../configuration.md#selectable_components-setstr-optional).

Note that `InputData.type` often contains name of the LLM tool used to load the data (eg. in our [AI framework bindings](../ai_apps_binding/index.md)), 
so tool names are directly used for binding to UI components in this case.

### Example configuration

In the case of this example [yaml configuration](../configuration.md#yaml-configuration), selection and configuration works this way:

* For input data with `type`=`movies:movie-detail`, Hand Build Component with name `movies:movie-detail-view` is used. Its specific 
  rendering code has to be provided in used UI renderer.
* For input data with `type`=`movie:movies-list`, `table` Dynamic Component is used, configured to show three columns and "Movies" title.
* For input data with `type`=`movie:actors-list`, LLM selects between `table` and `set-of-cards` based on user prompt and data. Table uses pre-configured fields, cards are fully configured by LLM.
* For other input data, AI/LLM powered selection and configuration is performed from all available components.

```yaml
---
data_types:
  movies:movie-detail:
    components:
      - component: movies:movie-detail-view
  
  movie:movies-list:
    components:
      - component: table
        configuration:
          title: "Movies"
          fields:
            - name: "Name"
              data_path: "$..movies[].name"
            - name: "Year"
              data_path: "$..movies[].year"
            - name: "IMDB Rating"
              data_path: "$..movies[].imdb.rating"
  
  movie:actors-list:
    components:
      # LLM selects best option based on user prompt and data
      - component: table
        llm_configure: false  # Use pre-configured fields
        configuration:
          title: "Actors"
          fields:
            - name: "Name"
              data_path: "$..actors[].name"
            - name: "Age"
              data_path: "$..actors[].age"
      - component: set-of-cards
        llm_configure: true  # LLM generates fields
```

## Prompt Customization for Component Selection

For agent decisions, the LLM uses system prompt to select the best component based on the user's query and data and configure it. This prompt can be customized at multiple levels with increasing specificity.

This section focuses on **component-specific prompt customization** (component descriptions, chart instructions, configuration examples). For customizing the **initial system prompt sections** (rules, instructions, strategy-specific prompts), see [Prompt Tuning](../llm/prompt_tuning.md).

### Prompt Override Precedence

Prompts are constructed by merging overrides in this order (later overrides replace earlier ones):

1. **Base prompts**: Default component prompts hardcoded in the agent, see [`COMPONENT_METADATA`](https://github.com/RedHat-UX/next-gen-ui-agent/blob/cf80d1c49f49d1eca282fc656db4afaa6a5eeea2/libs/next_gen_ui_agent/component_selection_common.py#L127C1-L127C19)
2. **Global prompt overrides**: From `config.prompt` fields - applies to all data types
3. **Per-data-type prompt overrides**: From `config.data_types[type].prompt` fields - applies to specific data type (NEW)
4. **Per-component prompt overrides**: From `data_types[type].components[component].prompt` - applies only to this component in this `InputData.type`

Note: Per-component overrides (level 4) only affect component-specific fields (description, chart_*, twostep_step2configure_*), while per-data-type overrides (level 3) affect the overall system prompt structure, examples, and chart instructions.

!!!warning
    Please be aware that one large system prompt is constructed by the UI Agent using these per-component overrides, but also common parts. 
    Final inference results heavily depend on used LLM type, for some change of one component system prompt may also affect other components or overal agent's performance. Mainly smaller LLMs are more sensitive on system prompt changes and interdependencies in it.
    Always use the [evaluation tool](../llm/evaluations.md), and ideally your project specific evaluation dataset, to measure agent's performance when tuning system prompt this way.
    It is always a good idea to start with default prompts fields from [`COMPONENT_METADATA`](https://github.com/RedHat-UX/next-gen-ui-agent/blob/cf80d1c49f49d1eca282fc656db4afaa6a5eeea2/libs/next_gen_ui_agent/component_selection_common.py#L127C1-L127C19) and gradually fine-tune them while measuring agent's performance.

### Configuration Example

```yaml
# Global prompt customization (applies everywhere)
prompt:
  components:
    table:
      description: "Use table to show multiple items"

data_types:
  movie-data:
    components:
      # This table uses per-component override (takes precedence)
      - component: table
        prompt:
          description: "Use table for movie listings with many items but without actors"
          twostep_step2configure_rules: "Always include title and year fields."
      
      # HBC with required description
      - component: movies:list-with-actors
        prompt:
          description: "Use this component if user wants to see movies with actors."
      
      # Cards uses global prompt (no per-component override)
      - component: set-of-cards
```

### Prompt customization fields by Component Type

Different component types use different prompt customization fields:

- **All components**: `description` - Main description for component selection. It should 
- **Dynamic components**: `twostep_step2configure_example`, `twostep_step2configure_rules` - Field selection guidance used by two-step strategy only
- **Dynamic Chart components**: `chart_description`, `chart_fields_spec`, `chart_rules`, `chart_inline_examples` - Chart-specific guidance

**For Hand-Build Components (HBCs)**:
- Only `description` field is used for LLM component selection, `chart_*` and `twostep_step2configure_*` fields are not used for HBCs.
- When multiple components include HBCs, each HBC must have `prompt.description` defined

### Per-Data-Type Prompt Customization

In addition to per-component prompt customization described above, you can customize the overall system prompt structure, examples, and chart instructions on a per-data-type basis. This is useful when different data types (typically from different tools or data sources) require different prompting strategies.

#### Available Fields

All fields from `AgentConfigPromptBase` can be customized per data type (everything from global `prompt` configuration except `components`):

- **`system_prompt_start`**: Override initial system prompt for one-step strategy
- **`chart_instructions_template`**: Override chart instructions template
- **`examples_normalcomponents`**: Override normal component examples (one-step)
- **`examples_charts`**: Override chart component examples (one-step)
- **`twostep_step1select_system_prompt_start`**: Override initial prompt for two-step strategy step1
- **`twostep_step2configure_system_prompt_start`**: Override initial prompt for two-step strategy step2
- **`twostep_step1select_examples_normalcomponents`**: Override normal component examples (two-step step1)
- **`twostep_step1select_examples_charts`**: Override chart component examples (two-step step1)

#### Precedence Order

For system prompt construction:
1. Data-type specific prompt (highest priority)
2. Global prompt from `config.prompt`
3. Default hardcoded prompt (lowest priority)

#### Configuration Example

```yaml
# Global prompt configuration
prompt:
  system_prompt_start: |
    You are a generic UI assistant.
    
    AVAILABLE UI COMPONENTS:
  examples_normalcomponents: |
    Generic table example:
    {"component": "table", "title": "Items"}

data_types:
  # Tool A data with specific prompt requirements
  tool-a:result:
    prompt:
      system_prompt_start: |
        You are a Tool A data visualization assistant.
        Focus on key metrics and trends.
        
        AVAILABLE UI COMPONENTS:
      examples_normalcomponents: |
        Tool A table example with metrics:
        {"component": "table", "title": "Tool A Metrics"}
    components:
      - component: table
      - component: chart-bar
  
  # Tool B data with different prompt strategy
  tool-b:result:
    prompt:
      system_prompt_start: |
        You are a Tool B data visualization assistant.
        Emphasize relationships and hierarchies.
        
        AVAILABLE UI COMPONENTS:
      chart_instructions_template: |
        Tool B specific chart guidance:
        {charts_description}
    components:
      - component: table
      - component: set-of-cards
  
  # Tool C uses global prompts (no data-type override)
  tool-c:result:
    components:
      - component: one-card
```

In this example:
- `tool-a:result` data uses Tool A specific prompts and examples
- `tool-b:result` data uses Tool B specific prompts with custom chart instructions
- `tool-c:result` data falls back to global prompts
- Other data types without configuration use global prompts

#### Use Cases

Per-data-type prompt customization is particularly useful for:

1. **Different Tool Outputs**: When integrating multiple tools, each tool's output may benefit from domain-specific prompting
2. **Data Source Variations**: Different data sources (databases, APIs, files) may need different visualization strategies
3. **Multi-Tenant Applications**: Different tenants or customers may have different visualization preferences
4. **A/B Testing**: Test different prompting strategies for the same data type
5. **Language/Locale Variations**: Provide prompts in different languages for different data types

#### Best Practices

1. **Start with Global**: Define global prompts first, then override only what's necessary per data type
2. **Test Thoroughly**: Use the [evaluation tool](../llm/evaluations.md) to measure impact
3. **Document Rationale**: Comment why specific data types need custom prompts
4. **Combine with Per-Component**: Use both per-data-type AND per-component customization for fine-grained control
5. **Monitor Performance**: Small LLMs are more sensitive to prompt changes - validate with your target LLM

### How Prompts Are Used

The system prompt construction process (for multi-component scenarios):

1. **Component lookup**: Strategy determines which components are available for the processed `InputData.type`
2. **Prompt metadata merging**: Applies base → global → per-input-data-type-component prompt overrides
4. **Caching**: Caches the system prompt using `InputData.type` as key for performance
5. **LLM selection**: LLM uses the customized system prompt to select best component

This allows you to:
- Fine-tune component selection per input data type (typically tool call loading data)
- Provide domain-specific guidance for component usage
- Mix HBCs with dynamic components when appropriate
- Maintain different component selection criteria for different input data types
