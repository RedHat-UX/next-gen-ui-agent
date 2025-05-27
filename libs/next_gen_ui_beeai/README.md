# Next Gen UI BeeAI Integration

## Installation

```sh
pip install -U next_gen_ui_beeai
```

### Interface usage in ACP Agent

```py
from next_gen_ui_acp import NextGenUIACPAgent
from next_gen_ui_beeai import BeeAIInference

agent = NextGenUIACPAgent(
    component_system="rhds",
    inference=BeeAIInference(model="ollama:llama3.2"),
)
```
