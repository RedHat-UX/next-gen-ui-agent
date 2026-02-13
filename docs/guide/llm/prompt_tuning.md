# System Prompt Tuning

The Next Gen UI Agent uses carefully crafted system prompts to instruct the LLM to select and configure UI components. While the default system prompts work well for general use cases, 
you may want to customize them for domain-specific applications or to optimize for specific LLM characteristics.

System prompt is constructed dynamically from smaller bits described in this chapter, to match different use cases requested in InputData, it is mainly bound to the processed `data_type`.

Default prompt bits are hardcoded in the agent, they can be customized at multiple levels:

- **Global level**: Via `config.prompt` - applies to all data types if not overrident
- **Per-data-type level**: Via `config.data_types[type].prompt` and `config.data_types[type].components[component].prompt`- override applied to specific input data types (tool call names are used here in many cases)

Then there is an "user prompt" passed to the LLM for each inference run, which contains input data itself and real user prompt asked by the user, passed from the calling AI assistant to be processed. 
They are separated by clear headers, which can be used in the system prompt to reference individual parts to better instruct LLM how to process them. 
LLM User prompt can't be customized.

Example of the user prompt passed to the LLM:

```
=== User query ===
Show me the Toy Story poster.

=== Data ===
{
  "movie-detail": {
    "title": "Toy Story",
    "pictureUrl": "https://movies.org/posters/toystory.png",
    "trailerUrl": "https://movies.org/trailers/toystory.mp4",
    "revenue": 458000000,
    "released": "1995"
  }
}
```

## LLM calling strtegies

UI agent implements two LLM calling strategies. 
Default "one step" strategy uses just one LLM call both to select UI component and configure it.
Then there is also an experimental "two step strategy", which uses first LLM call only to select UI component type, then second LLM call to configure it. We haven't seen any 
improvements using this strategy (it was even worse in some cases than one step), and it is also slower and more expensive (more LLM tokens used). It is kept mainly for experimental purposes, not recomended for real world use.

## Understanding the system prompt structure

Each system prompt used for LLM consists of two parts:

1. **Initial Section** (configurable): Instructions, rules, and context not specific for component. Generic instructions for the LLM role and rules forcing expected json output format.
2. **Components Section** (automatic): Component specific descriptions, examples, and rules - contains component specific parts, only allowed/relevant components for each inference run are put into actual system prompt.

## Available Customization Points

The configurable sections are defined in the agent configuration under the global `prompt` key or data_type specific `data_types[data_type].prompt` key.

### System Promp initial section

The main initial part of the system prompt that instructs the LLM to select a component and configure it. It also forces LLM to produce expected json output. 
UI agent code performs validation of that JSON, but it also provides sanitizations for some parts to prevend unnecessary errors even if LLM response is not only json. 
Eg. if LLM responds with plain text containing JSON part, that JSON part is only taken into further processing. 
Produced JSONPaths for values pickups from the input data structure are also sanitized in the postprocessing. 

InputData are also pre-processed before LLM inference to make LLM processing faster and cheaper. Mainly arrays are shrink to contain two items only, and information 
about real array size is provided in the field name.

Key: **`system_prompt_start`**

**Example:**

```yaml
prompt:
  system_prompt_start: |
    You are an expert financial data visualization assistant.
    
    RULES:
    - Generate valid JSON only
    - Prioritize clarity and accuracy for financial data
    - Select exactly one component from the AVAILABLE UI COMPONENTS list
    - Include fields: component, title, reasonForTheComponentSelection, confidenceScore, fields
    - Each field must have: name, data_path
    
    JSONPATH REQUIREMENTS:
    - Use precise JSONPath expressions
    - For arrays, always use [*] notation
    - Include full nested paths (e.g., items[*].order.total)
    
    AVAILABLE UI COMPONENTS:
```

**Important:** List of component available for the selection is appended just behind this part, so you can end it with header which is referenced in the previous instructions. 
Then charts specific instructions are optinally appende, and Examples of the json output, see next chapters.

When using `component_selection_strategy: two_llm_calls`, similar customization options are available through `twostep_step1select_system_prompt_start` (for step 1 component selection) and `twostep_step2configure_system_prompt_start` (for step 2 field configuration). These work analogously to the one-step strategy prompt. Note that `twostep_step2configure_system_prompt_start` requires a `{component}` placeholder.

