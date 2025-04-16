# Test Streamlit GUI

Testing GUI for running Next Gen UI agent with mocked agent's LLM response.

## Pants Setup

```sh
pants export
```

## Run Streamlit

```sh
python -m streamlit run tests/gui_streamlit/app.py --server.runOnSave True
```

Or run in VS Code the `Python Debugger: streamlit` with opened `tests/gui/test_gui.py` file for debugging
