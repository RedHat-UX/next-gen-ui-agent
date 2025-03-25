# Tests of all distribution packages

It's expected that previous jobs run package goal:

```sh
pants package ::
```

## Run Test

```sh
python3 -m venv .venv
```

Install depenendcies:

```sh
sh install_deps.sh
source .venv/bin/activate
```

```sh
pytest .
```

## Debugging

Dependencies:

```sh
pip install deptree
deptree
```