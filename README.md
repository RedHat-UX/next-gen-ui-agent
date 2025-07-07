# Next Gen UI Agent

The goal of this AI agent is to generate personalised and rich UI components based on 
the user prompt, chat history and backend data provided by other agent in your assistant.

## Why use Next Gen UI?

* `Rich user experience` - Extends simple text based LLM applications output by UI components like card, table, chart, 
video-player, image gallery etc.
* `Extensible architecture` - Developer's choice to which AI framwork to choose and which UI component framework.
* `AI Frameworks integration` - Seamless integration of various AI framworks.
* `Server (Agent) side UI rendering` - Powerful agent centralized HTML (e.g. web component) rendition.
* `Client side UI rendering` - Client side rendering for more control over the rendition.

Example of rich card component including image and structured data.

![Card UI Component](https://raw.githubusercontent.com/RedHat-UX/next-gen-ui-agent/refs/heads/main/docs/img/data_ui_block_card.png "Card UI Component")


## Example

Following example shows how easy you can integrate your ReAct LangGraph agent with Next Gen UI Agent.
For other frameworks see below.

```py
from langgraph.prebuilt import create_react_agent
# This code depends on pip install langchain[anthropic]

def search(query: str):
    """Call to surf the web."""
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."

agent = create_react_agent("anthropic:claude-3-7-sonnet-latest", tools=[search])
agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
)

# TODO (NGUI-97)LangGraph simple example

ngui_agent = NextGenUILangGraphAgent("anthropic:claude-3-7-sonnet-latest")
graph = agent.build_graph()
```

## AI Frameworks

For seamless integration with your AI application following frameworks are supported. 

1. [LangGraph](./libs/next_gen_ui_langgraph/)
2. [Llama-stack](./libs/next_gen_ui_llama_stack/)
3. [BeeAI Framework](./libs/next_gen_ui_beeai/) - WIP

Missing framework?
[Create an issue](https://issues.redhat.com/projects/NGUI/issues) please.


## AI/UI Protocols

Protocols provides standardization between client and agent and provides TypeScript / Python interoperability.

1. [ACP](./libs/next_gen_ui_acp/) - WIP
2. A2A - TBD


## UI Frameworks

1. [React/PatternFly](./libs_js/next_gen_ui_react/) - WIP
2. [Hat Design System System](./libs/next_gen_ui_rhds_renderer/) - Server-side web component rendering
3. Text - TBD

## Contributing

Follow the [CONTRIBUTING.md](./CONTRIBUTING.md)
