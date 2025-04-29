from next_gen_ui_agent import UIComponentMetadata
from next_gen_ui_agent.types import DataField

_transformed_component = UIComponentMetadata.model_validate(
    {
        "id": "test_id_1",
        "title": "Toy Story Details",
        "reasonForTheComponentSelection": "One item available in the data",
        "confidenceScore": "100%",
        "component": "one-card",
        "fields": [
            {"name": "Title", "data_path": "movie.title", "data": ["Toy Story"]},
            {"name": "Year", "data_path": "movie.year", "data": ["1995"]},
            {
                "name": "IMDB Rating",
                "data_path": "movie.imdbRating",
                "data": ["8.3"],
            },
            {
                "name": "Release Date",
                "data_path": "movie.released",
                "data": ["1995-11-22"],
            },
            {
                "name": "Actors",
                "data_path": "actors[*]",
                "data": ["Jim Varney", "Tim Allen", "Tom Hanks", "Don Rickles"],
            },
        ],
    }
)


def get_transformed_component():
    return _transformed_component.model_copy()


def get_transformed_component_testing_data():
    c = _transformed_component.model_copy()
    c.fields.append(
        DataField(
            name="testing.arrayNumbers[*]",
            data_path="testing.arrayNumbers[*]",
            data=[1, 2, 3],
        )
    )
    c.fields.append(
        DataField(
            name="testing.arrayBooleans[*]",
            data_path="testing.arrayBooleans[*]",
            data=[True, False],
        )
    )
    c.fields.append(
        DataField(
            name="Poster",
            data_path="movie.posterUrl",
            data=[
                "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg"
            ],
        )
    )

    return c
