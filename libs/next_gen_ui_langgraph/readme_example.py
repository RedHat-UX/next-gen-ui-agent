import asyncio
import json
import os

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from next_gen_ui_langgraph import NextGenUILangGraphAgent

# Movie database with comprehensive data including box office, awards, and weekly performance
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
        "genres": ["Animation", "Adventure", "Family", "Comedy"],
        "director": "John Lasseter",
        "productionCompany": "Pixar Animation Studios",
        "openingWeekend": 29140617,
        "domesticRevenue": 191796233,
        "internationalRevenue": 181757800,
        "profit": 343554033,
        "roi": 11.45,
        "audienceScore": 92,
        "criticScore": 100,
        "awards": {"wins": 28, "nominations": 24, "oscars": 1},
        "weeklyBoxOffice": [
            {"week": 1, "revenue": 29140617},
            {"week": 2, "revenue": 18923456},
            {"week": 3, "revenue": 15234567},
            {"week": 4, "revenue": 12345678},
        ],
    },
    "the_shawshank_redemption": {
        "languages": ["English"],
        "year": 1994,
        "imdbId": "0110912",
        "runtime": 142,
        "imdbRating": 9.3,
        "movieId": "2",
        "countries": ["USA"],
        "imdbVotes": 2589173,
        "title": "The Shawshank Redemption",
        "url": "https://themoviedb.org/movie/278",
        "revenue": 28341469,
        "tmdbId": "278",
        "plot": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
        "posterUrl": "https://image.tmdb.org/t/p/w440_and_h660_face/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg",
        "released": "1994-09-23",
        "trailerUrl": "https://www.youtube.com/watch?v=6hB3S9bIaco",
        "budget": 25000000,
        "actors": ["Tim Robbins", "Morgan Freeman", "Bob Gunton", "William Sadler"],
        "genres": ["Drama", "Crime"],
        "director": "Frank Darabont",
        "productionCompany": "Castle Rock Entertainment",
        "openingWeekend": 727327,
        "domesticRevenue": 28341469,
        "internationalRevenue": 30500000,
        "profit": 33841469,
        "roi": 1.35,
        "audienceScore": 98,
        "criticScore": 91,
        "awards": {"wins": 23, "nominations": 51, "oscars": 0},
        "weeklyBoxOffice": [
            {"week": 1, "revenue": 727327},
            {"week": 2, "revenue": 1234567},
            {"week": 3, "revenue": 2456789},
            {"week": 4, "revenue": 3123456},
        ],
    },
    "the_dark_knight": {
        "languages": ["English"],
        "year": 2008,
        "imdbId": "0468569",
        "runtime": 152,
        "imdbRating": 9.0,
        "movieId": "3",
        "countries": ["USA", "UK"],
        "imdbVotes": 2654321,
        "title": "The Dark Knight",
        "url": "https://themoviedb.org/movie/155",
        "revenue": 1004558444,
        "tmdbId": "155",
        "plot": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests.",
        "posterUrl": "https://image.tmdb.org/t/p/w440_and_h660_face/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
        "released": "2008-07-18",
        "trailerUrl": "https://www.youtube.com/watch?v=EXeTwQWrcwY",
        "budget": 185000000,
        "actors": ["Christian Bale", "Heath Ledger", "Aaron Eckhart", "Michael Caine"],
        "genres": ["Action", "Crime", "Drama", "Thriller"],
        "director": "Christopher Nolan",
        "productionCompany": "Warner Bros.",
        "openingWeekend": 158411483,
        "domesticRevenue": 534858444,
        "internationalRevenue": 469700000,
        "profit": 819558444,
        "roi": 4.43,
        "audienceScore": 94,
        "criticScore": 94,
        "awards": {"wins": 164, "nominations": 164, "oscars": 2},
        "weeklyBoxOffice": [
            {"week": 1, "revenue": 158411483},
            {"week": 2, "revenue": 75165786},
            {"week": 3, "revenue": 42674614},
            {"week": 4, "revenue": 26088337},
        ],
    },
    "inception": {
        "languages": ["English"],
        "year": 2010,
        "imdbId": "1375666",
        "runtime": 148,
        "imdbRating": 8.8,
        "movieId": "4",
        "countries": ["USA", "UK"],
        "imdbVotes": 2289456,
        "title": "Inception",
        "url": "https://themoviedb.org/movie/27205",
        "revenue": 836848102,
        "tmdbId": "27205",
        "plot": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a CEO.",
        "posterUrl": "https://image.tmdb.org/t/p/w440_and_h660_face/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg",
        "released": "2010-07-16",
        "trailerUrl": "https://www.youtube.com/watch?v=YoHD9XEInc0",
        "budget": 160000000,
        "actors": [
            "Leonardo DiCaprio",
            "Joseph Gordon-Levitt",
            "Ellen Page",
            "Tom Hardy",
        ],
        "genres": ["Action", "Sci-Fi", "Thriller"],
        "director": "Christopher Nolan",
        "productionCompany": "Warner Bros.",
        "openingWeekend": 62785337,
        "domesticRevenue": 292576195,
        "internationalRevenue": 544271907,
        "profit": 676848102,
        "roi": 4.23,
        "audienceScore": 91,
        "criticScore": 87,
        "awards": {"wins": 158, "nominations": 220, "oscars": 4},
        "weeklyBoxOffice": [
            {"week": 1, "revenue": 62785337},
            {"week": 2, "revenue": 42682944},
            {"week": 3, "revenue": 27305569},
            {"week": 4, "revenue": 18688378},
        ],
    },
    "the_matrix": {
        "languages": ["English"],
        "year": 1999,
        "imdbId": "0133093",
        "runtime": 136,
        "imdbRating": 8.7,
        "movieId": "5",
        "countries": ["USA"],
        "imdbVotes": 1876543,
        "title": "The Matrix",
        "url": "https://themoviedb.org/movie/603",
        "revenue": 463517383,
        "tmdbId": "603",
        "plot": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.",
        "posterUrl": "https://image.tmdb.org/t/p/w440_and_h660_face/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
        "released": "1999-03-31",
        "trailerUrl": "https://www.youtube.com/watch?v=vKQi3bBA1y8",
        "budget": 63000000,
        "actors": [
            "Keanu Reeves",
            "Laurence Fishburne",
            "Carrie-Anne Moss",
            "Hugo Weaving",
        ],
        "genres": ["Action", "Sci-Fi"],
        "director": "The Wachowskis",
        "productionCompany": "Warner Bros.",
        "openingWeekend": 27788331,
        "domesticRevenue": 171479930,
        "internationalRevenue": 292037453,
        "profit": 400517383,
        "roi": 6.36,
        "audienceScore": 85,
        "criticScore": 88,
        "awards": {"wins": 42, "nominations": 51, "oscars": 4},
        "weeklyBoxOffice": [
            {"week": 1, "revenue": 27788331},
            {"week": 2, "revenue": 17158943},
            {"week": 3, "revenue": 14502507},
            {"week": 4, "revenue": 9345803},
        ],
    },
    "interstellar": {
        "languages": ["English"],
        "year": 2014,
        "imdbId": "0816692",
        "runtime": 169,
        "imdbRating": 8.6,
        "movieId": "6",
        "countries": ["USA", "UK", "Canada"],
        "imdbVotes": 1765432,
        "title": "Interstellar",
        "url": "https://themoviedb.org/movie/157336",
        "revenue": 677471339,
        "tmdbId": "157336",
        "plot": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
        "posterUrl": "https://image.tmdb.org/t/p/w440_and_h660_face/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
        "released": "2014-11-07",
        "trailerUrl": "https://www.youtube.com/watch?v=zSWdZVtXT7E",
        "budget": 165000000,
        "actors": [
            "Matthew McConaughey",
            "Anne Hathaway",
            "Jessica Chastain",
            "Michael Caine",
        ],
        "genres": ["Adventure", "Drama", "Sci-Fi"],
        "director": "Christopher Nolan",
        "productionCompany": "Paramount Pictures",
        "openingWeekend": 47510360,
        "domesticRevenue": 188020017,
        "internationalRevenue": 489451322,
        "profit": 512471339,
        "roi": 3.11,
        "audienceScore": 86,
        "criticScore": 73,
        "awards": {"wins": 44, "nominations": 148, "oscars": 1},
        "weeklyBoxOffice": [
            {"week": 1, "revenue": 47510360},
            {"week": 2, "revenue": 29185788},
            {"week": 3, "revenue": 15123127},
            {"week": 4, "revenue": 12045876},
        ],
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
    Use this ONLY when user asks about a SPECIFIC movie by name.
    DO NOT use for distribution/aggregation queries - use get_all_movies() instead.
    
    Args:
        title: Movie title e.g. 'Toy Story', 'Finding Nemo'
    """
    title_lower = title.lower().replace(" ", "_")
    for key, movie_data in MOVIES_DB.items():
        if title_lower in key or key in title_lower:
            print(f"Returning JSON payload of '{title}' movie")
            return json.dumps([{"movie": movie_data}], default=str)
    return None


def get_all_movies():
    """Get all movies in the database with comprehensive details including ratings, box office, awards, and weekly performance.
    Use this when user asks for:
    - all movies, movie list, or wants to see all available movies
    - comparing multiple movies (without specific titles)
    - opening weekends, box office trends, or revenue comparisons across all movies
    - DISTRIBUTION queries (e.g., "genre distribution", "rating distribution", "director distribution")
    - AGGREGATION queries (e.g., "average rating", "total revenue", "highest budget")
    Returns rich data including: revenue, budget, ROI, ratings, awards, genres, directors, opening weekend, and weekly box office.
    """
    print("Returning JSON payload of all movies")
    all_movies = [{"movie": movie} for movie in MOVIES_DB.values()]
    return json.dumps(all_movies, default=str)


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
    """Compare multiple movies side by side by their specific titles.
    ONLY use this when user mentions SPECIFIC movie names like 'Toy Story, The Matrix'.
    For comparing ALL movies by a field (like opening weekends, revenue), use get_all_movies() instead.

    Args:
        titles: Comma-separated movie titles e.g. 'Toy Story, The Matrix, Inception'
    """
    print(f"Comparing movies: {titles}")
    
    # Check if user is asking for "all movies" - redirect to get_all_movies()
    if "all" in titles.lower() and "movie" in titles.lower():
        print("Detected 'all movies' - redirecting to get_all_movies()")
        return get_all_movies()
    
    movie_list = [t.strip() for t in titles.split(",")]

    # Check if user is asking for a field comparison instead of specific movies
    field_keywords = [
        "opening",
        "weekend",
        "revenue",
        "budget",
        "roi",
        "rating",
        "profit",
    ]
    if any(keyword in titles.lower() for keyword in field_keywords):
        print(
            f"WARNING: '{titles}' looks like a field name, not movie titles. "
            "Consider using get_all_movies() instead."
        )
        return None

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
        get_all_movies,
        get_top_rated_movies,
        compare_movies,
        get_box_office_leaders,
    ],
    prompt="""You are a helpful movies assistant. Use the available tools to answer user questions about movies.

CRITICAL TOOL SELECTION RULES:
1. "compare opening weekends" / "compare revenue" / "all movies" → ALWAYS use get_all_movies()
2. IF USER MENTIONS A SPECIFIC MOVIE NAME in the query → use search_movie(title="Movie Name"):
   - "Show daily box office for The Dark Knight" → search_movie(title="The Dark Knight")
   - "Weekly revenue for Inception" → search_movie(title="Inception")
   - "Toy Story budget" → search_movie(title="Toy Story")
   - "box office for Interstellar" → search_movie(title="Interstellar")
   ⚠️  ONLY use search_movie() when user asks about ONE specific movie!
3. DISTRIBUTION/AGGREGATION queries → ALWAYS use get_all_movies():
   - "genre distribution", "rating distribution", "director distribution"
   - "average rating", "total revenue", "highest budget"
   - Any query asking about patterns/statistics across all movies
4. "top rated" / "best movies" → use get_top_rated_movies()
5. "Toy Story vs Matrix" (specific names) → use compare_movies(titles="Toy Story, The Matrix")
6. "highest grossing" / "box office leaders" → use get_box_office_leaders()

NEVER pass field names like "openingWeekend" or "revenue" to compare_movies().
compare_movies() ONLY accepts actual movie titles like "Toy Story, The Matrix".

The database includes: revenue, budget, profit, ROI, ratings, awards, genres, directors, openingWeekend, and weeklyBoxOffice.""",
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
