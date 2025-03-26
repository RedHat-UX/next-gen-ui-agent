# Tests of all distribution packages

It's expected that previous jobs run package goal:

```sh
pants package ::
```

## Create venv and install deps:

```sh
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