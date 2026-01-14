# LLM inference

*UI Agent* currently uses LLM to process `User Prompt` and structured [`Input Data`](input_data/index.md) relevant to this prompt.
LLM selects the best UI component to visualize that data, and also configures it by selecting which values from the data have to be shown.

For now, every piece of `Input Data` is processed independently. 
In the future, we expect that conversation history will also be processed to get better UI consistency through conversation.
And that all `Input Data` pieces will be processed at once, to also select which piece should be shown at given conversation step.

To instruct LLM to produce structured output expected by the agent, we use prompt engineering technique.

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