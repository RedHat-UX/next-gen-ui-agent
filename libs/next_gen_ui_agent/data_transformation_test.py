from next_gen_ui_agent.data_transformation import enhance_component_by_input_data
from next_gen_ui_agent.types import InputData, UIComponentMetadata


def test_enhance_component_by_input_data() -> None:
    movie1 = """
[
  {
    "movie":{
      "languages":[
        "English"
      ],
      "year":1995,
      "imdbId":"0114709",
      "runtime":81,
      "imdbRating":8.3,
      "movieId":"1",
      "countries":[
        "USA"
      ],
      "imdbVotes":591836,
      "title":"Toy Story",
      "url":"https://themoviedb.org/movie/862",
      "revenue":373554033,
      "tmdbId":"862",
      "plot":"A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room.",
      "posterUrl":"https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
      "released":"1995-11-22",
      "trailerUrl": "https://www.youtube.com/watch?v=v-PjgYDrg70",
      "budget":30000000
    },
    "actors":[
      "Jim Varney",
      "Tim Allen",
      "Tom Hanks",
      "Don Rickles"
    ]
  }
]
"""

    movie2 = """
[
  {
    "movie":{
      "languages":[
        "English"
      ],
      "year":1996,
      "imdbId":"0114709",
      "runtime":81,
      "imdbRating":8.3,
      "movieId":"1",
      "countries":[
        "USA"
      ],
      "imdbVotes":591836,
      "title":"No More",
      "url":"https://themoviedb.org/movie/862",
      "revenue":373554033,
      "tmdbId":"862",
      "plot":"A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room.",
      "posterUrl":"https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
      "released":"1995-11-22",
      "trailerUrl": "https://www.youtube.com/watch?v=v-PjgYDrg70",
      "budget":30000000
    },
    "actors":[
      "Jim Varney",
      "Tim Allen",
      "Tom Hanks",
      "Don Rickles"
    ]
  }
]
"""

    id = "test_id_1"
    input_data = InputData({"id": id, "data": movie1})
    input_data_2 = InputData({"id": "other", "data": movie2})

    component1 = UIComponentMetadata.model_validate(
        {
            "id": id,
            "title": "Toy Story Details",
            "reasonForTheComponentSelection": "One item available in the data",
            "confidenceScore": "100%",
            "component": "one-card",
            "fields": [
                {"name": "Title", "data_path": "movie.title"},
                {"name": "Year", "data_path": "movie.year"},
                {"name": "IMDB Rating", "data_path": "movie.imdbRating"},
                {"name": "Release Date", "data_path": "movie.released"},
                {"name": "Actors", "data_path": "actors[*]"},
            ],
        }
    )

    # put in two input data to be sure the correct one are selected
    enhance_component_by_input_data(
        input_data=[input_data_2, input_data], components=[component1]
    )
    fields = component1.fields
    assert fields[0].data == ["Toy Story"]
    assert fields[1].data == [1995]
    assert fields[2].data == [8.3]
    assert fields[3].data == ["1995-11-22"]  # TODO: Date time formatting
    assert fields[4].data == [
        "Jim Varney",
        "Tim Allen",
        "Tom Hanks",
        "Don Rickles",
    ]


if __name__ == "__main__":
    test_enhance_component_by_input_data()
