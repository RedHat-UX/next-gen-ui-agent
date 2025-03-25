# Next Gen UI Red Hat Design System Plugin

This Python package provides a plugin which will enable a renderer for Next Gen UI Agent that produces Red Hat Design System Web Components as an output.

Next Gen UI Agent utilises [Stevedore Plugin framework](https://docs.openstack.org/stevedore/latest/index.html) which automates to a high degree how you can configure this plugin to work in your deployment.

## Usage

1. Add next_gen_ui_rhds_renderer to your project dependencies
2. Configure your Next Gen UI Agent to use `rhds` as component system