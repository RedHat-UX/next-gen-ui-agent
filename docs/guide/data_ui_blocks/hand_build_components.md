# Hand Build Components

## What is "*Hand Build Component*" (aka `HBC`)

Do you already have an existing UI component to visualize some backend data? Or do you need some functionality
currently not supported in *UI Agent* generic UI components.
Or does LLM generated view not suits your needs and you want to have well-tuned view for that piece of data?

No problem, you can use *Hand Buil Component* and register it into *UI Agent*, together with frontend code,
to render the view for that data piece. 

AI powered component selection and configuration is NOT performed for HBC.

## How are HBC selected

HBC selection is performed for each piece of `InputData` sent to *UI Agent* for processin, before AI powered 
component selection happens.

### Mapping from `InputData.type`

This approach is useful if you want to completely decouple UI component selection from *Controlling assistant* into *UI Agent*.

Each [`InputData`](../input_data/index.md#inputdata-object-fields) sent to *UI Agent* can have `type` defined, which is a 
string identifier of the data piece type eg. `movies:movie-detail`, `movies:movies-list`, `movies:actor-detail`. It is up 
to *Controlling assistant* to define and use these types, but it might be a good idea to use tree like hierarchy here. 
Other option is to use name of the LLM tool used to load backend data, as implemented in some of our AI framework bindings.

During the *UI Agent* construction, you can [configure mapping from `InputData.type`](../configuration.md#data_types-dictstr-agentconfigdatatype-optional) to hand build component name like:

```python
data_types={
    "movies:movie-detail": { components: [{ component: "movies:movie-detail-view" }]},
    "movies:movies-list": { components: [{ component: "movies:movies-list-view" }]},
}

agent = NextGenUIAgent(
    config=AgentConfig(
        data_types=data_types
    )
)
```

Be cautious when selecting component name for your HBC, as they can be "mixed" with *UI Agent* [dynamic 
components](./dynamic_components.md) in this configuration (every name which is not known dynamic component 
is interpreted as a HBC). Ideally add some prefix to these names, like `movies:` used in the example.

When data piece is send to *UI Agent* for processing, agent consults this mapping, and if `type` is found here, HBC is selected.
If `type` is not found in this mapping, AI powered component selection and configuration is performed for that data piece.

*UI Agent*'s' LlamaStack and LanGraph AI framework bindings propagate tool name as 
an [`InputData.type`](../input_data/index.md#inputdata-object-fields), so HBC can be mapped based 
on the tool name of the tool used to load given data.

### Requested in `InputData.hand_build_component_type`

If your *Controlling assistant* needs/is able to directly define HBC component type to visualize some piece of data, it can 
explicitly request it using [`InputData.hand_build_component_type`](../input_data/index.md#inputdata-object-fields). 
Type provided here is not validated in *UI Agent* until 
rendering happens, so make sure rendering code is provided for every component type requested this way.

This HBC selection happens even before mapping from `InputData.type`.

## How is UI rendered for HBC

Once HBC is selected, *UI Agent* core generates [`ComponentDataHandBuildComponent`](../../spec/component.md#hand-build-component-aka-hbc) 
from its "data generation" step, which is propagated into rendering step.

Be cautious when selecting component name for your HBC, as they are "mixed" with *UI Agent* [dynamic 
components](./dynamic_components.md) in the metadata sent to renderer. Ideally add some prefix to these names, like `movies:` used in the example.

It contains these most important fields:

* `component` is identification of the component type (`hand_build_component_type`) coming from the selection process. Hand build code MUST be 
registered for this type in the [UI renderer](../renderer/index.md). That code must be able to take values/fields from `data` and visualize them 
using UI technology/design system used in that renderer. Each of component type has own code for the rendering. 
For details refer documentation of the renderer you are using please.
* `data` are simply parsed JSON data originally sent into *UI Agent*

Example of the [`ComponentDataHandBuildComponent` as JSON](../../spec/component.md#hand-build-component-aka-hbc) :

```json
{
    "id": "4585-8554-af54-54c8",
    "component": "movies:movie-detail-view",
    "data": {
        "title": "Toy Story",
        "year": 1995,
        ...
    }
}
```