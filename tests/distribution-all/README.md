# Tests of all distribution packages

It's expected that previous jobs run package goal:

```sh
pants package ::
```

## Create venv and install deps:

```sh
cd tests/distribution-all
rm -rf .venv && \
python3 -m venv .venv  && \
source .venv/bin/activate  && \
sh install_deps.sh && \
source .venv/bin/activate
```

## Run Test

```sh
pytest .
```

## Debugging

Dependencies:

```sh
pip install deptree
deptree
```


## Run other executables in libs directory

```sh
python ../../libs/next_gen_ui_langgraph/readme_example.py
```
