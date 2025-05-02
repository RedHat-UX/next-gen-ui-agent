import logging

import streamlit as st

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


st.set_page_config(
    page_title="Next Gen UI Demo App",
    # page_icon=favicon,
    initial_sidebar_state="expanded",
    layout="wide",
)


pages = [
    st.Page("pages/welcome.py", title="Welcome"),
    st.Page("pages/one_card.py", title="One Card"),
    st.Page("pages/dev_console.py", title="Developer Console"),
]

pg = st.navigation(pages)
pg.run()
