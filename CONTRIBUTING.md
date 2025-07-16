# Contributing to Next Gen UI Agent

Thank you for being interested in contributing to Next Gen UI Agent!

## General guidelines
Here are some things to keep in mind for all types of contributions:

* Follow the ["fork and pull request"](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project) workflow.
* Ensure your PR passes formatting, linting, and testing checks before requesting a review. Run `pants fmt lint check ::`
* Keep scope as isolated as possible. As a general rule, your changes should not affect more than one package at a time.
* Use always conventional commits message style.
* Install `pre-commit` hooks.

## Setup

Python 3.11+ has to be installed on the computer.

Install [Pants Build](https://www.pantsbuild.org/stable/docs/getting-started/installing-pants).

On Linux, you can run `./get-pants.sh` available in the repo root, as described/recommended in the Pants Installation docs.

### VSCode

Run Pants export to create a virtual env

```sh
$ pants export
...
$ Wrote symlink to immutable virtualenv for python-default (using Python 3.11.13) to dist/export/python/virtualenvs/python-default/3.11.13
```

Create a symlink to the immutable virtualenv you've just created, so that our shared `.vscode` settings work. Make sure to use the right version coming from the previous command

```sh
ln -s $PWD/dist/export/python/virtualenvs/python-default/3.11.13 $PWD/dist/export/python/virtualenvs/python-default/latest
```

VS Code should automatically set the interepreter path to `./dist/export/python/virtualenvs/python-default/latest` (path taken from previous task).
If not point our IDE interpreter to this folder - CMD+Shift+P and type 'Python: Select Interpreter' to find the setting.

## LlamaStack server

Some parts of the project require local LamaStack server to be running for the development, for details see [LLAMASTACK_DEV.md](LLAMASTACK_DEV.md).

## Developer guide

### Prerequisities

Install dev deps

```sh
pip3 install -r requirements_dev.txt
```

Install pre commit hook to perform python code lint and checks.

```sh
pre-commit install
```

You should run `pants fmt lint check ::` before every commit to be sure commit won't fail.

### Commit Message Guidelines

Follows the [Angular guidline types](https://github.com/angular/angular/blob/22b96b9/CONTRIBUTING.md#type) to ensure the commit will appear in changelog.
Also use NGUI JIRA next to the change type.

These types goes to changelog and control the version bump:
* feat -> MINOR
* fix -> MICRO
* refactor -> MICRO

Example: `refactor(NGUI-123): refactoring agent tests`

### Useful Pants commands

```sh
# show dependencies
pants dependencies ::
# Regenerate lock file (after changing deps, do not forget to run `pants export` for local development)
pants generate-lockfiles

# Run all tests
pants test ::

# Run python file
pants run libs/next_gen_ui_llama_stack/agent_test.py

# Run formatter, linter, check
pants fmt lint check ::
```

### Testing

#### Unit tests

[PyTest](https://docs.pytest.org/en/stable/) library is used to write unit tests in modules.

You can use [Pants test](https://www.pantsbuild.org/dev/docs/python/goals/test) to run them:

Running all tests:
```sh
pants test ::
```

#### Evaluation of the AI functionality

Evaluation of the UI component selection and configuration AI powered functionality is available in the `tests/ai_eval_components` module.
For more details see its [README.md](tests/ai_eval_components/README.md).


## Versioning

Version is managed by commitizen and stored in [cz.toml](./cz.toml) and tagged in git.
All libraries has the same version.

### Check version & changelog

Dry Run first and check output (changelog, version bump):
```sh
cz changelog --dry-run --unreleased-version="0.1.0"
cz bump --dry-run
# or with verion
cz bump 0.1.0 --dry-run
```

### Generate release notes

Take changelog and genereate a Release Notes by [Google Gemini](https://gemini.google.com/) with following prompt and pasted changelog:

```
Create release notes that clearly document:
 - A high-level overview of the release.
 - Key features and benefits.
 - Known issues or limitations.

The changelog for this release is following:
<CHANGELOG.TXT - only particular version>
```

Review generated release notes and add it into [docs/development/release_notes.md](./docs/development/release_notes.md) and push it to main branch.

### Perform version bump (release)

```sh
cz bump 0.1.0
git push --tags
```


## Release

Github Ci/CD pipeline automatically publish all packages. During every git push it pushes to [Test PyPI](https://test.pypi.org/project/next-gen-ui-agent/).
On Tag the pipeline build and pushes packages to [PyPI](https://pypi.org/project/next-gen-ui-agent/).

To perform actual release bump the version (see above).

## Documentation

Install [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)

```sh
pip install mkdocs-material
pip install mkdocs-include-markdown-plugin
```

Serve documentation locally

```sh
mkdocs serve
```

and contribute in `docs` directory.

### Build documentation

```sh
mkdocs build
```
