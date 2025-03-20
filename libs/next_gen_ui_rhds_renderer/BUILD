# This target sets the metadata for all the Python non-test files in this directory.
python_sources(
    name="lib"
)

# This target sets the metadata for all the Python test files in this directory.
python_tests(
    name="tests",
    dependencies=[
        "libs/3rdparty/python:pytest",
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
    dependencies=[":lib"],
    wheel=True,
    sdist=True,
    provides=setup_py(
        name="next_gen_ui_rhds_renderer",
        version="0.0.1",
        description="Next Gen UI Red Hat Design System Renderer",
        entry_points={
            'next_gen_ui.agent.renderer_factory': [
                'rhds = next_gen_ui_rhds_renderer.rhds_renderer:RhdsStrategyFactory'
            ],
        },
    ),
)
