from next_gen_ui_agent.data_transform.types import (
    ComponentDataImage,
    ComponentDataOneCard,
    ComponentDataVideo,
)
from next_gen_ui_agent.types import DataField

_transformed_component_one_card = ComponentDataOneCard.model_validate(
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

_transformed_component_image = ComponentDataImage.model_validate(
    {
        "id": "test_id_1",
        "title": "Toy Story Poster",
        "component": "image",
        "fields": [
            {"name": "Title", "data_path": "movie.title", "data": ["Toy Story"]},
            {
                "name": "Poster",
                "data_path": "movie.posterUrl",
            },
        ],
        "image": "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
    }
)

_transformed_component_video = ComponentDataVideo.model_validate(
    {
        "component": "video-player",
        "id": "test-id",
        "title": "Toy Story Trailer",
        "video": "https://www.youtube.com/embed/v-PjgYDrg70",
        "video_img": "https://img.youtube.com/vi/v-PjgYDrg70/maxresdefault.jpg",
    }
)


def get_transformed_component(component_name="one-card"):
    match component_name:
        case _transformed_component_one_card.component:
            return _transformed_component_one_card.model_copy()
        case _transformed_component_image.component:
            return _transformed_component_image.model_copy()
        case _transformed_component_video.component:
            return _transformed_component_video.model_copy()
        case _:
            raise Exception(
                f"Unkonwn _transformed_component component_name={component_name}"
            )


def get_transformed_component_testing_data():
    c = _transformed_component_one_card.model_copy()
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
    c.image = (
        "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg"
    )

    return c
