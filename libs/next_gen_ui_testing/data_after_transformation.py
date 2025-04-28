from next_gen_ui_agent import UIComponentMetadata

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
