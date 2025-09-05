# Next Gen UI Core Functionality

Module category: `Core`  
Module status: `Supported`

This module contains UI Agent Core functionality.

Provides:

* `NextGenUIAgent` providing agent configuration and methods for individual processing steps
* extensible framework for "data transformation" step
* plugable "UI renderer" framework for rendering + default `json` renderer used for Client-Side renderers
* abstraction of the LLM inference
  * `InferenceBase` interface
  * `LangChainModelInference` implementation using LangChain `chat_models`.

## Installation

```sh
pip install -U next_gen_ui_agent
```

### Interface usage

```py
from next_gen_ui_agent import NextGenUIAgent

inference = # any AI framework inference

agent = NextGenUIAgent(
    inference=LlamaStackInference(model="ollama:llama3.2"),
)

# API is not very friendly ATM, as you have to call methods for individual processing steps. We plan to improve it iit the near future.

```
