import asyncio
import json
import os
import pprint

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from next_gen_ui_langgraph.agent import NextGenUILangGraphAgent

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
    prompt="You are useful movies assistant to answer user quesiont",
)

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

    print("\n\n===Next Gen UI JSON Rendition===")
    rendition_json = json.loads(ngui_response["renditions"][0].content)
    pprint.pprint(rendition_json)
