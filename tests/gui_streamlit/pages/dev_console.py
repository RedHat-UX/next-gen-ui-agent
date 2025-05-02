import asyncio
import json
import logging

import streamlit as st
from gui_streamlit.assistant import execute_ngui_agent
from gui_streamlit.rhds_component import ngui_rhds_component
from next_gen_ui_agent.types import UIComponentMetadata
from next_gen_ui_testing.data_set_movies import find_movie

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

prompt = "tell me details about Toy Story movie"
movie = find_movie("Toy Story")
movie.append({"testing": {"arrayNumbers": [1, 2, 3]}})
component_one_card = UIComponentMetadata.model_validate(
    {
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
            {"name": "Poster", "data_path": "movie.posterUrl"},
            # {"name": "testing.arrayNumbers[*]", "data_path": "testing.arrayNumbers[*]"},
        ],
    }
)
component_video_player = UIComponentMetadata.model_validate(
    {
        "title": "Toy Story Details",
        "reasonForTheComponentSelection": "One item available in the data",
        "confidenceScore": "100%",
        "component": "video-player",
        "fields": [
            {"name": "Title", "data_path": "movie.title"},
            {"name": "Video", "data_path": "movie.trailerUrl"},
        ],
    }
)


# Streamlit UI
st.header("Developer Console")

renderers = ["rhds", "json", "patternfly"]
if "renderer" not in st.session_state:
    st.session_state.renderer = renderers[0]


async def start_chat() -> None:
    col1, col2 = st.columns(2, gap="medium", border=False)
    with col1:
        st.subheader("Agent Input")
        st.text(
            "How it works: NextGen UI Agent takes Data and LLM Mocked response as component selection and configuration as input "
            "and renders desired output by LangGraph Agent adapter"
        )

        # with st.chat_message("user"):
        #     st.markdown(prompt)

        with st.expander("Data Selection"):
            input_data = st.text_area(
                "Data Selection",
                value=json.dumps(movie, indent=2, default=str),
                height=1000,
                label_visibility="hidden",
            )

        with st.expander("Component selection & configuration"):
            example_code = st.selectbox(
                label="Example",
                options=[
                    component_one_card.component,
                    component_video_player.component,
                ],
                key="example_code",
            )
            if example_code == component_one_card.component:
                llm_data = component_one_card
            if example_code == component_video_player.component:
                llm_data = component_video_player

            ngui_data = llm_data.model_dump_json(indent=4)
            ngui_data = st.text_area(
                "Component selection & configuration",
                value=ngui_data,
                height=1200,
                label_visibility="hidden",
            )

    with col2:
        st.subheader("Rendering")
        component_system: str = st.selectbox(
            label="Rendering System",
            options=renderers,
            key="renderer_select",
            index=renderers.index(st.session_state.renderer),
        )
        try:
            mocked_data = json.loads(ngui_data)
            msg_content = await execute_ngui_agent(
                llm_data=mocked_data,
                prompt=prompt,
                input_data=input_data,
                component_system=component_system,
            )

            match component_system:
                case "json":
                    msg_json = json.loads(msg_content)
                    st.code(
                        json.dumps(
                            msg_json,
                            indent=2,
                            sort_keys=True,
                            default=str,
                        )
                    )
                case "rhds":
                    ngui_rhds_component(msg_content)
                case _:
                    st.html(msg_content)
            st.text(f"Rendering DONE: {component_system}")
        except Exception as e:
            logger.exception("Error in execution")
            with col2:
                st.error(e)
                st.exception(e)


asyncio.run(start_chat())
