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
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from next_gen_ui_langgraph.agent import NextGenUILangGraphAgent

# search_movie tool function
# def search_movie(title: str):
#  ...

llm = ChatOpenAI(**llm_settings)
movies_agent = create_react_agent(model=llm, tools=[search_movie])

# Next Gen UI Agent - Build it as Standard LangGraph agent
ngui_agent = NextGenUILangGraphAgent(model=llm).build_graph()
ngui_cfg = {"configurable": {"component_system": "json"}}

if __name__ == "__main__":
    # Run Movies Agent to get raw movie data and answer
    movies_response = movies_agent.invoke(
        {"messages": [{"role": "user", "content": "Play Toy Story movie trailer"}]}
    )
    print("\n\n===Movies Text Answer===\n", movies_response["messages"][-1].content)

    # Run NGUI Agent to get UI component as JSON for client-side rendering
    ngui_response = asyncio.run(
        # Run Next Gen UI Agent. Pass movies agent response directly.
        ngui_agent.ainvoke(movies_response, ngui_cfg),
    )

    print(f"\n\n===Next Gen UI {component_system} Rendition===\n", ngui_response["renditions"][0].content)
```
Note: Full python file is stored in [libs/next_gen_ui_langgraph/readme_example.py](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/libs/next_gen_ui_langgraph/readme_example.py).

Running this assistant with user's questions `Play Toy Story movie trailer` generates following output of movies agent:

```
===Movies Text Answer===
 Here's the answer to the original user question:

[Intro music plays]

Narrator (in a deep, dramatic voice): "In a world where toys come to life..."

[Scene: Andy's room, toys are scattered all over the floor. Woody, a pull-string cowboy toy, is centered on a shelf.]

Narrator: "One toy stands tall."

[Scene: Close-up of Woody's face]
```

and Next Gen UI json rendering:

```js
===Next Gen UI json Rendition===
{
    'component': 'video-player',
    'id': 'call_zomga3r3',
    'title': 'Toy Story Trailer',
    'video': 'https://www.youtube.com/embed/v-PjgYDrg70',
    'video_img': 'https://img.youtube.com/vi/v-PjgYDrg70/maxresdefault.jpg'
}
```


## AI Frameworks

For seamless integration with your AI application following frameworks are supported. 

1. [LangGraph](./libs/next_gen_ui_langgraph/)
2. [Llama-stack](./libs/next_gen_ui_llama_stack/)
3. [BeeAI Framework](./libs/next_gen_ui_beeai/) - WIP

Missing framework?
[Create an github issue](https://github.com/RedHat-UX/next-gen-ui-agent/issues) please.


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
