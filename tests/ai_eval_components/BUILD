# This target sets the metadata for all the Python non-test files in this directory.
python_sources(
    name="lib",
    dependencies=[
        "libs/next_gen_ui_agent:lib",
        "libs/next_gen_ui_llama_stack:lib",
        ":llama-stack",
    ],
)

python_tests(
    name="tests",
    dependencies=[
        "libs/3rdparty/python:pytest",
        "libs/3rdparty/python:langchain",
    ],
)

python_requirements(
    name="llama-stack",
    source="llama-stack-requirements.txt",
)
