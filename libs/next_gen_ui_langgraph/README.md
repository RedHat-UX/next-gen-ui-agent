# Next Gen UI LangGraph Agent

## Installation

```sh
pip install -U next_gen_ui_langgraph
```


## Example

### Get NextGenUI agent

Use `NextGenUILangGraphAgent` class and just pass your model

```py
from next_gen_ui_langgraph import NextGenUILangGraphAgent
from langchain_openai import ChatOpenAI

llm_settings = {
    "model": "llama3.2",
    "base_url": "http://localhost:11434/v1",
    "api_key": "ollama",
    "temperature": 0,
}
model = ChatOpenAI(**llm_settings, disable_streaming=True)

agent = NextGenUILangGraphAgent(model)
graph = agent.build_graph()
```

## Integrate NextGenUI agent in your assistant workflow 

TODO