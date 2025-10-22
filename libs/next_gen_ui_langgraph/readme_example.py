import asyncio
import json
import os

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from next_gen_ui_langgraph import NextGenUILangGraphAgent

# Movie database with realistic data
MOVIES_DB = {
    "toy_story": {
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
        "released": "1995-11-22",
        "trailerUrl": "https://www.youtube.com/watch?v=v-PjgYDrg70",
        "budget": 30000000,
        "actors": ["Jim Varney", "Tim Allen", "Tom Hanks", "Don Rickles"],
        "studio": "Pixar",
    },
    "finding_nemo": {
        "languages": ["English"],
        "year": 2003,
        "imdbId": "0266543",
        "runtime": 100,
        "imdbRating": 8.2,
        "movieId": "2",
        "countries": ["USA"],
        "imdbVotes": 1089429,
        "title": "Finding Nemo",
        "url": "https://themoviedb.org/movie/12",
        "revenue": 940335536,
        "tmdbId": "12",
        "plot": "A clownfish named Marlin searches for his missing son across the ocean.",
        "posterUrl": "https://image.tmdb.org/t/p/w440_and_h660_face/eHuGQ10FUzK1mdOY69wF5pGgEf5.jpg",
        "released": "2003-05-30",
        "trailerUrl": "https://www.youtube.com/watch?v=wZdpNglLbt8",
        "budget": 94000000,
        "actors": ["Albert Brooks", "Ellen DeGeneres", "Alexander Gould"],
        "studio": "Pixar",
    },
    "the_incredibles": {
        "languages": ["English"],
        "year": 2004,
        "imdbId": "0317705",
        "runtime": 115,
        "imdbRating": 8.0,
        "movieId": "3",
        "countries": ["USA"],
        "imdbVotes": 781926,
        "title": "The Incredibles",
        "url": "https://themoviedb.org/movie/9806",
        "revenue": 631606713,
        "tmdbId": "9806",
        "plot": "A family of undercover superheroes attempts to live a quiet suburban life.",
        "posterUrl": "https://image.tmdb.org/t/p/w440_and_h660_face/2LqaLgk4Z226KkgPJuiOQ58wvrm.jpg",
        "released": "2004-11-05",
        "trailerUrl": "https://www.youtube.com/watch?v=eZbzbC9285I",
        "budget": 92000000,
        "actors": ["Craig T. Nelson", "Holly Hunter", "Samuel L. Jackson"],
        "studio": "Pixar",
    },
    "up": {
        "languages": ["English"],
        "year": 2009,
        "imdbId": "1049413",
        "runtime": 96,
        "imdbRating": 8.3,
        "movieId": "4",
        "countries": ["USA"],
        "imdbVotes": 1086493,
        "title": "Up",
        "url": "https://themoviedb.org/movie/14160",
        "revenue": 735099082,
        "tmdbId": "14160",
        "plot": "An elderly widower uses balloons to fly his house to South America.",
        "posterUrl": "https://image.tmdb.org/t/p/w440_and_h660_face/vpbaStTMt8qqXaEgnOR2EE4DNJk.jpg",
        "released": "2009-05-29",
        "trailerUrl": "https://www.youtube.com/watch?v=ORFWdXl_zJ4",
        "budget": 175000000,
        "actors": ["Ed Asner", "Jordan Nagai", "John Ratzenberger"],
        "studio": "Pixar",
    },
    "inside_out": {
        "languages": ["English"],
        "year": 2015,
        "imdbId": "2096673",
        "runtime": 95,
        "imdbRating": 8.1,
        "movieId": "5",
        "countries": ["USA"],
        "imdbVotes": 748929,
        "title": "Inside Out",
        "url": "https://themoviedb.org/movie/150540",
        "revenue": 858846732,
        "tmdbId": "150540",
        "plot": "After moving to a new city, an 11-year-old girl's emotions conflict on how to best navigate her new life.",
        "posterUrl": "https://image.tmdb.org/t/p/w440_and_h660_face/2H1TmgdfNtsKlU9jKdeNyYL5y8T.jpg",
        "released": "2015-06-19",
        "trailerUrl": "https://www.youtube.com/watch?v=yRUAzGQ3nSY",
        "budget": 175000000,
        "actors": ["Amy Poehler", "Phyllis Smith", "Bill Hader"],
        "studio": "Pixar",
    },
}

