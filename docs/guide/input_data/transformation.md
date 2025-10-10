# Input Data Transformation

If structured `Input Data` are not in JSON format necessary for *UI Agent* processing, data transformation can be used to bring them to this format and data structures.

## Configuring data transformation for data type

Data transformer can be configured per [`InputData.type`](index.md#inputdata-object-fields), so it has to be defined to use transformation.

Example of the [yaml config](../configuration.md):

```yaml
data_types:
  movie.detail:
    data_transformer : yaml
    ...
```

Few OOTB transformers is provided in the [UI Agent Core package](../ai_apps_binding/pythonlib.md):

### YAML transformer

Transformer name: `yaml`

As [`YAML`](https://yaml.org) is another form how to express the same data structures as JSON, conversion is very straighforward.

### CSV transformers

Transformer name: `csv-comma`, `csv-semicolon`, `csv-tab`

This transformer takes CSV formatted text with delimiter indicated in the transformer name.
`"` character is used as quotation mark in the case delimiter or new line is present in the CSV value.
First row is used as field names, other rows are converted into [array of objects](../input_data/structure.md#array-of-objects-input-data), where 
field names from the first row are used.
Field names are sanitized so JSONPath can work with them easily.

Field values are trimmed from leading/trailing white spaces, and converted from `String` to `Boolean` or `Number` if possible.

## Writing own transformer

UI Agent core package allows to add new data transformers. [Stevedore framework](https://pypi.org/project/stevedore/) is used, so you only 
have to implement your own python module, and install it to the *UI Agent*.

To implement transformer, you have to:

1. Add `next-gen-ui-agent` dependency to your python module

2. Implement class extending [`next_gen_ui_agent.input_data_transform.types.InputDataTransformerBase`](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs/next_gen_ui_agent/input_data_transform/types.py). Be sure object structure returned from the
   transformation matches defined rules for values access by [`jsonpath_ng`](https://pypi.org/project/jsonpath-ng/)
   and JSON serialization by [Pydantic `model_dump_json()`](https://docs.pydantic.dev/latest/concepts/serialization/#modelmodel_dump_json).
   Implement correct error handling, write unit tests. 
   You can find [examples of transformers and their unit tests in UI Agent core source code](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs/next_gen_ui_agent/input_data_transform).

3. [Register your transformer under `next_gen_ui.agent.input_data_transformer_factory` namespace](https://docs.openstack.org/stevedore/latest/user/tutorial/creating_plugins.html#registering-the-plugins) in your python module. Use unique transformer name.

```
   entry_points={
        'next_gen_ui.agent.input_data_transformer_factory': [
            'my_transformer_name = transformer_example:MyTransformer'
        ],
    },
```