# Binding into UI - UI Renderes

*UI Agent* core works with abstract representation of the [`Data UI Block`](../data_ui_blocks/index.md). 
They can be rendered using pluggable GUI component system renderers, and integrated into the GUI of the *Controlling assistant*. 

Renderer can be Server-Side, so rendering into final component system markup happens in *UI Agent* backend, and its output is eg. `html` then, which 
can be directly used in the frontend.
Server side renderes can be developed as a separate python modules, and plugged into *UI Agent* backend, see [development guide](implementing_serverside.md).

Second possibility is Client-Side rendering, where output from `UI Agent` backend is JSON conforming [defined JSON Schema](../../spec/component.md), 
and rendering itself happens on client side. How are these definitions delivered into frontend depends on the *Controlling assistant* architecture/framework.

We provide renderers for several UI component systems:

* Server-Side
    * JSON - implemented in the [UI Agent Core](../ai_apps_binding/pythonlib.md), default one, produces UI definitions conforming [defined JSON Schema](../../spec/component.md) used eg. in Client-Side renderers.
    * [RHDS](rhds.md) - produces [Red Hat Design System](https://ux.redhat.com/) Web Components html
* Client-Side
    * [PatternFly NPM](patternfly_npm.md) - produces [PatternFly](https://www.patternfly.org/) React components

