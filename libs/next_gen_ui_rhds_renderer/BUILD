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
    dependencies=[
        "libs/3rdparty/python:pytest",
        "libs/next_gen_ui_testing:tests",
    ],
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
        name="next_gen_ui_rhds_renderer",
        version=env("VERSION"),
        entry_points={
            "next_gen_ui.agent.renderer_factory": [
                "rhds = next_gen_ui_rhds_renderer:RhdsStrategyFactory"
            ],
        },
        license="Apache-2.0",
        description="RHDS Extension for Next Gen UI Agent",
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
    long_description_path="libs/next_gen_ui_rhds_renderer/README.md",
    generate_setup=True,
)