### Chart Instructions Template

Both strategies use chart instructions when at least one chart component is available for selection. You can customize the structure of this section. You can use few placeholders here, their content is generated for available chart components.

Key: **`chart_instructions_template`**

**Example:**

```yaml
prompt:
  chart_instructions_template: |
    CHART VISUALIZATION GUIDELINES:
    
    Available Chart Types:
    {charts_description}
    
    Required Fields per Chart Type:
    {charts_fields_spec}
    
    Chart Selection Rules:
    - Don't add unrequested metrics
    {charts_rules}
    
    Chart Configuration Examples:
    {charts_inline_examples}
```

**Placeholders:**

These placeholders are replaced with content generated from the [Component-Specific Prompt Customization](#component-specific-prompt-customization). Only chart components allowed/relevant for the every inference run are included here:

- `{charts_description}`: Content from `chart_description` field for each allowed chart component
- `{charts_fields_spec}`: Content from `chart_fields_spec` field for each allowed chart component
- `{charts_rules}`: Content from `chart_rules` field for each allowed chart component
- `{charts_inline_examples}`: Content from `chart_inline_examples` field for each allowed chart component

You can reorder sections, change headings, or add additional instructions. The common rule "- Don't add unrequested metrics" is shown as an example - include any common rules you want in your template text.

### Examples Customization

In addition to customizing the initial system prompt sections and chatr instructions, you can also customize the response examples that help guide the LLM to produce correctly formatted json output.

Examples can be customized using two keys:

1. **examples_normalcomponents**: Customize examples for normal (no chart) UI components like table, cards, and image components
2. **examples_charts**: Customize examples for chart components

Both types of examples are automatically combined and included in the system prompt when their respective component types are enabled/allowed for inference run.

```yaml
prompt:
  # Customize normal component examples
  examples_normalcomponents: |
    Example for financial transactions table:
    {
        "title": "Transaction History",
        "reasonForTheComponentSelection": "Displaying multiple transaction records with detailed fields",
        "confidenceScore": "95%",
        "component": "table",
        "fields": [
            {"name":"Transaction ID","data_path":"transactions[*].id"},
            {"name":"Amount","data_path":"transactions[*].amount"},
            {"name":"Date","data_path":"transactions[*].date"}
        ]
    }
  
  # Customize chart examples
  examples_charts: |
    Example for revenue comparison:
    {
        "title": "Quarterly Revenue",
        "reasonForTheComponentSelection": "Comparing revenue across quarters",
        "confidenceScore": "90%",
        "component": "chart-bar",
        "fields": [
            {"name":"Quarter","data_path":"data[*].quarter"},
            {"name":"Revenue","data_path":"data[*].revenue"}
        ]
    }
```

**Notes:**

- Examples are automatically combined: normal component examples followed by chart examples (if applicable)
- Examples are only included if relevant components are enabled in `selectable_components` or `data_type.components` configuration 
- You can customize just `*_normalcomponents`, just `*_charts`, or both
- Examples mainly define the JSON output format expected by the selection strategy
- Two-step strategy step2 examples are also configurable via component related prompt bits (`twostep_step2configure_example`)

### Component-Specific Prompt Customization

In addition to customizing the initial system prompt sections described above, you can also customize component-specific metadata that appears in the generated section of the prompt:

- **Component description**: Description of the component usage related to input data type/shape and user prompt
- **Chart-specific instructions**: Fields, rules, and examples for chart components
- **Step 2 configuration rules and examples**: For the two-step strategy's field configuration phase

These customizations can be applied globally (via `prompt.components`) or per-data-type (via `data_types[type].components[component].prompt`), providing fine-grained control over how the LLM perceives each component.

For detailed information about component-specific prompt customization, including precedence rules and configuration examples, see [Prompt Customization for Component Selection](../data_ui_blocks/index.md#prompt-customization-for-component-selection).

## Best Practices

### 1. Start with Defaults

Before customizing, test the default prompts with your use case. Only customize if you encounter issues or have specific requirements.

### 2. Preserve Key Elements

When customizing, make sure to include:

- Reference to the specific parts of the user prompt
- Component type selection instructions
- JSON output requirement
- Required output fields
- JSONPath usage guidelines

### 3. Test Thoroughly

After customizing prompts:

1. Test with various data structures - build evaluation dataset and run it using [our Evaluation tool](evaluations.md)
2. Verify JSONPath expressions are correct
3. Check that confidence scores are reasonable
4. Ensure component selection is appropriate

### 4. Domain-Specific Instructions

Add domain-specific context to improve results:

```yaml
prompt:
  system_prompt_start: |
    You are an advanced UI design assistant visualizing e-commerce data for business analytics dashboards.
    Select the best UI component to visualize the Data based on User query.
    
    DOMAIN CONTEXT:
    - Revenue and sales metrics are critical
    - User behavior patterns should be highlighted
    - Compare periods when temporal data is available
    
    RULES:
    - Generate valid JSON only
    ...
```

### 5. LLM-Specific Tuning

Different LLMs may respond better to different prompt styles:

- **Smaller models** (2B-3B): Use concise, direct instructions
- **Medium models** (7B-13B): Can handle more context and examples
- **Large models** (70B+): Benefit from detailed reasoning instructions

## Debugging Custom Prompts

What to do if your custom prompts aren't working as expected:

1. **Check LLM interactions**: Use any provided debug tool to see really used system prompts
2. **Validate placeholders**: Ensure `{component}` and other placeholders are used correctly
3. **Test incrementally**: Start with small changes from the default
4. **Verify syntax**: YAML multiline strings require proper indentation


You can use few options to see really used system prompts.

### System prompts output from evaluation tool

This is primary tool for evaluation driven system prompt tuning. After each [evaluation tool](evaluations.md) run, 
`tests/ai_eval_components/errors/agent_system_prompts.txt` file is available with all system prompts used during the evaluations.

### Command-line tool

The `debug_system_prompt` commandline tool provided in the `next_gen_ui_agent` module allows you to inspect the actual system prompts 
used by the agent for different configurations and data types.

Just clone source repository, [setup development environment](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/CONTRIBUTING.md), and run the tool using `pants`
from the project root directory. LLM is not used by this tool, it just prints system prompts.

#### Usage

**Basic usage:**
```bash
pants run libs/next_gen_ui_agent:debug_system_prompt
```

**With UI agent configuration file:**

```bash
pants run libs/next_gen_ui_agent:debug_system_prompt -- --config-path my-config.yaml
```

#### Command-line Arguments

- `--config-path PATH` - Path to YAML config file (can be specified multiple times for config merging)
- `--strategy {one_llm_call,two_llm_calls}` - Component selection strategy (defaults to config file value then to `one_llm_call`)
- `--data-type TYPE` - Optional data type for data-type-specific prompt inspection. Global prompt is shown if not provided.
- `--component COMPONENT` - For two-step strategy: specific component name to show step2 system prompt (e.g., `table`, `chart-bar`)
- `--selectable-components COMP1 COMP2 ...` - Override which components are selectable (defaults to config file value then to all)

#### Examples

**Inspect one-step strategy with custom data type:**

```bash
pants run libs/next_gen_ui_agent:debug_system_prompt -- \
  --config-path config.yaml \
  --data-type "k8s:deployment"
```

**Inspect two-step strategy step2 prompt for a specific component:**

```bash
pants run libs/next_gen_ui_agent:debug_system_prompt -- \
  --strategy two_llm_calls \
  --component chart-bar \
  --data-type "metrics:timeseries"
```

**Test merged configurations:**

```bash
pants run libs/next_gen_ui_agent:debug_system_prompt -- \
  --config-path base-config.yaml \
  --config-path overrides.yaml
```

### Debug view in the E2E test app

You can use Debug console in the [E2E test application](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/tests/ngui-e2e) to see system prompt used for every run.

### Application logging from agent core

You can enable `DEBUG` level for the core module application logging for `component_selection_llm_onestep.py` or `component_selection_llm_twostep.py` file to see 
system prompt in the application logs. 
Mainly usefull for production/runtime debugging.

## Further Reading

* [Configuration reference](../configuration.md)