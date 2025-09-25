# Next Gen UI Agent

The goal of this AI agent is to generate personalised and rich UI components based on 
the user prompt, chat history and backend data provided by other agent in your assistant.

In the future, this agent will also maintain UI state and view layouts to keep UI and flows 
consistent, handle personalized values formating, and many other features. Stay tuned ;-)

## Why use Next Gen UI?

* `Rich user experience` - Extends simple text based LLM applications output by rich GUI components like card, table, chart, 
video-player, image gallery etc. Possibility to plug in own components.
* `Extensible architecture` - Developer's choice to which AI framwork to plug and which UI component framework to render.
* `AI Frameworks integration` - Seamless integration of various AI framworks.
* `Server (Agent) side UI rendering` - Powerful agent centralized HTML (e.g. web component) rendition.
* `Client side UI rendering` - Client side rendering for more control over the rendition - React/PatternFly NPM.

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
    print("===Movies Text Answer===", movies_response["messages"][-1].content)

    # Run NGUI Agent to get UI component as JSON for client-side rendering
    ngui_response = asyncio.run(
        # Run Next Gen UI Agent. Pass movies agent response directly.
        ngui_agent.ainvoke(movies_response, ngui_cfg),
    )

    print(f"===Next Gen UI {component_system} Rendition===", ngui_response["renditions"][0].content)
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

For seamless integration of the UI Agent into your AI application following frameworks are supported. 

1. [LangGraph](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs/next_gen_ui_langgraph/)
2. [Llama Stack](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs/next_gen_ui_llama_stack/) and [Llama Stack Embedded](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs/next_gen_ui_llama_stack_embedded)
3. [BeeAI Framework](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs/next_gen_ui_beeai/) - Tech Preview

Missing framework?
[Create an github issue](https://github.com/RedHat-UX/next-gen-ui-agent/issues) please.


## AI Protocols

Protocols provides standardization between client and agent and provides TypeScript / Python interoperability.
These modules provide way to integrate protocol into your AI application, servers to run it as a service, 
and even container images to run it easily.

1. [MCP](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs/next_gen_ui_mcp)
2. [ACP](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs/next_gen_ui_acp/) - Tech Preview
3. A2A - [WIP](https://github.com/RedHat-UX/next-gen-ui-agent/pull/149)


## UI Frameworks

Renders for distinct UI frameworks

1. [React/PatternFly NPM](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs_js/next_gen_ui_react/) - Client-Side React components
2. [Red Hat Design System System](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs/next_gen_ui_rhds_renderer/) - Server-side web component rendering
3. Text - TBD

## Contributing

Follow the [CONTRIBUTING.md](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/CONTRIBUTING.md)
