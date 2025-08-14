# Test Streamlit GUI

Testing GUI for running Next Gen UI agent with mocked agent's LLM response.

## Python Setup

Run next commands in the root of the git repo, not in this folder.

Create venv via pants export:

**Note:** if you have venv already created as descriebed in the [`CONTRIBUTING.md`](../../CONTRIBUTING.md), 
you can skip this and use the exisiting one.

```sh
pants export
```

Activate venv and configure python:

```sh
# change `3.11.11` in the path to your python version, or to `latest` for venv symlink created from `CONTRIBUTING.md`!
source dist/export/python/virtualenvs/python-default/3.11.11/bin/activate
export PYTHONPATH=./libs:./tests:$PYTHONPATH
```

## Run Streamlit

```sh
python -m streamlit run tests/gui_streamlit/app.py --server.runOnSave True
```

Or run in VS Code the `Python Debugger: streamlit` with opened `tests/gui/test_gui.py` file for debugging
