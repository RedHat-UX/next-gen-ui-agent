# This target sets the metadata for all the Python non-test files in this directory.
python_sources(
    name="lib",
    dependencies=[
        "libs/3rdparty/python:a2a",
    ],
)

# This target sets the metadata for all the Python test files in this directory.
python_tests(
    name="tests",
    dependencies=[
        "libs/3rdparty/python:a2a",
        "libs/3rdparty/python:pytest",
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
        name="next_gen_ui_a2a",
        version=env("VERSION"),
        license="Apache-2.0",
        description="A2A integration for Next Gen UI Agent",
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
    long_description_path="libs/next_gen_ui_a2a/README.md",
    generate_setup=True,
)

docker_image(
    name="docker",
    source="Containerfile",
    repository="next-gen-ui/a2a",
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
