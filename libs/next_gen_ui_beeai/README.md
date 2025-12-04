# Next Gen UI BeeAI Framework Integration

This module is part of the [Next Gen UI Agent project](https://github.com/RedHat-UX/next-gen-ui-agent).

[![Module Category](https://img.shields.io/badge/Module%20Category-AI%20Framework-darkred)](https://github.com/RedHat-UX/next-gen-ui-agent)
[![Module Status](https://img.shields.io/badge/Module%20Status-Tech%20Preview-orange)](https://github.com/RedHat-UX/next-gen-ui-agent)

Support for [BeeAI Framework](https://github.com/i-am-bee/beeai-framework).

As `A2A` or `MCP` are the AI protocols used by BeeAI, UI Agent binding into assistant app should use these protocol bindings provided in other modules.

## Provides

* `BeeAIInference` - ability to use BeeAI framework exposed LLM for UI Agent

## Installation

```sh
pip install -U next_gen_ui_beeai
```

### Interface usage in A2A Agent

```py
from next_gen_ui_a2a import NextGenUIA2AAgent
from next_gen_ui_beeai import BeeAIInference

agent = NextGenUIA2AAgent(
    component_system="rhds",
    inference=BeeAIInference(model="ollama:llama3.2"),
)
```

## Links

* [Documentation](https://redhat-ux.github.io/next-gen-ui-agent/guide/ai_apps_binding/beeai/)
* [Source Codes](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs/next_gen_ui_beeai)
* [Contributing](https://redhat-ux.github.io/next-gen-ui-agent/development/contributing/)
