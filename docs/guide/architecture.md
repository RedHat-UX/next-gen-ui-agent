# Architecture

This guide shows how to use *NextGen UI Agent* in your AI application, how it plays with other building blocks of it.

## What is *UI Agent*

In short, *UI Agent* takes `User Prompt` and [`Structured Data`](input_data/index.md) relevant to this prompt as an input, 
and generates UI component to visualize that piece of data to the user. We call it [`Data UI Block`](data_ui_blocks/index.md).

UI Agent uses [AI (LLM)](./llm/index.md) in this step to understand the `User Prompt` and [input data structure](./input_data/structure.md),
and select the best dynamic UI component and displayed data values. 
As UI component generation is an AI narrow task, small LLMs (3B, 8B, Mini/Flash/Flash-Lite series) are typically able to provide 
good results for this task, which saves LLM price. They also provide better processing time, which is important for good user experience.
We provide [LLM evaluation tool](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/tests/ai_eval_components) as part of this project, 
results from some [eval runs are available](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/tests/ai_eval_components/results).
We expect to provide small LLMs finetuned for UI generation task in the future.

*UI Agent* can process structured Input Data in different formats. Extensible [input data transformation framework](./input_data/transformation.md) 
is used, with OOTB transformers provided for the most common formats like `JSON`, `YAML`, `CSV` and `fixed width columns table`.

Stricter configuration can be defined when tighter control of the UI components applied to the input data is necessary, for
details see [Component Selection and Configuration docs](./data_ui_blocks/index.md#selection-and-configuration-process).

In the future, this agent will also maintain `UI state` and view layouts to keep UI and flows consistent, handle personalized 
values formatting, and many other features. Stay tuned ;-)

Example of the generated `Data UI Block`:
![Example of the Data UI Block](../img/data_ui_block_card.png "Example of the Data UI Block")

*UI Agent* also suports [*Hand Build Components*](data_ui_blocks/hand_build_components.md) for pieces of data where UI component exists 
already, or where it is needed to provide special visualization or use features on top of AI generated UI components.

## How to use *UI Agent*

Your AI application, called *Controlling assistant*, has to provide other building blocks and their orchestration to implement complete solution.

Example of the *Controlling assistant* architecture:
![Example of the Controlling assistant architecture](../img/architecture_assistant_flow.jpg "Example of the Controlling assistant architecture")

*Controlling assistant* has to load structured data relevant for the `User Prompt` first, before calling the *UI Agent*. 
It can do it directly, for example using `LLM Tools Calling`/`MCP`, or it can call *Data providing agent* in case 
of Multi-Agent architecture. It can even generate that data itself in process of Reasoning or user's intent detection and processing.
*Controlling assistant* can load more pieces of data for one conversation turn, and send them all to the *UI Agent* to generate 
more `Data UI Blocks` to be shown to the user in the assistant's GUI.

*Controlling assistant* can also generate *Natural language response* based on this data and deliver it to the user through GUI or Voice user interface.
To follow vision of the *NextGen UI*, this natural language response should not repeat visualized data, but rather provide 
data summarizations, insights based on the data, proposals of the user actions, etc.
*UI Agent* itself has nothing to do with this response generation, it is responsibility of the *Controlling Assistant* to provide it.

Example mockup of the *Controlling assistant* GUI:
![Example mockup of the Controlling assistant GUI](../img/architecture_gui_mockup.png "Example mockup of the Controlling assistant GUI")

*UI Agent* core works with abstract representation of the [`Data UI Block`](data_ui_blocks/index.md). 
They can be rendered using pluggable GUI component system renderers, and integrated into the GUI of the *Controlling assistant*. 
We provide renderers for several UI component systems, either Server-Side or Client-Side, see [Binding into UI](renderer/index.md).

Output of the *UI Agent* does not contain the `Data UI Block` rendering only, but also [structured UI component configuration](../spec/output.md). 
It can be used to implement [advanced UI features](renderer/advanced_ui_features.md), like live data updates from backend, manual selection of visualized table columns etc.

## How to integrate *UI Agent*

*UI Agent* can be integrated into *Controlling Assistant* developed using multiple AI frameworks or AI protocols,
see [Binding into AI application](ai_apps_binding/index.md). You can also refer ["Choose your framework"](../installation.md) guide.

The first approach how to integrate *UI Agent* into the *Controlling assistant* is to use assistant's LLM to choose and execute the 
UI Agent. This approach makes sense if you want your assistant to act like `Orchestrator` - to decide about the UI component generation.
For example to select which backend data loaded during the processing needs to be visualized in UI, or whether UI has to be generated at all.
This approach cost you more in terms of the main LLM processing price (tokens) and time, but gives you more flexibility.

Alternative approach is to invoke *UI Agent* directly as part of your assistant logic, at the specific moment of the processing flow, 
after gathering structured backend data for the response.
This approach is a bit more reliable, helps to reduce main LLM processing price (tokens) and time (you can even generate UI in 
parallel with *Natural language response* generation), but is a bit less flexible.
