# LLM inference

*UI Agent* currently uses LLM to process `User Prompt` and structured [`Input Data`](input_data/index.md) relevant to this prompt.
LLM selects the best UI component to visualize that data, and also configures it by selecting which values from the data have to be shown.

For now, every piece of `Input Data` is processed independently. 
In the future, we expect that conversation history will also be processed to get better UI consistency through conversation.
And that all `Input Data` pieces will be processed at once, to also select which piece should be shown at given conversation step.

To instruct LLM to produce structured output expected by the agent, we use prompt engineering technique.

Parts of the LLM prompt used by the agent can be [customized in its configuration](configuration.md#prompt-agentconfigprompt-optional).

## LLM Evaluations

To evaluate how well a particular LLM is performing on *UI Agent* component selection and configuration task, 
we provide [Evaluation tool and dataset](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/tests/ai_eval_components).

This evaluation currently covers distinct shapes of the input data, and evaluates if LLM generates correct configuration from 
the "technical" point of view. Currently it is not able to evaluate if data values selected to be shown in very generic 
components, like `one-card` or `table`, are good enough. So you have to do this evaluation by yourself still.

Evaluation results for some LLMs are available in `/results` directory.

## Which LLM to use?

### Foundation LLMs
Generally, even very small LLMs, like 3B `Llama 3.2` or 2B `Granite 3.2`, are pretty good at this task. They mostly struggle to 
generate pointers to values in `InputData` for some shapes.

A bit larger models, like 8B `Granite 3.2` or Google `Gemini Flash` and `Gemini Flash Lite` are good in most evaluations.

Improvements on even larger LLMs are not significant, and you pay all the prices for the large LLM - slower speed and more expensive runtime.

It seems that larger LLMs tend to put more values into generic components (more columns in the table or Facts in the card).

### Fine-tuned LLM

LLM finetuning may be beneficial for the UI agent functionality, as UI component type selection and configuration is a relatively narrow AI task.
Finetuning might help to get better results from smaller LLMs, which means better performance and lower cost of the processing.

We provide basic support for finetuning in the [`llm_finetuning` directory](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/llm_finetuning). 
It contains [Google Colab notebook](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/llm_finetuning/finetune_model.ipynb) to finetune 3B or 
8B model using LoRA approach and Unsloth library, and export model to quantized GGUF file runnable using [Ollama](https://www.ollama.com/). 
Finetuning using T4 GPU available on Google Colab for free takes only a few minutes.

Experimental finetuning dataset is provided in the [`training_data` directory](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/llm_finetuning/training_data),
with training data covering distinct aspects of the UI Agent functionality called "skills".
We achieved good results (measured by provided evaluations) on the Llama 3.2 3B model with 27% fewer errors against the base model, 
but finetuning results on the Llama 3.1 8B model are not so good (generated `image` component configuration is broken ;-).

Alternatively, we should build a training dataset mimicking real LLM calls performed by the UI Agent, containing exact user prompts and expected exact responses.

More work is definitely necessary in this area.

## How is LLM really called

[*UI Agent* core library](ai_apps_binding/pythonlib.md) abstracts LLM inference over `InferenceBase` interface. 
Multiple implementations are then provided in some of the [AI Framework and protocols](ai_apps_binding/index.md) bindings, 
including OpenAI compatible API, LlamaStack remote and embedded server, Anthropic/Claude models from proxied Google Vertex AI API etc.

To get repeatable results from the agent, you should always use `temperature=0` when calling the LLM behind this interface.

## Prompt Tuning

The Next Gen UI Agent uses carefully crafted system prompts to instruct the LLM to select and configure UI components. While the default prompts work well for general use cases, you may want to customize them for domain-specific applications or to optimize for specific LLM characteristics.

### Understanding the Prompt Structure

Each prompt consists of two parts:

1. **Initial Section** (configurable): Instructions, rules, and context
2. **Generated Section** (automatic): Component descriptions, examples, and metadata - may contain component specific parts for allowed/relevant components for inference run.

The configurable sections are defined in the agent configuration under the `prompt` key.

### Available Customization Points

#### System Promp initial section


- **`system_prompt_start`**: The main system prompt that instructs the LLM to select a component and configure it in a single call.

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

**Important:** Always end your custom prompt with `AVAILABLE UI COMPONENTS:` header which you reference in previous instructions - the component list will be appended automatically.

When using `component_selection_strategy: two_llm_calls`, similar customization options are available through `twostep_step1select_system_prompt_start` (for step 1 component selection) and `twostep_step2configure_system_prompt_start` (for step 2 field configuration). These work analogously to the one-step strategy prompt. Note that `twostep_step2configure_system_prompt_start` requires a `{component}` placeholder. See the [Configuration Guide](configuration.md#prompt-configuration) for details.

#### Chart Instructions Template

Both strategies use chart instructions when chart components are available. You can customize the structure:

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

These placeholders are replaced with content from the component configuration section (see [Component-Specific Prompt Customization](#component-specific-prompt-customization)). Only chart components allowed/relevant for the every inference run are included here:

- `{charts_description}`: Content from `chart_description` field for each chart component
- `{charts_fields_spec}`: Content from `chart_fields_spec` field for each chart component
- `{charts_rules}`: Content from `chart_rules` field for each chart component
- `{charts_inline_examples}`: Content from `chart_inline_examples` field for each chart component

You can reorder sections, change headings, or add additional instructions. The common rule "- Don't add unrequested metrics" is shown as an example - include any common rules you want in your template text.

#### Component-Specific Prompt Customization

In addition to customizing the initial system prompt sections (described above), you can also customize component-specific metadata that appears in the generated section of the prompt:

- **Component descriptions**: How each component is described to the LLM
- **Chart-specific instructions**: Fields, rules, and examples for chart components
- **Step 2 configuration rules and examples**: For the two-step strategy's field configuration phase

These customizations can be applied globally (via `config.prompt.components`) or per-data-type (via `data_types[type].components[component].prompt`), providing fine-grained control over how the LLM perceives each component.

For detailed information about component-specific prompt customization, including precedence rules and configuration examples, see [Prompt Customization for Component Selection](data_ui_blocks/index.md#prompt-customization-for-component-selection).

#### Examples Customization

In addition to customizing the initial system prompt sections, you can also customize the response examples that help guide the LLM to produce correctly formatted output.

Examples can be customized at two levels:

1. **Normal Component Examples**: Customize examples for table, cards, and image components
2. **Chart Component Examples**: Customize examples for chart components

Both types of examples are automatically combined and included in the system prompt when their respective component types are enabled.

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
- Two-step step2 examples are already configurable via component related prompt bits (`twostep_step2configure_example`)

### Best Practices

#### 1. Start with Defaults

Before customizing, test the default prompts with your use case. Only customize if you encounter issues or have specific requirements.

#### 2. Preserve Key Elements

When customizing, make sure to include:

- JSON generation requirement
- Component selection instruction
- Required output fields
- JSONPath usage guidelines

#### 3. Test Thoroughly

After customizing prompts:

1. Test with various data structures - build evaluation dataset and run it using [our Evaluation tool](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/tests/ai_eval_components)
2. Verify JSONPath expressions are correct
3. Check that confidence scores are reasonable
4. Ensure component selection is appropriate

#### 4. Domain-Specific Instructions

Add domain-specific context to improve results:

```yaml
prompt:
  system_prompt_start: |
    You are visualizing e-commerce data for business analytics dashboards.
    
    DOMAIN CONTEXT:
    - Revenue and sales metrics are critical
    - User behavior patterns should be highlighted
    - Compare periods when temporal data is available
    
    RULES:
    - Generate valid JSON only
    ...
```

#### 5. LLM-Specific Tuning

Different LLMs may respond better to different prompt styles:

- **Smaller models** (2B-3B): Use concise, direct instructions
- **Medium models** (7B-13B): Can handle more context and examples
- **Large models** (70B+): Benefit from detailed reasoning instructions

### Debugging Custom Prompts

If your custom prompts aren't working as expected:

1. **Check LLM interactions**: Enable debug logging to see actual prompts sent to the LLM
2. **Validate placeholders**: Ensure `{component}` placeholder is used correctly
3. **Test incrementally**: Start with small changes from the default
4. **Verify syntax**: YAML multiline strings require proper indentation

### Complete Example

Here's a complete configuration example for a financial analytics application:

```yaml
component_system: json
selectable_components:
  - table
  - chart-bar
  - chart-line
  - one-card

component_selection_strategy: one_llm_call

prompt:
  system_prompt_start: |
    You are a financial data visualization expert.
    
    RULES:
    - Generate valid JSON only
    - Prioritize financial KPIs and trends
    - Use tables for detailed data, charts for trends
    - Include currency and percentage formatting context in field names
    - Component must be from AVAILABLE UI COMPONENTS list
    - Required fields: component, title, reasonForTheComponentSelection, confidenceScore, fields
    
    JSONPATH REQUIREMENTS:
    - Analyze data structure carefully
    - Use [*] for arrays (e.g., transactions[*].amount)
    - Include full nested paths
    - No calculations in data_path
    
    AVAILABLE UI COMPONENTS:
  
  chart_instructions_template: |
    FINANCIAL CHART GUIDELINES:
    
    Available Chart Types:
    {charts_description}
    
    Field Requirements:
    {charts_fields_spec}
    
    Financial Chart Rules:
    - Don't add unrequested metrics
    - Prefer line charts for time-series financial data
    - Use bar charts for category comparisons
    {charts_rules}
    
    Examples:
    {charts_inline_examples}
  
  components:
    table:
      description: "component to display detailed financial transactions in tabular format"
    chart-line:
      description: "component for financial time-series trends (revenue, expenses, growth)"
```

### Further Reading

- [Configuration Reference](configuration.md#prompt-agentconfigprompt-optional)
- [LLM Evaluations](#llm-evaluations)
- [Component Metadata Customization](configuration.md#components-dictstr-agentconfigpromptcomponent-optional)