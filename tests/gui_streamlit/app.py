import asyncio
import json
import logging

import streamlit as st
from gui_streamlit.ngui_rhds_component import ngui_rhds_component
from langchain_core.language_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage, BaseMessage, ChatMessage, ToolMessage
from next_gen_ui_agent.renderer.base_renderer import PLUGGABLE_RENDERERS_NAMESPACE
from next_gen_ui_agent.types import UIComponentMetadata
from next_gen_ui_langgraph.agent import NextGenUILangGraphAgent
from next_gen_ui_patternfly_renderer.patternfly_renderer import (
    PatternflyStrategyFactory,
)
from next_gen_ui_rhds_renderer.rhds_renderer import RhdsStrategyFactory
from next_gen_ui_testing.data_set_movies import find_movie
from stevedore.extension import Extension, ExtensionManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

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


def create_ngui_graph(llm_data):
    msg = AIMessage(content=json.dumps(llm_data, default=str))
    ngui_model = FakeMessagesListChatModel(responses=[msg], cache=False)
    ngui_graph = NextGenUILangGraphAgent(ngui_model)
    extension_rhds = Extension(
        name="rhds", entry_point=None, plugin=None, obj=RhdsStrategyFactory()
    )
    extension_patternfly = Extension(
        name="patternfly",
        entry_point=None,
        plugin=None,
        obj=PatternflyStrategyFactory(),
    )
    em = ExtensionManager(PLUGGABLE_RENDERERS_NAMESPACE).make_test_instance(
        extensions=[extension_rhds, extension_patternfly],
        namespace=PLUGGABLE_RENDERERS_NAMESPACE,
    )
    ngui_graph.ngui_agent._extension_manager = em
    return ngui_graph


# Streamlit UI
st.set_page_config(initial_sidebar_state="collapsed", layout="wide")
st.header("Developer Console")

renderers = ["rhds", "json", "patternfly"]
if "renderer" not in st.session_state:
    st.session_state.renderer = renderers[0]


async def start_chat() -> None:
    messages: list[BaseMessage] = []
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
            ngui_graph = create_ngui_graph(mocked_data)
            assistant = ngui_graph.build_graph()
            logger.info(prompt)
            logger.info(input_data)

            messages.append(ChatMessage(content=prompt, role="user"))
            messages.append(ToolMessage(content=input_data, tool_call_id="test-id"))
            logger.debug("Sending mesages to the NGUI Agent.count=%s", len(messages))
            async for msg, metadata in assistant.astream(
                {"messages": messages},
                {"configurable": {"component_system": component_system}},
                stream_mode="messages",
            ):
                langgraph_node = metadata["langgraph_node"]
                if langgraph_node == "design_system_handler" and msg.content:
                    match component_system:
                        case "json":
                            msg_json = json.loads(msg.content)
                            st.code(
                                json.dumps(
                                    msg_json,
                                    indent=2,
                                    sort_keys=True,
                                    default=str,
                                )
                            )
                        case "rhds":
                            ngui_rhds_component(my_input_value=msg.content)
                        case _:
                            st.html(msg.content)
        except Exception as e:
            logger.exception("Error in execution")
            with col2:
                st.error(e)
                st.exception(e)

    st.text(f"Rendering DONE: {component_system}")


asyncio.run(start_chat())
