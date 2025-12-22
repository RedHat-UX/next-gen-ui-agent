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
      1. [Hand Build Component](./hand_build_components.md#mapping-from-inputdatatype) - no LLM required
      2. [pre-configured Dynamic Component](./dynamic_components.md), its configuration is 
          defined in the [agent config](../configuration.md#configuration-agentconfigdynamiccomponentconfiguration-optional) - no LLM required
3. Fully LLM selected and configured [Dynamic Component](./dynamic_components.md) - LLM is required

If only *"no LLM required"* use cases are used in your deployment, the *UI Agent* can be instantiated without LLM (without LLM Inference provider).

*UI Agent* by default selects from all the supported Dynamic Components in step `3.`, but you can narrow choice to the components suitable for your application
[in the configuration](../configuration.md#selectable_components-setstr-optional).

In the future, we plan to implement additional options for "per `InputData.type` configured" components:

* LLM powered selection from more components (dynamic with or without pre-defined configuration, or HBC)
* LLM powered configuration of the Dynamic Component configured without pre-defined configuration
* LLM powered update of the Dynamic Component pre-defined configuration to better fit `User prompt`, with fallback when LLM is not available

Note that `InputData.type` often contains name of the LLM tool used to load the data (eg. in our [AI framework bindings](../ai_apps_binding/index.md)), 
so tool names are directly used for binding to UI components in this case.

### Example configuration

In the case of this example [yaml configuration](../configuration.md#yaml-configuration), selection and configuration works this way:

* For input data with `type`=`movies:movie-detail`, Hand Build Component with name `movies:movie-detail-view` is used. Its specific 
  rendering code has to be provided in used UI renderer.
* For input data with `type`=`movie:movies-list`, `table` Dynamic Component is used, configured to show three columns and "Movies" title.
* For input data with `type`=`movie:actors-list`, error is produced, as not pre-configured Dynamic components are not supported ATM.
* For other inut data, AI/LLM powered selection and configuration is performed.

```yaml
...

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
      - component: table

```