movie_toy_story = [{"movie": MOVIES_DB["toy_story"]}]

if not os.environ.get("OPENAI_API_KEY"):
    # getpass.getpass("Enter your OpenAI API key: ")
    os.environ["OPENAI_API_KEY"] = "ollama"

llm = ChatOpenAI(model="llama3.2", base_url="http://localhost:11434/v1")


# Movies Agent Tools
def search_movie(title: str):
    """Search for a single movie by title.
    Args:
        title: Movie title e.g. 'Toy Story', 'Finding Nemo'
    """
    title_lower = title.lower().replace(" ", "_")
    for key, movie_data in MOVIES_DB.items():
        if title_lower in key or key in title_lower:
            print(f"Returning JSON payload of '{title}' movie")
            return json.dumps([{"movie": movie_data}], default=str)
    return None


def get_pixar_movies():
    """Get a list of popular Pixar animated movies with ratings and box office data.
    Use this when user asks for multiple Pixar movies, animated films, or wants to compare Pixar movies.
    """
    print("Returning JSON payload of Pixar movies")
    pixar_movies = [{"movie": movie} for movie in MOVIES_DB.values()]
    return json.dumps(pixar_movies, default=str)


def get_top_rated_movies(min_rating: float = 8.0):
    """Get top-rated movies above a minimum rating threshold.
    Args:
        min_rating: Minimum IMDB rating (default 8.0)
    """
    print(f"Returning movies with rating >= {min_rating}")
    top_movies = [
        {"movie": movie}
        for movie in MOVIES_DB.values()
        if movie["imdbRating"] >= min_rating
    ]
    return json.dumps(top_movies, default=str) if top_movies else None


def compare_movies(titles: str):
    """Compare multiple movies side by side. Useful for charts showing ratings, budgets, or revenue comparisons.
    Args:
        titles: Comma-separated movie titles e.g. 'Toy Story, Finding Nemo, Up'
    """
    print(f"Comparing movies: {titles}")
    movie_list = [t.strip() for t in titles.split(",")]
    results = []

    for title in movie_list:
        title_lower = title.lower().replace(" ", "_")
        for key, movie_data in MOVIES_DB.items():
            if title_lower in key or key in title_lower:
                results.append({"movie": movie_data})
                break

    return json.dumps(results, default=str) if results else None


def get_box_office_leaders():
    """Get movies sorted by box office revenue. Perfect for revenue comparison charts."""
    print("Returning box office leaders")
    sorted_movies = sorted(MOVIES_DB.values(), key=lambda m: m["revenue"], reverse=True)
    return json.dumps([{"movie": m} for m in sorted_movies], default=str)


movies_agent = create_react_agent(
    model=llm,
    tools=[
        search_movie,
        get_pixar_movies,
        get_top_rated_movies,
        compare_movies,
        get_box_office_leaders,
    ],
    prompt="You are a helpful movies assistant. Use the available tools to answer user questions about movies, ratings, and box office performance.",
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
    print("\n\n===Movies Text Answer===\n", movies_response["messages"][-1].content)

    # Run NGUI Agent to get UI component as JSON for client-side rendering
    ngui_response = asyncio.run(
        # Run Next Gen UI Agent. Pass movies agent response directly.
        ngui_agent.ainvoke(movies_response, ngui_cfg),
    )

    print(
        f"\n\n===Next Gen UI {component_system} Rendition===\n",
        ngui_response["renditions"][0].content,
    )


if __name__ == "__main__":
    run()
