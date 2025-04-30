# Data Set - Movies

import datetime

movies = [
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
            "released": datetime.datetime(2022, 11, 2),
            "trailerUrl": "https://www.youtube.com/watch?v=v-PjgYDrg70",
            "budget": 30000000,
        },
        "actors": ["Jim Varney", "Tim Allen", "Tom Hanks", "Don Rickles"],
    }
]


def find_movie(title: str):
    if not title:
        raise ValueError("title argment is required to query movies")
    return [m for m in movies if m["movie"]["title"] == title]  # type: ignore
