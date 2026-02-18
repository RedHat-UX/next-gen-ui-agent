# Advanced UI features

Beside data visualization during the ephemeral conversation, there are few more advanced UI functionalities which can be implementd if required.

Technically, these functionalities must be implemented in the *Controlling Assistant* and its UI/Frontend. Concrete solution depends heavily on the used frontend technology and AI framework/protocol.

*UI Agent* and its renderers provide features to support these functionalities.

## Rehydration of the UI view 

You want to store UI view for later re-use by the same user, or to allow sharing with other users.

You can store and share UI component configuration and rendering produced by the *UI Agent*. It contains originanly visualized data, so they can be simply re-shown.
It might be a good idea to indicate how old the data are, eg. by showing loading timestamp.

If you want to show fresh data during that rehydration, you have to use similar approach as described in the ["Live updates of data" chapter](#live-updates-of-visualized-data). 
Tool call replay is a good strategy here to get fresh data.
For rehydration after longer time, you have to take into account possibility of changes in the backend data loading mechanisms, you may be not able to reload data 
as underlying mechanism changed. To deal with it, you can simply show old view and info that data reload is not possible, or only that info without old view, or you can ask LLM to load the same/similar data by some newer mechanism if it exists and then replace UI component with the new one.

If you want user to be able to continue conversation with the AI after the rehydration, you have to store/share LLM conversation history in the *Calling assistant* also.

If you want to support view sharing, you have to solve concurency somehow, eg. share as readonly and allow to create copy by other user to continue conversation, 
or support full concurrent conversations/updates of the UI.

## Live updates of visualized data 

You have a cases when backend data are constantly changing and you want to reflect these changes in UI. 
Examples are CPU utilization or memory consumption from live deployment. So you have to refresh view periodically to show the latest data. 

This case is mostly frontend concern, you have to implement a way how to "load" fresh data from the backend. There are several options:

- pooling of REST/GraphQL API
- events based - frontend has to register to receive updates (WebSockets, Kafka or other messaging soolution)
- replay of the MCP tool call used to load original data (MCP Apps approach)

All the solutions have pros and cons, you have to select the one which suits your needs and available technology the best.

### Support in the UI Agent

*UI Agent* provides few functionalities to help implement this feature.

#### Passing info necessary for data loading from assistant backend to frontend

Frontend may need to know some info used to load original data in the assistant backend to be able to reload them.
*UI Agent* supports this with [`type_metadata` string field in the `InputData`](../input_data/index.md), which is passed through *UI Agent*
to the frontend as `configuration.input_type_metadata` field in the [*UI agent* output JSON](../../spec/output.md). 
Frontend can store it then and use for data loading.

Exact content of this field and how it is used in the frontend depends on concrete technology used to load data.
Eg. if MCP tool call is used to load data in the assistant backend, tool call arguments can be passed through this field. 
Tool call name itself is typically put into `InputData.type` which is also available in the frontend.

#### UI Component update from new data

When frontend loads fresh data, it needs a way how to apply them into existing UI component view. There are two main ways how to do it:

* use `data_path` info from fields to get values out of new data and update UI component directly in frontend, using data specific CSS classes. Mostly usefull for JSON formated data.
* use *UI Agent* exposed method where old component configuration JSON (`configuration` field in [the agent's output](../../spec/output.md)) and new data can be passed, to get UI component rendering with new data.
  [Input data transformation](../input_data/transformation.md) is applied, new data must be in the same format as the original data. Ways how the method is exposed depends on the used technology.

Both approaches expect that new data structure is the same as old one, so JSONPaths from `field.data_path` are valid for values pickup.

## Possibility to manualy re-arrange table columns by user

For [`table` component](../data_ui_blocks/dynamic_components.md#table), *UI Agent* can generate list of all available columns from the visualized data. UI component implementation can then use this info to provide possibility to the user to manually re-arrange visualized columns.

All fields info is generated only if [enabled in the configuration](../configuration.md#generate_all_fields-bool-optional) and is stored in the [*UI Agent* output JSON](../../spec/output.md) as `configuration.component_metadata.fields_all`. 

**TBD** Table implementations in the reenderers are expected to use this info if present, and provide necessary UI controls.

