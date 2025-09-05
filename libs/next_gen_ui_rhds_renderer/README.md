# Next Gen UI Red Hat Design System Plugin

Module category: `UI renderer`  
Module status: `Supported`

This Python package provides a plugin which will enable a renderer for Next Gen UI Agent that produces [Red Hat Design System Web Components](https://ux.redhat.com/) as an output.

Next Gen UI Agent utilises [Stevedore Plugin framework](https://docs.openstack.org/stevedore/latest/index.html) which automates to a high degree how you can configure this plugin to work in your deployment.

## Installation

```sh
pip install -U next_gen_ui_rhds_renderer
```

## Usage

By installing `next_gen_ui_rhds_renderer` the agent automatically discovers the renderer.

To enable renderer simply configure your Next Gen UI Agent to use `rhds` as component system.
