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

This approach is usefull if you want to completely decouple UI component selection from *Controlling assistant* into *UI Agent*.

Each `InputData` send to *UI Agent* can have `type` defined, which is a string identifier of the data piece
type eg. `movies.movie-detail`, `movies.movies-list`, `movies.actor-detail`. It is up to *Controlling assistant*
to define and use these types, but it might be a good idea to use tree like hierarchy here.

During the *UI Agent* construction, you can define mapping from data piece `type` to `component_type` like:

```python
hbc_mapping={
    "movies.movie-detail": "movie-detail-view",
    "movies.movies-list": "movies-list-view",
}

agent = NextGenUIAgent(
    config=AgentConfig(
        hand_build_components_mapping=hbc_mapping
    )
)
```

When data piece is send to *UI Agent* for processing, agent consults this mapping, and if `type` is found here, HBC is selected.
If `type` is not found in this mapping, AI powered component selection and configuration is performed for that data piece.

*UI Agent*'s' LlamaStack and LanGraph AI framework bindings propagate tool name as an `InputData.type`, so HBC can be mapped based 
on the tool name of the tool used to load given data.

### Requested in `InputData.hand_build_component_type`

If your *Controlling assistant* needs/is able to directly define HBC component type to visualize some piece of data, it can 
explicitly request it using `InputData.hand_build_component_type`. Type provided here is not validated in *UI Agent* until 
rendering happens, so make sure rendering code is provided for every component type requested this way.

This HBC selection happens even before mapping from `InputData.type`.

## How is UI rendered for HBC

Once HBC is selected, *UI Agent* core generates [`ComponentDataHandBuildComponent`](../spec/component.md#hand-build-component) 
from its "data generation" step, which is propagated into rendering step.

It contains these most important fields:

* `component_type` is identification of the component type coming from the selection process. Hand written code MUST be 
registered for this type in the renderer. That code must be able to take values/fields from `data` and visualize them 
using UI technology/design system used in that renderer. Each of component type has own code for the rendering. 
For details refer documentation of the renderer you are using please.
* `data` are simply parsed JSON data sent into *UI Agent*

Example of the `ComponentDataHandBuildComponent` as JSON:

```json
{
    "id": "4585-8554-af54-54c8",
    "component": "hand-build-component",
    "component_type": "my-nice-component-for-movie-detail",
    "data": {
        "title": "Toy Story",
        "year": 1995,
        ...
    }
}
```