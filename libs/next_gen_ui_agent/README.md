# Next Gen UI Core Functionality

This module is part of the [Next Gen UI Agent project](https://github.com/RedHat-UX/next-gen-ui-agent).

[![Module Category](https://img.shields.io/badge/Module%20Category-Core-blue)](https://github.com/RedHat-UX/next-gen-ui-agent)
[![Module Status](https://img.shields.io/badge/Module%20Status-Supported-green)](https://github.com/RedHat-UX/next-gen-ui-agent)

This module contains UI Agent Core functionality and frameworks.

## Provides

* `NextGenUIAgent` providing agent configuration and methods for individual processing steps
* Produced *UI Data Blocks*:
    * [LLM selected and configured dynamic components](https://redhat-ux.github.io/next-gen-ui-agent/guide/data_ui_blocks/dynamic_components/)
        * Supported: `one-card`, `image`, `video-player`
        * Tech-Preview: `set-of-cards`, `table`
    * [Hand Build Components](https://redhat-ux.github.io/next-gen-ui-agent/guide/data_ui_blocks/hand_build_components/)
* Extensible framework for "data transformation" step
* Plugable "UI renderer" framework for UI components rendering
    * Default `json` renderer used to send definitions to client-side renderers
* Abstraction of the LLM inference
    * `InferenceBase` interface used by UI Agent
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

## Links

* [Documentation](https://redhat-ux.github.io/next-gen-ui-agent/guide/ai_apps_binding/pythonlib/)
* [Source Codes](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs/next_gen_ui_agent)
* [Contributing](https://redhat-ux.github.io/next-gen-ui-agent/development/contributing/)
