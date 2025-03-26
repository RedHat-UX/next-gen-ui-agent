# Contributing to Next Gen UI Agent

Thank you for being interested in contributing to Next Gen UI Agent!

## General guidelines
Here are some things to keep in mind for all types of contributions:

* Follow the ["fork and pull request"](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project) workflow.
* Ensure your PR passes formatting, linting, and testing checks before requesting a review. Run `pants fmt lint check ::`
* Keep scope as isolated as possible. As a general rule, your changes should not affect more than one package at a time.


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

### Useful Pants commands

```sh
# show dependencies
pants dependencies ::
# Regenerate lock file (after changing deps)
pants generate-lockfiles

# Run all tests
pants test ::

# Run python file
pants run libs/next_gen_ui_llama_stack/agent_test.py

# Run formatter, linter, check
pants fmt lint check ::
```


## Versioning

TOOD: Explain versioning

## Release

TODO: Add release steps
