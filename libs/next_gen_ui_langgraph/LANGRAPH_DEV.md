# Setup langgraph dev server

## Build whole project

```sh
pants package ::
pip install 
```

### Create an environment and install dependencies

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -U -r requirements.txt
pip install -U langgraph-cli
pip install -U "langgraph-cli[inmem]"
```


### Run Langgraph Dev 

```sh
source .venv/bin/activate
langgraph dev
```
