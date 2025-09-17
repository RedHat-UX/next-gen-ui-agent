# Next Gen UI Patternfly Renderer

This module is part of the [Next Gen UI Agent project](https://github.com/RedHat-UX/next-gen-ui-agent).

[![Module Category](https://img.shields.io/badge/Module%20Category-UI%20Renderer-darkgreen)](https://github.com/RedHat-UX/next-gen-ui-agent)
[![Module Status](https://img.shields.io/badge/Module%20Status-Deprecated-lightgray)](https://github.com/RedHat-UX/next-gen-ui-agent)

This Python package provides a Server-Side renderer for Next Gen UI Agent that produces Patternfly JavaScript components code as an output.

Next Gen UI Agent utilises [Stevedore Plugin framework](https://docs.openstack.org/stevedore/latest/index.html) which automates to a high degree how you can configure this plugin to work in your deployment.

## Usage

1. Add `next_gen_ui_patternfly_renderer` to your project dependencies
2. Configure your Next Gen UI Agent to use `patternfly` as component system