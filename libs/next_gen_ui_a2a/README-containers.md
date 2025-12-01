# Next Gen UI Agent A2A Server Container (Dev Preview)

This module is part of the [Next Gen UI Agent project](https://github.com/RedHat-UX/next-gen-ui-agent).

[![Module Category](https://img.shields.io/badge/Module%20Category-AI%20Protocol-red)](https://github.com/RedHat-UX/next-gen-ui-agent)
[![Module Status](https://img.shields.io/badge/Module%20Status-Dev%20Preview-yellow)](https://github.com/RedHat-UX/next-gen-ui-agent)


## Provides

* container image to easily run Next Gen UI Agent A2A server

## Installation

```sh
podman pull quay.io/next-gen-ui/a2a:dev
```

## Usage

```sh
podman run --rm -p 9999:9999 \
    -e INFERENCE_MODEL=llama3.2 \
    -e OPEN_API_URL=http://host.containers.internal:11434/v1 \
    quay.io/next-gen-ui/a2a:dev
```

TODO: NGUI-493 improve documentation
