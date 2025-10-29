# Next Gen UI Red Hat Design System Renderer

This module is part of the [Next Gen UI Agent project](https://github.com/RedHat-UX/next-gen-ui-agent).

[![Module Category](https://img.shields.io/badge/Module%20Category-UI%20Renderer-darkgreen)](https://github.com/RedHat-UX/next-gen-ui-agent)
[![Module Status](https://img.shields.io/badge/Module%20Status-Supported-green)](https://github.com/RedHat-UX/next-gen-ui-agent)

This Python package provides a Server-Side renderer for Next Gen UI Agent that produces [Red Hat Design System Web Components](https://ux.redhat.com/) as an output. Renderer id for configuration in UI Agent is `rhds`.

Next Gen UI Agent utilises [Stevedore Plugin framework](https://docs.openstack.org/stevedore/latest/index.html) which automates to a high degree how you can configure this plugin to work in your deployment.

## Provides

* Rendering of [Dynamic Componet](https://redhat-ux.github.io/next-gen-ui-agent/guide/data_ui_blocks/dynamic_components/) html using RHDS.
    * Supported: `one-card`, `image`, `video-player`
    * Tech-Preview: `set-of-cards`, `table`
* `video-player` uses [`Video embed` element](https://ux.redhat.com/elements/video-embed/), which supports YouTube video url's only

## Installation

```sh
pip install -U next_gen_ui_rhds_renderer
```

## Usage

By installing `next_gen_ui_rhds_renderer` the agent automatically discovers the renderer.

To enable renderer simply configure your Next Gen UI Agent to use `rhds` as component system.

## Extending the RHDS renderer to support hand build components

In this section we'll explain how to add support for rendering [hand build components](https://redhat-ux.github.io/next-gen-ui-agent/guide/data_ui_blocks/hand_build_components/) aka HBC to the RHDS server-side renderer.

The process is as simple as creating a new renderer package by following steps which are documented [here](https://redhat-ux.github.io/next-gen-ui-agent/guide/renderer/implementing_serverside/#a-step-by-step-guide-to-create-a-renderer-plugin) with one simplification of the process. In step 5, rather than implementing your own StrategyFactory from scratch, we suggest just extending the RhdsStrategyFactory and overriding two functions that will add the HBC support. Below you can see an example code how your code could look like. The benefit of going this route is that all the standard strategies for dynamically chosen components and Jinja templates remain as they are.

```py
from next_gen_ui_agent.data_transform.types import ComponentDataBase
from next_gen_ui_rhds_renderer.rhds_renderer import (
    RhdsStrategyBase,
    RhdsStrategyFactory,
)

class HbcExampleRhdsStrategyFactory(RhdsStrategyFactory):
    """Example extension of RhdsStrategyFactory demonstrating how to add custom hand build components handling."""

    # Example hardcoded array of custom HBC (Human Build Components) supported components
    CUSTOM_HBC_COMPONENTS = [
        "hbc-example-component",
        "DUMMY_COMPONENT_TYPE",  # This is purely for shareable tests to work
    ]

    def get_component_system_name(self) -> str:
        """Override to return custom renderer name."""
        return "hbc-example-rhds"

    def default_render_strategy_handler(self, component: ComponentDataBase):
        """Override to provide example of checking against custom HBC components."""
        # Check if the component type matches any custom HBC components
        if component.component in self.CUSTOM_HBC_COMPONENTS:
            # Return a basic strategy for custom HBC components which assumes that the component name is the same as the template name.
            return HbcExampleRhdsStrategy()

        # If no custom HBC component matches, throw ValueError as in default implementation
        raise ValueError(
            f"This component: {component.component} is not supported by Red Hat Design System rendering plugin."
        )


class HbcExampleRhdsStrategy(RhdsStrategyBase):
    """
    Example strategy for HBC components that loads templates from the next_gen_ui_rhds_hbc_example_renderer module.
    In case you need to load templates from a different module or folder you can override the __init__ method.
    Usage:
        class MyStrategy(HbcExampleRhdsStrategyBase):
            def __init__(self):
                super().__init__("my_templates")
    """
    pass

```

## Links

* [Documentation](https://redhat-ux.github.io/next-gen-ui-agent/guide/renderer/rhds/)
* [Source Codes](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs/next_gen_ui_rhds_renderer)
* [Contributing](https://redhat-ux.github.io/next-gen-ui-agent/development/contributing/)
