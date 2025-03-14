# Contributing to Next Gen UI Agent

## Setup

Install [Pants Build](https://www.pantsbuild.org/stable/docs/getting-started/installing-pants)

### VSCode

Create virtual env

```sh
$ pants export --py-resolve-format=symlinked_immutable_virtualenv --resolve=python-default
$ 14:52:09.05 [INFO] Completed: Get interpreter version
$ 14:52:14.52 [INFO] Completed: Build pex for resolve `python-default`
$ Wrote symlink to immutable virtualenv for python-default (using Python 3.11.11) to dist/export/python/virtualenvs/python-default/3.11.11
```

Point our IDE to the venv `dist/export/python/virtualenvs/python-default/3.11.11`

## Developer Guide

### Useful Pants Commands

```sh
# show dependencies
pants dependencies ::
# Regenerate lock file (after changing deps)
pants generate-lockfiles --resolve=python-default

# Run all tests
pants test ::

# Run python file
pants run libs/next_gen_ui_llama_stack/agent_test.py

# Run formatter, linter, check
pants fmt lint check ::
```
