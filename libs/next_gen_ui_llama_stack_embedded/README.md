# Next Gen UI Embedded Llama Stack Server Inference

This module is part of the [Next Gen UI Agent project](https://github.com/RedHat-UX/next-gen-ui-agent).

Module category: `AI framework`  
Module status: `Supported`

Support for LLM inference using [Embedded Llama Stack server](https://github.com/meta-llama/llama-stack).

Provides:

* `LlamaStackEmbeddedAsyncAgentInference` to use LLM hosted in embedded Llama Stack server, started from provided [Llama Stack config file](https://llama-stack.readthedocs.io/en/latest/distributions/configuration.html).
* `init_inference_from_env` method to init Llama Stack inference (remote or embedded) based on environment variables
    * `INFERENCE_MODEL` - LLM model to use - inference is not created if undefined (default value can be provided as method parameter)
    * `LLAMA_STACK_HOST` - remote LlamaStack host - if defined then it is used with LLAMA_STACK_PORT to create remote LlamaStack inference
    * `LLAMA_STACK_PORT` - remote LlamaStack port - optional, defaults to `5001`
    * `LLAMA_STACK_URL` - remote LlamaStack url - if `LLAMA_STACK_HOST` is not defined, but this url is defined, then it 
      is used to create remote LlamaStack inference
    * `LLAMA_STACK_CONFIG_FILE` - path to embedded LlamaStack server config file, used only if no remote LlamaStack is configured 
      (default value can be provided as method parameter)
* `examples/llamastack-ollama.yaml` example of the LlamaStack config file to use LLM from [Ollama](https://ollama.com/) running on 
  localhost (with model also taken from `INFERENCE_MODEL` env variable).

## Installation

```sh
pip install -U next_gen_ui_llama_stack_embedded
```

## Example

### Instantiation of `LlamaStackEmbeddedAsyncAgentInference`

```py

from next_gen_ui_llama_stack_embedded import LlamaStackEmbeddedAsyncAgentInference

config_file = "example/llamastack-ollama.yaml"
model = "llama3.2:latest"

inference = LlamaStackEmbeddedAsyncAgentInference(config_file, model)

# init UI Agent using inference

```

### Inference initialization from environment variables

```py
from next_gen_ui_llama_stack_embedded import init_inference_from_env

# default model used if env variable is not defined
INFERENCE_MODEL_DEFAULT = "granite3.3:2b"

inference = init_inference_from_env(default_model=INFERENCE_MODEL_DEFAULT)

if (inference):
    # init UI Agent using inference
else:
    print("Inference not initialized because not configured in env variables")

```
