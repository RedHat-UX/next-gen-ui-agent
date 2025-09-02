# Next Gen UI LangGraph Agent

Support for [LangGraph](https://www.langchain.com/langgraph). 

`NextGenUILangGraphAgent` takes all tool messages from provided LanGraph state, and process data from them into UI components.

Tool name is used as `InputData.type` for each tool message, so can be used for [Hand Build Component](../../docs/guide/hand_build_components.md) selection based on mapping in UI Agent's configuration.

## Installation

```sh
pip install -U next_gen_ui_langgraph
```


## Example

### Get NextGenUI agent

Use `NextGenUILangGraphAgent` class and just pass your model to get standard LangGraph Agent.

```py
from next_gen_ui_langgraph import NextGenUILangGraphAgent
from langchain_openai import ChatOpenAI

llm_settings = {
    "model": "llama3.2",
    "base_url": "http://localhost:11434/v1",
    "api_key": "ollama",
    "temperature": 0,
}
model = ChatOpenAI(**llm_settings)

ngui_agent = NextGenUILangGraphAgent(model).build_graph()
```

## Integrate NextGenUI agent in your assistant workflow 

This complete example shows how movies ReAct agent get data about movie and then response is passed to Next Gen UI Agent.

```py
import asyncio
import json
import os

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from next_gen_ui_langgraph import NextGenUILangGraphAgent

movie_toy_story = [
    {
        "movie": {
            "languages": ["English"],
            "year": 1995,
            "imdbId": "0114709",
            "runtime": 81,
            "imdbRating": 8.3,
            "movieId": "1",
            "countries": ["USA"],
            "imdbVotes": 591836,
            "title": "Toy Story",
            "url": "https://themoviedb.org/movie/862",
            "revenue": 373554033,
            "tmdbId": "862",
            "plot": "A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room.",
            "posterUrl": "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
            "released": "2022-11-02",
            "trailerUrl": "https://www.youtube.com/watch?v=v-PjgYDrg70",
            "budget": 30000000,
            "actors": ["Jim Varney", "Tim Allen", "Tom Hanks", "Don Rickles"],
        },
    }
]

if not os.environ.get("OPENAI_API_KEY"):
    # getpass.getpass("Enter your OpenAI API key: ")
    os.environ["OPENAI_API_KEY"] = "ollama"

llm = ChatOpenAI(model="llama3.2", base_url="http://localhost:11434/v1")


# Movies Agent
# Search movie tool
def search_movie(title: str):
    """Call to find movie.
    Args:
    title: Movie title e.g. 'Toy Story'
    """
    if "toy story" in title.lower():
        print(f"Returning JSON payload of '{title}' movie")
        return json.dumps(movie_toy_story, default=str)
    return None


movies_agent = create_react_agent(
    model=llm,
    tools=[search_movie],
    prompt="You are useful movies assistant to answer user questions",
)

# Next Gen UI Agent - Build it as Standard LangGraph agent
ngui_agent = NextGenUILangGraphAgent(model=llm).build_graph()
component_system = "json"
# component_system = "rhds" # use rhds if you have installed package next_gen_ui_rhds_renderer
ngui_cfg = {"configurable": {"component_system": component_system}}


def run() -> None:
    # Run Movies Agent to get raw movie data and answer
    prompt = "Play Toy Story movie trailer"
    # prompt = "Show me the poster of Toy Story"
    # prompt = "Tell me details about Toy Story, including poster"
    movies_response = movies_agent.invoke(
        {"messages": [{"role": "user", "content": prompt}]}
    )
    print("===Movies Text Answer===", movies_response["messages"][-1].content)

    # Run NGUI Agent to get UI component as JSON for client-side rendering
    ngui_response = asyncio.run(
        # Run Next Gen UI Agent. Pass movies agent response directly.
        ngui_agent.ainvoke(movies_response, ngui_cfg),
    )

    print(f"===Next Gen UI {component_system} Rendition===", ngui_response["renditions"][0].content)


if __name__ == "__main__":
    run()
```

Running this assistant with user's questions `Play Toy Story movie trailer` return this output:

```
===Movies Text Answer===
 Here's the answer to the original user question:

[Intro music plays]

Narrator (in a deep, dramatic voice): "In a world where toys come to life..."

[Scene: Andy's room, toys are scattered all over the floor. Woody, a pull-string cowboy toy, is centered on a shelf.]

Narrator: "One toy stands tall."

[Scene: Close-up of Woody's face]

===Next Gen UI json Rendition===
{
    'component': 'video-player',
    'id': 'call_zomga3r3',
    'title': 'Toy Story Trailer',
    'video': 'https://www.youtube.com/embed/v-PjgYDrg70',
    'video_img': 'https://img.youtube.com/vi/v-PjgYDrg70/maxresdefault.jpg'
}
```
