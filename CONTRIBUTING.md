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

Python 3.12+ has to be installed on the computer.

Install [Pants Build](https://www.pantsbuild.org/stable/docs/getting-started/installing-pants).

On Linux, you can run `./get-pants.sh` available in the repo root, as described/recommended in the Pants Installation docs.

Install [Podman](https://podman.io/) to be able build images like `Next Gen UI MCP Server`.

### VSCode

The VSCode extension `Python` should be installed.

Run Pants export to create a virtual env

```sh
$ pants export
...
$ Wrote symlink to immutable virtualenv for python-default (using Python 3.12.11) to dist/export/python/virtualenvs/python-default/3.12.11
```

Create a symlink to the immutable virtualenv you've just created, so that our shared `.vscode` settings work. Make sure to use the right version coming from the previous command

```sh
ln -s $PWD/dist/export/python/virtualenvs/python-default/3.12.11 $PWD/dist/export/python/virtualenvs/python-default/latest
```

VS Code should automatically set the interepreter path to `./dist/export/python/virtualenvs/python-default/latest` (path taken from previous task).
If not point our IDE interpreter to this folder - CMD+Shift+P and type 'Python: Select Interpreter' to find the setting.

## LlamaStack server

Some parts of the project require local LamaStack server to be running for the development, for details see [LLAMASTACK_DEV.md](LLAMASTACK_DEV.md).

## Developer guide

### Prerequisities

# install dev requirements
```sh
pip install -r requirements_dev.txt
```

# Install dev deps

```sh
pip3 install -r requirements_dev.txt
```

# Install pre commit hook to perform python code lint and checks.

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

# Build all packages including python and docker
pants package ::

# Build only Python packages
pants package --filter-target-type=python_distribution ::
```

### Dependency Management

Dependencies are controled by Pants build. All 3rd party dependencies are managed in [libs/3rdparty/python/](./libs/3rdparty/python/) 
directory and categorized by frameworks.
During build/tests Pants automatically detects your dependencies from your source code and creates your dependency tree.

To check your dependencies you can run `pants dependencies --transitive tests/ai_eval_components/types.py` to see your dependencies of particular file.
The final list of required dependencies is in generated `setup.py` in the package in `dist` folder. Simply unzip the package.

All transitive dependencies should work. However some libraries does not manage their transitive dependencies very well resp. ask
the client to add needed dependencies manually. In this case we have to explicitly name them in BUILD file. For example `llama-stack-client`
has missing `fire` dependencies so we name them explicitly in [libs/next_gen_ui_llama_stack/BUILD](./libs/next_gen_ui_llama_stack/BUILD) file.

#### Adding a new dependencies

When adding a new module with net new libraries define them in separate requirements file in [libs/3rdparty/python/](./libs/3rdparty/python/) directory
and include it in the [libs/3rdparty/python/BUILD](./libs/3rdparty/python/BUILD) file.
It's recommendet to define a range which is supported.

Then regenerate lock file `pants generate-lockfiles` and refresh your virtual environtment by `pants export`.

#### Dependency constrains

The `llama-stack-client` is special dependency because it's used in [libs/next_gen_ui_llama_stack](./libs/next_gen_ui_llama_stack/) module as library 
dependency (with defined version range) but also we use llama-stack-client to run evaluations.

To pin exact version for running evals it's pinned in constraint 
file [libs/3rdparty/python/llama-stack-client-constraints.txt](./libs/3rdparty/python/llama-stack-client-constraints.txt) and 
defined in [BUILD](./BUILD) file. Beacuse of this constain the generated lock file will use only pinned version but same time 
the [libs/next_gen_ui_llama_stack](./libs/next_gen_ui_llama_stack/) module will require dependency range as defined in 
[libs/3rdparty/python/llama-stack-client-requirements.txt](./libs/3rdparty/python/llama-stack-client-requirements.txt).


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

#### Testing apps

New E2E testing app for the Next Gen UI Agent, demonstrating AI-driven UI component generation with a split server/client architecture, is available 
in [`/tests/ngui-e2e/` directory](/tests/ngui-e2e/). Its GUI is based on Patternfly and uses [Next Gen UI Patternfly React Renderer](https://github.com/RedHat-UX/next-gen-ui-react).
Server part exposes REST API for the GUI client, but also usefull for automatd testing.
See [`README.md`](/tests/ngui-e2e/README.md). 

Older GUI showcase/testing/developer console, based on [Streamlit](https://streamlit.io/) GUI framework, is available in [`/tests/gui_streamlit/` directory](/tests/gui_streamlit/). 
See [`README.md`](/tests/gui_streamlit/README.md). 


### Regenerating spec files

UI Agent spec files (JSON schema of component outputs, JSON schema of the agent configuration) are stored in `spec` subdirectories. 
To regenerate them, you have to run main method from the relevant `*_schema_test.py` file/s in the `spec` directory, then commit and push changes into git.

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
git push
git push --tags
```


## Release

Github Ci/CD pipeline automatically publish all packages. During every git push it pushes to [Test PyPI](https://test.pypi.org/project/next-gen-ui-agent/).
On Tag the pipeline build and pushes packages to [PyPI](https://pypi.org/project/next-gen-ui-agent/).

To perform actual release bump the version (see above).

## Documentation

### Documenting modules in source repo

Each folder in the source repo with separate project module, like library (python or Node.js), testing app, evaluation tool, has to have `README.md` file.

This file is used as a library package description during package release into PIPI or NPM repo, so make sure it makes sense at this locations.
But it is also included into projects documentation site (see next chapter). 

Be carefull when putting links into this file, you should always use absolute links here to work at all locations!

The file must start with the 1st level Heading with the module name. For the released packages (PIP, NPM), name must start wih the `Next Gen UI `.

Released packages must contain link pointing to the project repository `https://github.com/RedHat-UX/next-gen-ui-agent`, see example below.

Then there has to be two badges with categorization of the module.

Module category badge is one of:

* `Core` - UI agent's core functionality. 
    * Badge markup: `[![Module Category](https://img.shields.io/badge/Module%20Category-Core-blue)](https://github.com/RedHat-UX/next-gen-ui-agent)`
* `Testing/Evaluation` - testing and evaluation related module. Eg. library, evaluation framework or dataset, testing app etc.
    * Badge markup: `[![Module Category](https://img.shields.io/badge/Module%20Category-Testing/Evaluation-darkmagenta)](https://github.com/RedHat-UX/next-gen-ui-agent)`
* `AI framework` - AI framework binding, including inference providers. 
    * Badge markup: `[![Module Category](https://img.shields.io/badge/Module%20Category-AI%20Framework-darkred)](https://github.com/RedHat-UX/next-gen-ui-agent)`
* `AI Protocol` - AI protocol suppor/server. 
    * Badge markup: `[![Module Category](https://img.shields.io/badge/Module%20Category-AI%20Protocol-red)](https://github.com/RedHat-UX/next-gen-ui-agent)`
* `UI renderer` - UI renderer - in general info below, mention if it is a Server-Side or Client-Side. 
    * Badge markup: `[![Module Category](https://img.shields.io/badge/Module%20Category-UI%20Renderer-darkgreen)](https://github.com/RedHat-UX/next-gen-ui-agent)`

Module status badge is one of:

* `Tech Preview` - code/package which is in development and is not fully stable and supported yet. So API can change etc. 
    * Badge markup: `[![Module Status](https://img.shields.io/badge/Module%20Status-Tech%20Preview-orange)](https://github.com/RedHat-UX/next-gen-ui-agent)`
* `Supported` - code/package which is supported. Some functionality included in it can be `Tech Preview` still. 
    * Badge markup: `[![Module Status](https://img.shields.io/badge/Module%20Status-Supported-green)](https://github.com/RedHat-UX/next-gen-ui-agent)`
* `Deprecated` - code/package which is deprecated and will be removed in the future. 
    * Badge markup: `[![Module Status](https://img.shields.io/badge/Module%20Status-Deprecated-lightgray)](https://github.com/RedHat-UX/next-gen-ui-agent)`

Then provide some general info, what is the module about, with link to implemented frameworks etc.

Then there must be `Provides` chapter with list of exposed functionalities, code points etc. You can mark some of them as `Tech Preview` here.

For modules published as a library to repositories like `PyPI` or `NPM`, there must be `Links` chapter at the end, providing 
links to the Documentation, Source Codes, and Contributing info (in the documentation site).

Then there may be chapters about module installation, configuration, examples of use, screenshots etc. 
But generally not too much details should be here for modules which are covered in the documentation site (then details 
has to be in the documentation site), and mainly for modules published as a library to repositories like `PyPI` or `NPM`.
But include details for modules which are not covered in the documentation (eg. test apps etc.).


Example of the README for module published as a library into repo: 

```md
# Next Gen UI Core Functionality

This module is part of the [Next Gen UI Agent project](https://github.com/RedHat-UX/next-gen-ui-agent).

[![Module Category](https://img.shields.io/badge/Module%20Category-Core-blue)](https://github.com/RedHat-UX/next-gen-ui-agent)
[![Module Status](https://img.shields.io/badge/Module%20Status-Supported-green)](https://github.com/RedHat-UX/next-gen-ui-agent)

This module contains UI Agent Core functionality and frameworks.

## Provides

* `NextGenUIAgent` providing agent configuration and methods for individual processing steps
* extensible framework for "data transformation" step
* plugable "UI renderer" framework for rendering + default `json` renderer used for Client-Side renderers
* abstraction of the LLM inference
  * `InferenceBase` interface
  * `LangChainModelInference` implementation using LangChain `chat_models`.

## Links

* [Documentation](https://redhat-ux.github.io/next-gen-ui-agent/guide/ai_apps_binding/pythonlib/)
* [Source Codes](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs/next_gen_ui_agent)
* [Contributing](https://redhat-ux.github.io/next-gen-ui-agent/development/contributing/)

```

### Documentation site

Source files (markdown files, images) of the site are stored in `docs` directory. 

Main config file is `mkdocs.yml` in the project root. Documentation menu and other things are described here.

Some files are provided in `docs` directory, but some are copied from source directory structure, mainly modules `REDAME.md`s. 
Be carefull as linking between content in the `docs` directory and source directory structure doesn't work well - absolute 
links have to be used. So try to minimize use of source structure files in the docs.

### Running site locally

Install [MkDocs Material](https://squidfunk.github.io/mkdocs-material/).
This should be already done as installed from `requirements_dev.txt`.

```sh
pip install mkdocs-material
pip install mkdocs-include-markdown-plugin
```

Serve documentation locally

```sh
mkdocs serve
```

URL is shown in the console, where documentation site is available, typically [http://127.0.0.1:8000](http://127.0.0.1:8000).

Contribute in `docs` directory, local documentation site is automatically refreshed.

#### Build documentation

```sh
mkdocs build
```

#### Publish documentation

Documentation is automatically published to Github Pages on every commit / PR merge to `main` branch.
