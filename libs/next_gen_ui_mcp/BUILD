# This target sets the metadata for all the Python non-test files in this directory.
python_sources(
    name="lib",
    dependencies=[
        "libs/next_gen_ui_agent:lib",
    ],
)

# This target sets the metadata for all the Python test files in this directory.
python_tests(
    name="tests",
    sources=["agent_test.py"],
    dependencies=[
        "libs/next_gen_ui_agent:lib",
        "libs/next_gen_ui_beeai:lib",
        "libs/next_gen_ui_testing:tests",
        "libs/3rdparty/python:pytest",
    ],
)

# Integration test that requires Llama Stack dependencies (optional)
python_tests(
    name="integration_tests",
    sources=["llamastack_mcp_integration_test.py"],
    dependencies=[
        "libs/next_gen_ui_agent:lib",
        "libs/3rdparty/python:pytest",
        ":lib",
    ],
)

python_requirements(
    name="reqs",
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
        ":reqs",
    ],
    provides=python_artifact(
        name="next_gen_ui_mcp",
        version=env("VERSION"),
        license="Apache-2.0",
        description="MCP Integration for Next Gen UI Agent",
        long_description_content_type="text/markdown",
        classifiers=[
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Programming Language :: Python :: 3.13",
            "License :: OSI Approved :: Apache Software License",
        ],
        url="https://github.com/RedHat-UX/next-gen-ui-agent",
    ),
    long_description_path="README.md",
    generate_setup=True,
)
