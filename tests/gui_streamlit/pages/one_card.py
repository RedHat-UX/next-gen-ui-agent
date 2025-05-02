import asyncio
import json

import streamlit as st
from gui_streamlit.assistant import execute_ngui_agent
from gui_streamlit.rhds_component import ngui_rhds_component
from next_gen_ui_agent.types import DataField, UIComponentMetadata
from next_gen_ui_testing.data_set_movies import find_movie

st.header("One Card")

prompt = "tell me details about Toy Story movie"
movie = find_movie("Toy Story")
input_data = json.dumps(movie, default=str)


def get_component():
    component_one_card = UIComponentMetadata.model_validate(
        {
            "title": "Toy Story Details",
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
    return component_one_card.model_copy()


component_system = "rhds"


async def case_fields():
    st.subheader("Multiple facts with no image")
    component = get_component()

    msg_content = await execute_ngui_agent(
        llm_data=component.model_dump(),
        prompt=prompt,
        input_data=input_data,
        component_system=component_system,
    )
    ngui_rhds_component(msg_content)


async def case_one_field():
    st.subheader("One Fact")
    component = get_component()
    component.fields.clear()
    component.fields.append(DataField(name="Plot", data_path="movie.plot"))

    msg_content = await execute_ngui_agent(
        llm_data=component.model_dump(),
        prompt=prompt,
        input_data=input_data,
        component_system=component_system,
    )
    ngui_rhds_component(msg_content)


async def case_image():
    st.subheader("Facts with image")
    component = get_component()
    component.fields.append(DataField(name="Poster", data_path="movie.posterUrl"))

    msg_content = await execute_ngui_agent(
        llm_data=component.model_dump(),
        prompt=prompt,
        input_data=input_data,
        component_system=component_system,
    )
    ngui_rhds_component(msg_content)


async def render():
    await case_fields()
    await case_one_field()
    await case_image()
    st.text(f"Rendering DONE: {component_system}")


asyncio.run(render())
