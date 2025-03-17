# Setup langgraph dev server

## Build whole project

```sh
pants package ::
```

### Create an environment and install dependencies

```sh
cd libs/next_gen_ui_langgraph
python3 -m venv .venv
source .venv/bin/activate
pip install -U -r requirements.txt
pip install -U langgraph-cli
pip install -U "langgraph-cli[inmem]"
pip install --force-reinstall ../../dist/next_gen_ui_agent-0.0.1-py3-none-any.whl
```


### Run Langgraph Dev 

```sh
source .venv/bin/activate
langgraph dev
```
