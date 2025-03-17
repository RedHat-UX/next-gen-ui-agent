from .data_transformation import enhance_component_by_input_data
from .datamodel import DataPath, InputData, UIComponentMetadata


def test_enhance_component_by_input_data():
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
    id = "test_id_1"
    input_data = InputData(id, movie1)

    component1 = UIComponentMetadata(
        id=id,
        title="Toy Story Details",
        reasonForTheComponentSelection="One item available in the data",
        confidenceScore="100%",
        component="one-card",
        fields=[
            DataPath(name="Title", data_path="movie.title"),
            DataPath(name="Year", data_path="movie.year"),
            DataPath(name="Actors", data_path="actors[*]"),
        ],
    )

    enhance_component_by_input_data(input_data=[input_data], components=[component1])
    assert component1.fields[0].data == ["Toy Story"]
    assert component1.fields[1].data == [1995]
    assert component1.fields[2].data == [
        "Jim Varney",
        "Tim Allen",
        "Tom Hanks",
        "Don Rickles",
    ]


if __name__ == "__main__":
    test_enhance_component_by_input_data()
