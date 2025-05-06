python_tests(
    name="tests",
    dependencies=[
        "libs/3rdparty/python:pytest",
        "libs/next_gen_ui_agent:lib",
        ":schemas",
    ],
)

resources(
    name="schemas",
    sources=["**/*.schema.json"],
)
