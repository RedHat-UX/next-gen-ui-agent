# This target sets the metadata for all the Python non-test files in this directory.
python_sources(
    name="tests",
)

python_distribution(
    name="dist",
    dependencies=[
        ":tests",
    ],
    provides=python_artifact(
        name="next_gen_ui_testing",
        version=env("VERSION"),
        license="Apache-2.0",
        description="Testing data Next Gen UI",
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
    long_description_path="libs/next_gen_ui_testing/README.md",
    generate_setup=True,
)
