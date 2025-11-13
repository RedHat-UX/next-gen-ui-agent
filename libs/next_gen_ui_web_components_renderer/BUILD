# This target sets the metadata for all the Python non-test files in this directory.
python_sources(
    name="lib",
    dependencies=[
        "libs/next_gen_ui_agent:lib",
        ":jinja2",
        ":templates",
    ],
)

# This target sets the metadata for all the Python test files in this directory.
python_tests(
    name="tests",
)

python_requirement(
    name="jinja2",
    requirements=[
        "jinja2",
    ],
)

resources(
    name="templates",
    sources=["**/*.jinja"],
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
        name="next_gen_ui_web_components_renderer",
        version=env("VERSION"),
        entry_points={
            "next_gen_ui.agent.renderer_factory": [
                "web-components = next_gen_ui_web_components_renderer:WebComponentsStrategyFactory"
            ],
        },
        license="Apache-2.0",
        description="Web Components Renderer for Next Gen UI Agent",
        long_description_content_type="text/markdown",
        classifiers=[
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.12",
            "Programming Language :: Python :: 3.13",
            "Programming Language :: Python :: 3.14",
            "License :: OSI Approved :: Apache Software License",
        ],
        url="https://github.com/RedHat-UX/next-gen-ui-agent",
    ),
    generate_setup=True,
)
