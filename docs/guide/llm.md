# LLM inference

*UI Agent* currently uses LLM to process `User Prompt` and [`Structured Data`](input_data.md) relevant to this prompt.
LLM selects the best UI component to visualize that data, and also configres it by selecting which values from the data has to be shown.

Every piece of `Input Data` is processed independently now.

In the future, we expect that conversation history will be also processed to get better UI consistency through conversation. 
And that all `Input Data` pieces will be processed at once, to also select which piece should be shown at given conversation step.

To perform this task, we use prompt engineering. LLM finetuning may be used in the future, as this is relatively narrow task. 
So finetuning might help to get better results from smaller LLMs, which means better performance and lower cost.

## Which LLM to use?



## LLM Evaluations



## How is LLM called

[*UI Agent* core library](ai_apps_binding/pythonlib.md) abstracts LLM infernce over `InferenceBase` interface. 
Multiple implementation are then provided in some of the [AI Framework and protocols](ai_apps_binding/index.md) bindings.