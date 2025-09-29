# This target sets the metadata for all the Python non-test files in this directory.
python_sources(
    name="lib",
    dependencies=[
        "libs/3rdparty/python:mcp",
        "libs/next_gen_ui_agent:lib",
    ],
    sources=[
        "!server_example.py",
        "!mcp_client_example.py",
        "!**/*_test.py",
        "**/*.py",
    ],
)

# This target is specifically made for playing with the MCP server and client
# It hooks up additional renderer libraries to be able to use them with the client
python_sources(
    name="extended",
    sources=["server_example.py", "mcp_client_example.py"],
    dependencies=[
        "libs/3rdparty/python:mcp",
        "libs/3rdparty/python:custom-renderers",
        "libs/3rdparty/python:agent-core",
        "libs/3rdparty/python:llama-stack",
        "libs/3rdparty/python:langchain",
        "libs/next_gen_ui_llama_stack:lib",
        "libs/next_gen_ui_agent:lib",
    ],
)

# This target sets the metadata for all the Python test files in this directory.
python_tests(
    name="tests",
    sources=["agent_test.py"],
    dependencies=[
        "libs/3rdparty/python:pytest",
        "libs/3rdparty/python:mcp",
        "libs/3rdparty/python:agent-core",
        "libs/next_gen_ui_testing:tests",
    ],
)

# This target allows us to build a `.whl` bdist and a `.tar.gz` sdist by auto-generating
#  `setup.py`. See https://www.pantsbuild.org/docs/python-distributions.
#
# Because this target has no source code, Pants cannot infer dependencies. We depend on `:lib`,
#  which means we'll include all the non-test Python files in this directory, and any of
#  their dependencies.
python_distribution(
    name="dist",
    dependencies=[
        ":lib",
    ],
    provides=python_artifact(
        name="next_gen_ui_mcp",
        version=env("VERSION"),
        license="Apache-2.0",
        description="MCP Integration for Next Gen UI Agent",
        long_description_content_type="text/markdown",
        classifiers=[
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.12",
            "Programming Language :: Python :: 3.13",
            "License :: OSI Approved :: Apache Software License",
        ],
        url="https://github.com/RedHat-UX/next-gen-ui-agent",
    ),
    long_description_path="libs/next_gen_ui_mcp/README.md",
    generate_setup=True,
)

docker_image(
    name="docker",
    source="Containerfile",
    repository="next-gen-ui/mcp",
    image_tags=[env("VERSION"), "latest", "dev"],
    registries=[
        "quay.io",
    ],
    dependencies=[
        ":dist",
        "libs/next_gen_ui_agent:dist",
        "libs/next_gen_ui_rhds_renderer:dist",
    ],
)
