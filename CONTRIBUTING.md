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

1. Python 3.12+ has to be installed on the computer.

2. Install [Pants Build](https://www.pantsbuild.org/stable/docs/getting-started/installing-pants). On Linux, you can run `./get-pants.sh` available in the repo root, as described/recommended in the Pants Installation docs.

3. Install [Podman](https://podman.io/) to be able build images like `Next Gen UI MCP Server`.

4. Clone [UI Agent github repository](https://github.com/RedHat-UX/next-gen-ui-agent).

5. Create python virtual environment with all required dependencies - run Pants export in the cloned repo root directory. Created virtual environment is used by all Pants commands.

```sh
$ pants export
```

6. Create a symlink for the virtual environment you've just created, so that you can activate it by stable command, and our shared VS Code settings work.
Make sure to use the right python version in the path (the path was created by the previous command).

```sh
ln -s $PWD/dist/export/python/virtualenvs/python-default/3.12.11 $PWD/dist/export/python/virtualenvs/python-default/latest
```

If you want to run project's python code out of the Pants commands or VS Code, you must activate the vitual environmet:

```sh
source dist/export/python/virtualenvs/python-default/latest/bin/activate
```

7. You can also clone other github repositories if you need. For setup follow their README.md:

   * https://github.com/RedHat-UX/next-gen-ui-react
   * https://github.com/RedHat-UX/next-gen-ui-examples 


### VS Code / Cursor setup

Install Python (`ms-python`) extension if not installed yet.

Open project root directory in VS Code / Cursor.

VS Code should automatically set the python interepreter path to `./dist/export/python/virtualenvs/python-default/latest` (virtual environment simlink created during *Setup* steps)
thanks to the config shared in the `.vscode/settings.js`.
If not, point your IDE interpreter to this folder - CMD+Shift+P and type 'Python: Select Interpreter' to find the setting.

There are also launch configurations defined to be used in `Run and Debug` view. 
You can run any current file requiring modules from `/libs` directory using `Python Debugger: Current File` configuration.
There is bunch of others for special purposes.

## LlamaStack server

Some parts of the project require LamaStack server to be running on your laptop for the development, for details see [LLAMASTACK_DEV.md](LLAMASTACK_DEV.md).

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

* `feat` -> MINOR
* `fix` -> MICRO
* `refactor` -> MICRO

You can also use other types which are not reflected in changelog. The most usefull are:

* `docs` - change in documentation
* `chore` - any change not necessary in the changelog, like build/CI/CD changes etc.

Example: `refactor(NGUI-123): refactoring agent tests`

### Useful Pants commands

```sh
# Show dependencies
pants dependencies ::
# Regenerate dependencies lock file - run after changing deps, do not forget to run `pants export` to refresh venv for local development then. It upgrades all dependencies to latest values matching version restrictions!
pants generate-lockfiles

# Create python virtual environment for local development, with all necessary dependencies from the lock file
pants export

# Run all tests
pants test ::

# Run given python file
pants run libs/next_gen_ui_llama_stack/agent_test.py

# Run code formatter, linter, checks
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
the client to add needed dependencies manually. In this case we have to explicitly name them in `BUILD` file. For example `llama-stack-client`
has missing `fire` dependencies so we name them explicitly in [libs/next_gen_ui_llama_stack/BUILD](./libs/next_gen_ui_llama_stack/BUILD) file.

#### Adding a new dependencies

When adding a new module with net new libraries define them in separate requirements file in [libs/3rdparty/python/](./libs/3rdparty/python/) directory
and include it in the [libs/3rdparty/python/BUILD](./libs/3rdparty/python/BUILD) file.
It's recommendet to define a range which is supported.

Then regenerate lock file `pants generate-lockfiles` and refresh your virtual environtment by `pants export`. Then commit lock file into git.

Try to reasonably restrict version of the newly added dependency, as `pants generate-lockfiles` upgrades everything to newest possible version matching restricitons.
If version is not restricted, this command can perform major version upgrade and break code / tests. It is not easy to look for versions of distinct
dependencies you haven't touch and restrict / downgrade them!

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

##### Writing tests

[PyTest](https://docs.pytest.org/en/stable/) library is used to write unit tests in modules.

Every piece of functionality should be covered by unit tests if possible.
Unit tests are placed in separate file next to the tested code, in file with `_test.py` suffix.
You can use classes to group together unit tests for one tested method.

Use `@pytest.mark.asyncio` decorator to mark method testing aync methods.

Use `with pytest.raises(ValueError, match="Invalid JSON format of the Input Data: "):` construct to tests exception is thrown.

No real LLM is used in these tests, responses are mocked where necessary.

##### Running tests

You can use [Pants test](https://www.pantsbuild.org/dev/docs/python/goals/test) to run them.

Running all tests:

```sh
pants test ::
```

Running one test file:

```sh
pants run libs/next_gen_ui_llama_stack/agent_test.py
```

You can also use `Testing` view in VS Code / Cursor, or run them directly from the test file source code using green arrows on the left of each test method.

#### Evaluation of the AI functionality

Evaluation of the UI component selection and configuration AI powered functionality is available in the `tests/ai_eval_components` module.
For more details see its [README.md](tests/ai_eval_components/README.md). It requires some LLM to be available.

#### Testing apps

New E2E testing app for the Next Gen UI Agent, demonstrating AI-driven UI component generation with a split server/client architecture, is available 
in [`/tests/ngui-e2e/` directory](/tests/ngui-e2e/). Its GUI is based on Patternfly and uses [Next Gen UI Patternfly React Renderer](https://github.com/RedHat-UX/next-gen-ui-react).
Server part exposes REST API for the GUI client, but also usefull for automatd testing.
See [`README.md`](/tests/ngui-e2e/README.md). 

Older GUI showcase/testing/developer console, based on [Streamlit](https://streamlit.io/) GUI framework, is available in [`/tests/gui_streamlit/` directory](/tests/gui_streamlit/). 
See [`README.md`](/tests/gui_streamlit/README.md). 


### Regenerating spec files

UI Agent spec files (JSON schema of component outputs, JSON schema of the agent configuration) are stored in `spec` subdirectories. 
To regenerate them, you need to run main method from `spec/schema_test.py` file, then review, commit and push changes into git.

```sh
PYTHONPATH=./libs python spec/schema_test.py
```

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

Paste generated changelog to CHANGELOG.TXT (do not commit!), select it and ask Cursor for selected text:

```
Create release notes that clearly document:
 - A high-level overview of the release.
 - Key features and benefits.
 - Known issues or limitations.
```

Cursor should update `release_notes.md` for you.
Create a PR with generated notes and label PR as `AI Assisted`. Then manually currate it and push changes again.
Finally merge PR and do `Perform version bump (release)` locally.

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
