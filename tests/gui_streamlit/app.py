import asyncio
import json
import logging

import streamlit as st
from langchain_core.language_models import FakeMessagesListChatModel
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
component_one_card = UIComponentMetadata(
    {
        "id": "test_id_1",
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


def create_ngui_graph():
    msg = {"type": "assistant", "content": json.dumps(component_one_card)}
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


ngui_graph = create_ngui_graph()
assistant = ngui_graph.build_graph()

# Streamlit UI
st.set_page_config(initial_sidebar_state="collapsed", layout="wide")
st.text(
    "How it works: NextGenUI Agent takes Backend Data and prompt as input emulating real multi-agent scenario but "
    "LLM is faked implementation providing just mocked response and agent can redner the compomnent "
)

with st.expander("Backend Data"):
    st.code(json.dumps(movie, indent=2))

component_system: str = st.selectbox(
    label="Rendering System",
    options=ngui_graph.ngui_agent.renderers,
    key="component_system",
)


async def start_chat():
    # prompt = st.chat_input("Ask something about movies...")
    if prompt:
        logger.info(prompt)
        logger.info(movie)
        messages = []
        messages.append({"role": "user", "content": prompt})
        messages.append(
            {"role": "tool", "tool_call_id": "test-id", "content": json.dumps(movie)}
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        logger.debug("Sending mesages to the NGUI Agent.count=%s", len(messages))
        with st.chat_message("assistant"):
            col1, col2 = st.columns(2, gap="medium", border=False)
            with col1:
                st.subheader("LLM Mock Response")
                st.code(json.dumps(component_one_card, indent=2))

            try:
                async for msg, metadata in assistant.astream(
                    {"messages": messages},
                    {"configurable": {"component_system": component_system}},
                    stream_mode="messages",
                ):
                    langgraph_node = metadata["langgraph_node"]
                    if langgraph_node == "design_system_handler" and msg.content:
                        with col2:
                            st.subheader(f"NGUI Rendering - {component_system}")
                            if component_system == "json":
                                msg_json = json.loads(msg.content)
                                st.code(json.dumps(msg_json, indent=2, sort_keys=True))
                            else:
                                st.html(msg.content)
                        st.text("Rendering DONE")
            except Exception as e:
                logger.exception("Error in execution")
                with col2:
                    st.text(e)


asyncio.run(start_chat())
