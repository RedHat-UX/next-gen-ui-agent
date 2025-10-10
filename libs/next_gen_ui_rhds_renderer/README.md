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

## Links

* [Documentation](https://redhat-ux.github.io/next-gen-ui-agent/guide/renderer/rhds/)
* [Source Codes](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs/next_gen_ui_rhds_renderer)
* [Contributing](https://redhat-ux.github.io/next-gen-ui-agent/development/contributing/)
