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
$ Wrote symlink to immutable virtualenv for python-default (using Python 3.11.11) to dist/export/python/virtualenvs/python-default/3.11.11
```

Point our IDE interpreter to the venv `dist/export/python/virtualenvs/python-default/3.11.11` 
taken from previous step output (python version may differ here)

## Developer guide

### Prerequisities

Install dev deps

```sh
pip3 install -r requirements_dev.txt
```

Install pre commit hook

```sh
pre-commit install
```

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


## Versioning

Version is managed by commitizen and stored in [cz.toml](./cz.toml) and tagged in git.
All libraries has the same version.

### Bump version

Dry Run first and check output (changelog, version bump):
```sh
cz changelog --dry-run --unreleased-version="1.0.0"
cz bump --dry-run
# or with verion
cz bump 0.1.0 --dry-run
```

Perform version bump (release)

```sh
cz bump 0.1.0
git push --tags
```


## Release

Github Ci/CD pipeline automatically publish all packages. During every git push it pushes to [Test PyPI](https://test.pypi.org/project/next-gen-ui-agent/).
On Tag the pipeline build and pushes packages to [PyPI](https://pypi.org/project/next-gen-ui-agent/).

To perform actual release bump the version (see above).
