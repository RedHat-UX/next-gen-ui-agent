# This target sets the metadata for all the Python non-test files in this directory.
# Note: MyPy checking is skipped for this test server code because it uses
# runtime-only relative imports that work in practice but are difficult to type-check.
python_sources(
    name="assistant_api",
    dependencies=[
        "libs/next_gen_ui_langgraph:lib",
        "libs/3rdparty/python:langchain",
        "libs/3rdparty/python:ngui-e2e-server",
    ],
    skip_mypy=True,
)

poetry_requirements(
    name="poetry",
)

python_requirements(
    name="reqs",
    source="pyproject.toml",
)
