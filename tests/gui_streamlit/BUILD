# This target sets the metadata for all the Python non-test files in this directory.
python_sources(
    name="lib",
    sources=[
        "**/*.py",
        "!*/*_test.py",
    ],
    dependencies=[
        "libs/next_gen_ui_agent:lib",
        "libs/next_gen_ui_langgraph:lib",
    ],
)

python_tests(
    name="tests",
    dependencies=[
        "libs/3rdparty/python:pytest",
        ":lib",  # streamlit needs to see app.py
    ],
)

python_requirements(
    name="reqs",
)
