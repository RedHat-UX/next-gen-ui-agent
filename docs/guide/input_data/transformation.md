# Input Data Transformation

If structured `Input Data` are not in JSON format necessary for *UI Agent* processing, data transformation can be used to bring 
them to this format and related [data structures](structure.md).

## Configuring default data transformation for UI Agent

Default data transformer can be [configured for the UI Agent](../configuration.md#data_transformer-str-optional). If not configured [JSON transformer](#json-transformer) is used.

If the transformer was not configured for a given data type, by default the system will try to auto detect the input type, unless this feature is [disabled through configuration](../configuration.md#enable_input_data_type_detection-bool-optional). If no type can be detected the [configured default transformer](#configuring-default-data-transformation-for-ui-agent) will be used.

## Configuring data transformation auto detection

### Usage

Auto detection is turned on by default and implemented in the most computationally efficient way to minimise its processing time. However, if you use the agent always with predefined types or the configured default transformer is all you need then it makes sense to turn off auto detection and optimise the performance.

The best use case for auto detection is if you're uncertain of some data types that may be provided to NextGenUI agent as input. Still, if you know that at least some data types always return certain format of content then it doesn't make sense to rely on auto detection feature but rather [configure the transformer](#configuring-data-transformation-for-data-type). In effect auto detection logic will be executed only when it's realy needed for those unpredictable data sources.

### How it works

When enabled and [default transformer was not configured for a given data type](../configuration.md#data_transformer-str-optional_1) the agent will run through detection methods provided in transformers' code trying to find one that confirms the input data structure matches particular transformer type. Whichever will match first will be used to transform the input data. In case none will be matched the [configured default data transformer](../configuration.md#data_transformer-str-optional) will be used.

If you disable this setting (`False`), the code will directly rely on what was configured for particular `data_type` or the default `data_transformer`.

### Configuration examples

**Example - Disabling auto-detection:**

```python
config = {
    "enable_input_data_type_detection": False,
    "data_transformer": "json"  # Always use JSON
}
```

**Example - Enabling auto-detection (default):**

```python
config = {
    "enable_input_data_type_detection": True  # Optional, True by default
    # No data_transformer specified - will be auto-detected or fallback to the default JSON transformer will happen
}
```

## Configuring data transformation for data type

Data transformer can be configured per [`InputData.type`](index.md#inputdata-object-fields) which ensures that particular transformation will be executed on the incoming data. In case such configuration is not provided the system may rely on [automatic data type detection](#configuring-data-transformation-auto-detection) (enabled by default). However, at any given time if particular data source is known to return a particular format of data it's better to configure it via the `data_transformer` setting rather than rely on auto detection due to lower performance and potential incorrect type detections.

Example of the [yaml config](../configuration.md#data_transformer-str-optional_1):

```yaml
data_types:
  movie.detail:
    data_transformer : yaml
    ...
```

## OOTB transformers

Few OOTB transformers are provided in the [UI Agent Core package](../ai_apps_binding/pythonlib.md). As it's an optional feature we also mention whether [auto detection](#configuring-data-transformation-auto-detection) is supported by a particular transformer.

### JSON transformer

Transformer name: `json`

Default transformer used for JSON data.

Auto detection: Supported

### YAML transformer

Transformer name: `yaml`

As [`YAML`](https://yaml.org) is another form how to express the same data structures as JSON, conversion is very straighforward.

Auto detection: Supported

### CSV transformers

Transformer name: `csv-comma`, `csv-semicolon`, `csv-tab`

This transformer takes CSV formatted text with delimiter indicated in the transformer name.
`"` character is used as quotation mark in the case delimiter or new line is present in the CSV value.
First row is used as field names, other rows are converted into [array of objects](../input_data/structure.md#array-of-objects-input-data), where 
field names from the first row are used.
Field names are sanitized so JSONPath can work with them easily.

Field values are trimmed from leading/trailing white spaces, and converted from `String` to `Boolean` or `Number` if possible.

Auto detection: Supported

### Fixed Width Columns Table transformer

Transformer name: `fwctable`

Similar to the CSV transformer, produces [array of objects](../input_data/structure.md#array-of-objects-input-data), 
but expects that columns of the table have fixed width in number of characters. First row is used as field names.
It expects at least two consecutive white characters as a column separator on the first row, so one white character can be used in the column label/field name.

Field names sanitization and values handling are the same as in case of the CSV transformer.

Example of data in "Fixed Width Column Table" format:

```
Name     Age  Birth city
John Doe 30   New York
Jane Ei  25   Boston
```

Auto detection: Supported

### Noop transformer

Transformer name: `noop`

This transformer keeps input data as a `string`, not as a parsed JSON tree. Useful if large chunk of unformatted text must be passed to the UI component.

For [Hand-Build Components](../data_ui_blocks/hand_build_components.md), text is outputted directly in [the `data` field of their JSON data](../../spec/component.md#hand-build-component-aka-hbc).

If LLM processing has to be applied, text is shortened to 1000 characters to save LLM's context and wrapped into JSON object with one field.

Auto detection: Not supported

## Writing own transformer

UI Agent core package allows to add new data transformers. [Stevedore framework](https://pypi.org/project/stevedore/) is used, so you only 
have to implement your own python module, and install it to the *UI Agent*.

To implement transformer, you have to:

1. Add `next-gen-ui-agent` dependency to your python module

2. Implement class extending [`next_gen_ui_agent.types.InputDataTransformerBase`](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/libs/next_gen_ui_agent/types.py#L413). Be sure object structure returned from the
   transformation matches defined rules for values access by [`jsonpath_ng`](https://pypi.org/project/jsonpath-ng/)
   and JSON serialization by [Pydantic `model_dump_json()`](https://docs.pydantic.dev/latest/concepts/serialization/#modelmodel_dump_json).
   Implement correct error handling, write unit tests. 
   You can find [examples of transformers and their unit tests in UI Agent core source code](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs/next_gen_ui_agent/input_data_transform).

3. Optionally you can also provide format [auto detection](#configuring-data-transformation-auto-detection) for your transformer by overriding the `detect_my_data_structure` method provided in our base class. If the implementation is not provided by default the method returns `False` effectively meaning that input data format for this transformer will be never auto detected.

4. [Register your transformer using Stevedore under `next_gen_ui.agent.input_data_transformer_factory` namespace](https://docs.openstack.org/stevedore/latest/user/tutorial/creating_plugins.html#registering-the-plugins) in your python module. Use unique transformer name.

```
   entry_points={
        'next_gen_ui.agent.input_data_transformer_factory': [
            'my_transformer_name = transformer_example:MyTransformer'
        ],
    },
```