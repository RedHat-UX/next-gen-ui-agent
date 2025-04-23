# Test Streamlit GUI

Testing GUI for running Next Gen UI agent with mocked agent's LLM response.

## Python Setup

Create venv via pants export:

```sh
pants export
```

Activate venv and configure python:

```sh
source dist/export/python/virtualenvs/python-default/3.11.11/bin/activate
export PYTHONPATH=./libs:./tests:$PYTHONPATH
```

## Run Streamlit

```sh
python -m streamlit run tests/gui_streamlit/app.py --server.runOnSave True
```

Or run in VS Code the `Python Debugger: streamlit` with opened `tests/gui/test_gui.py` file for debugging
