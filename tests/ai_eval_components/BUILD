# This target sets the metadata for all the Python non-test files in this directory.
python_sources(
    name="lib",
    dependencies=[
        # Has to be explicitly noted because of missing trans deps in llama-stack-client
        "libs/3rdparty/python:llama-stack",
    ],
)

python_tests(
    name="tests",
)
