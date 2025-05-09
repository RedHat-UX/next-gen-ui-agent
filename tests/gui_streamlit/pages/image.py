import asyncio
import json

import streamlit as st
from gui_streamlit.assistant import execute_ngui_agent
from gui_streamlit.rhds_component import ngui_rhds_component
from next_gen_ui_agent.types import UIComponentMetadata
from next_gen_ui_testing.data_set_movies import find_movie

st.header("Image")

prompt = "tell me details about Toy Story movie"
movie = find_movie("Toy Story")
input_data = json.dumps(movie, default=str)

st.sidebar.header("Image")
st.sidebar.text("Input data:")
st.sidebar.code(json.dumps(movie, default=str, indent=2))


@st.dialog("Agent LLM Mocked Response")
def show_llm_input(component: UIComponentMetadata):
    st.code(component.model_dump_json(indent=2, exclude_unset=True))


def get_component():
    component_one_card = UIComponentMetadata.model_validate(
        {
            "title": "Toy Story Poster",
            "component": "image",
            "fields": [
                {"name": "Title", "data_path": "movie.title"},
                {"name": "Year", "data_path": "movie.year"},
                {"name": "Poster", "data_path": "movie.posterUrl"},
            ],
        }
    )
    return component_one_card.model_copy()


component_system = "rhds"


async def case_image():
    st.subheader("Image with title")
    component = get_component()

    msg_content = await execute_ngui_agent(
        llm_data=component.model_dump(),
        prompt=prompt,
        input_data=input_data,
        component_system=component_system,
    )
    ngui_rhds_component(msg_content)
    if st.button("Agent LLM Mocked Response", key="llm_case_image"):
        show_llm_input(component)


async def render():
    await case_image()
    st.text(f"Rendering DONE: {component_system}")


asyncio.run(render())
