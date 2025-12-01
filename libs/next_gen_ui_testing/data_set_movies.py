# Data Set - Movies
# Comprehensive movie database with box office, awards, and weekly performance data for testing

import json
from typing import Any, Optional

# Movie database with comprehensive data including box office, awards, and weekly performance
MOVIES_DB: dict[str, dict[str, Any]] = {
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


# Tool Functions for Testing


def search_movie(title: str):
    """Search for a specific movie by title.

    Args:
        title: Movie title e.g. 'Toy Story', 'Inception'
    """
    title_lower = title.lower().replace(" ", "_")
    for key, movie_data in MOVIES_DB.items():
        if title_lower in key or key in title_lower:
            print(f"Returning JSON payload of '{title}' movie")
            return json.dumps([{"movie": movie_data}], default=str)
    return None


def get_all_movies(
    director: Optional[str] = None,
    genre: Optional[str] = None,
    actor: Optional[str] = None,
    year: Optional[int] = None,
    min_year: Optional[int] = None,
    max_year: Optional[int] = None,
    min_rating: Optional[float] = None,
):
    """Get movies from the database with optional filtering.

    Returns movies with revenue, budget, profit, ROI, ratings, awards, genres,
    directors, actors, opening weekend, and weekly box office data.

    Args:
        director: Filter by director name (case-insensitive, partial match)
        genre: Filter by genre (case-insensitive, partial match)
        actor: Filter by actor name (case-insensitive, partial match)
        year: Filter by exact release year
        min_year: Filter movies released on or after this year
        max_year: Filter movies released on or before this year
        min_rating: Filter movies with IMDB rating >= this value

    Examples:
        get_all_movies(director="Christopher Nolan")
        get_all_movies(genre="Sci-Fi", min_rating=8.0)
        get_all_movies(year=2008)
        get_all_movies(min_year=2000, max_year=2010)
        get_all_movies(actor="Tom Hanks")
    """
    # Normalize special "no filter" values to None
    if director and director.lower() in ("any", "all"):
        director = None
    if genre and genre.lower() in ("any", "all"):
        genre = None
    if actor and actor.lower() in ("any", "all"):
        actor = None

    filter_desc = []
    if director:
        filter_desc.append(f"director='{director}'")
    if genre:
        filter_desc.append(f"genre='{genre}'")
    if actor:
        filter_desc.append(f"actor='{actor}'")
    if year:
        filter_desc.append(f"year={year}")
    if min_year:
        filter_desc.append(f"min_year={min_year}")
    if max_year:
        filter_desc.append(f"max_year={max_year}")
    if min_rating:
        filter_desc.append(f"min_rating={min_rating}")

    filter_str = f" with filters: {', '.join(filter_desc)}" if filter_desc else ""
    print(f"Returning JSON payload of movies{filter_str}")

    # Apply filters
    filtered_movies = []
    for movie in MOVIES_DB.values():
        # Director filter
        if director and director.lower() not in movie["director"].lower():
            continue

        # Genre filter (check if genre is in the movie's genres list)
        if genre and not any(genre.lower() in g.lower() for g in movie["genres"]):
            continue

        # Actor filter (check if actor is in the movie's actors list)
        if actor and not any(actor.lower() in a.lower() for a in movie["actors"]):
            continue

        # Year filters
        if year and movie["year"] != year:
            continue
        if min_year and movie["year"] < min_year:
            continue
        if max_year and movie["year"] > max_year:
            continue

        # Rating filter
        if min_rating and movie["imdbRating"] < min_rating:
            continue

        filtered_movies.append({"movie": movie})

    return json.dumps(filtered_movies, default=str)


# Legacy function for backward compatibility
def find_movie(title: str):
    """Legacy function for backward compatibility. Use search_movie instead."""
    if not title:
        raise ValueError("title argument is required to query movies")
    result = search_movie(title)
    return json.loads(result) if result else []
