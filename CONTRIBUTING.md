# Contributing to Next Gen UI Agent

## Setup

Python 3.11+ has to be installed on the computer.

Install [Pants Build](https://www.pantsbuild.org/stable/docs/getting-started/installing-pants).

On Linux, you can run `./get-pants.sh` available in the repo root, as described/recommended in the Pants Installation docs.

### VSCode

Create virtual env

```sh
$ pants export
$ 14:52:09.05 [INFO] Completed: Get interpreter version
$ 14:52:14.52 [INFO] Completed: Build pex for resolve `python-default`
$ Wrote symlink to immutable virtualenv for python-default (using Python 3.11.11) to dist/export/python/virtualenvs/python-default/3.11.11
```

Point our IDE to the venv `dist/export/python/virtualenvs/python-default/3.11.11` (python version may differ here)

## Developer Guide

### Useful Pants Commands

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
