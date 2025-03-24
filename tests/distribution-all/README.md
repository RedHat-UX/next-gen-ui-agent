#

It's expected that previous jobs run package goal:

```sh
pants package ::
```

## Run Test

```sh
python3 -m venv .venv
source .venv/bin/activate
```

Install depenendcies:

```sh
sh install_deps.sh
```

```sh
python -m pytest  .
```

## Debugging

Dependencies:

```sh
pip install deptree
deptree
```