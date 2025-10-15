# Test Streamlit GUI

Testing GUI for running Next Gen UI agent with mocked agent's LLM response, so without real LLM.
It showcases `one-card`, `image` and `video` RHDS based dynamic components capabilities with relevant LLM outputs.
Its `Developer Console` screen allows to run/test agent's data transformation and server rendering steps, `json`, `rhds` or 
now deprecated server side Patternfly renderers can be selected to produce output rendered on this screen.

App is based on [Streamlit](https://streamlit.io/) GUI framework.

## Python Setup

Run next commands in the root of the git repo, not in this folder.

Create `venv` virtual environment with all dependencies via pants export:

**Note:** if you have `venv` already created as descriebed in the [`CONTRIBUTING.md`](../../CONTRIBUTING.md), 
you can skip this and use the exisiting one.

```sh
pants export
```

Activate `venv` and configure python:

```sh
# this expects `latest` venv symlink created, as described in `CONTRIBUTING.md`! You can also use your own python version here.
source dist/export/python/virtualenvs/python-default/latest/bin/activate
export PYTHONPATH=./libs:./tests:$PYTHONPATH
```

## Run Streamlit GUI

```sh
python -m streamlit run tests/gui_streamlit/app.py --server.runOnSave True
```

Or run in VS Code the `Python Debugger: streamlit` with opened `tests/gui/test_gui.py` file for debugging

Browser window with the app is opened  automatically.
