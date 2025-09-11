# LLM inference

*UI Agent* currently uses LLM to process `User Prompt` and strucutred [`Input Data`](input_data.md) relevant to this prompt.
LLM selects the best UI component to visualize that data, and also configres it by selecting which values from the data has to be shown.

For now, every piece of `Input Data` is processed independently. 
In the future, we expect that conversation history will be also processed to get better UI consistency through conversation.
And that all `Input Data` pieces will be processed at once, to also select which piece should be shown at given conversation step.

To instruct LLM to produce output expected by the agent, we use prompt engineering technique for now.
LLM finetuning may be used in the future, as component type selection and configuration is relatively narrow AI task.
Finetuning might help to get better results from smaller LLMs, which means better performance and lower cost of the processing.

## LLM Evaluations

To evaluate how well is particular LLM performing on *UI Agent* component selection and configuration task, 
we provide [Evaluation tool and dataset](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/tests/ai_eval_components).

This evaluation currently covers disting shapes of the input data, and evaluates if LLM generates correct configuration from 
the "technical" aspect of view. Currently it is not able to evaluate if data values selected to be shown in very generic 
components, like `one-card` or `table`, are good enough. So you have to do this evaluation by yourself still.

Evaluation results for some LLM's are available in `/results` directory.

## Which LLM to use?

Generally, even very small LLMs, like 3B `Llama 3.2` or 2B `Granite 3.2`, are pretty good at this task. They mostly struggle to 
generate pointers to values in `InputData` for some shapes.

A bit larger models, like 8B `Granite 3.2` or Google `Geminy Flash` and `Geminy Flash Lite` are good in the most evaluations.

Improvements on even larger LLM are not significant, and you pay all the rices for the larhe LLM - slower speed and more expensive runtime.

It seems that larger LLMs tend to put more values into generic components (more columns in the table or Facts in the card).


## How is LLM really called

[*UI Agent* core library](ai_apps_binding/pythonlib.md) abstracts LLM infernce over `InferenceBase` interface. 
Multiple implementation are then provided in some of the [AI Framework and protocols](ai_apps_binding/index.md) bindings.

To get repeatable results from the agent, you should always use `temperature=0` when calling the LLM behind this interface.