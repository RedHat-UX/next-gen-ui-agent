# Implementing Server-Side UI Renderer

Server side renderers can be developed as separate python modules, and plugged into *UI Agent* backend using framework available in [UI Agent Core](../ai_apps_binding/pythonlib.md). It is based on [Stevedore Plugin framework](https://docs.openstack.org/stevedore/latest/index.html).

Thanks to Stevedore and our comprehensively implemented base classes implementing your own renderer is very simple to start with. You just extend our classes, create the package, add it to Python environment during runtime and Stevedore will pick it up as a valid renderer to use.

To get a very good understanding what it takes to implement your own renderer it is worth going through the sources of our `next_gen_ui_rhds_renderer` as it's a good example of everything that needs doing. In the next sections of this guide we'll be referencing various pieces of this package to illustrate the approach.

## A step by step guide to create a renderer plugin
Those instructions will assume you're implementing the plugin as part of our NextGenUI repository fork but it's also possible to implement it completely separate, you'll just have to align the steps with your project structure, build scripts etc.

1. Clone [NextGenUI](https://github.com/RedHat-UX/next-gen-ui-agent) repository or your fork of it.
2. Create a subdirectory in `./libs` directory that will contain source files for your renderer. By convention we tend to name our renderer packages with the pattern of `next_gen_ui_******_renderer` with an example of `next_gen_ui_rhds_renderer`. This naming convention has no technical consequence, so it's up to you whether you follow it or not.
3. Add the `__init__.py` file and `README.md` files in your newly created plugin directory.
4. Create the main entrypoint script for your renderer. It'll extend classes provided in [./libs/next_gen_ui_agent/renderer/base_renderer.py](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/libs/next_gen_ui_agent/renderer/base_renderer.py). The code follows Factory and Strategy programming patterns to ease understanding and usage of the base implementation. You can also keep following [./libs/next_gen_ui_rhds_renderer/rhds_renderer.py](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/libs/next_gen_ui_rhds_renderer/rhds_renderer.py) for reference during implementing.
   1. Extend `StrategyFactory` abstract class and implement all the required methods. The `get_render_strategy` one is the key handler of rendering. It's responsible for switching between different rendering strategies depending on the component type. On its output a class inheriting from `RenderStrategyBase` is expected.
   2. Now for every component renderable by your system you have to provide a renderer strategy. You can see details about each type of the component and metadata it supports in our [Compoments documentation](../../spec/component.md).
   Rendering strategies implementations can be shared between components or you can have some inheritance approach as you can see in RHDS Renderer. The most important part is to extend `RenderStrategyBase` and then provide instances of those classes from the factory. Please refer to code comments in `RenderStrategyBase` to understand purpose of each of methods included in this class. If you just extend the class and provide no implementation, your renderer will already work and provide the default JSON responses.
   In our system we also provide an option to support [Hand Build Components](../data_ui_blocks/hand_build_components.md) and for them to work you also have to provide custom strategy handler.
5. Create a `BUILD` file for our Pants build and monorepo management system. 
   1. The easiest will be to copy the one from [./libs/next_gen_ui_rhds_renderer/BUILD](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/libs/next_gen_ui_rhds_renderer/BUILD) to start
   2. Update standard names, dependencies etc. values in it to be aligned with your project and its needs
   3. The crucial part to make the plugin discoverable by Stevedore is `entrypoints` section:
    ```
    entry_points={
        "next_gen_ui.agent.renderer_factory": [
            "rhds = next_gen_ui_rhds_renderer:RhdsStrategyFactory"
        ],
    },
    ```
    First two lines must not be changed as our Stevedore plugin manager is configured to look for plugins in `next_gen_ui.agent.renderer_factory` namespace.
    What you need to align with your code is the 3rd line. You need to replace `rhds` with your short name which later will be used as a renderer key when invoking NextGenUI.
    Then on the right side comes reference to your package and class that extends `StrategyFactory` from [./libs/next_gen_ui_agent/renderer/base_renderer.py](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/libs/next_gen_ui_agent/renderer/base_renderer.py) which you have written in the previous step.
6. Either write tests (see next section) or create your own script to run Next Gen UI Agent with the new renderer

## Writing renderer tests
Basically renderer tests can be written as standard Python tests. You can find a lot examples in RHDS Renderer sources but also in the main agent's JSON renderer at [./libs/next_gen_ui_agent/renderer/json/*_test.py](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs/next_gen_ui_agent/renderer/json) files.

Additionally, our base renderer provides also shareable tests which give you this possibility to just extend the classes they provide and gain at least basic level of testing that the output rendered contains certain tested fields.
The root classes providing shareable tests can be found in [./libs/next_gen_ui_agent/renderer/*_shareable_tests.py](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs/next_gen_ui_agent/renderer) files. To see how easy it is to use them you can see e.g. [TestOneCardRHDSRendererWithShareableTests](https://github.com/RedHat-UX/next-gen-ui-agent/blob/536f3fe4bc451ad2d71ef21597df1ea12d7288b4/libs/next_gen_ui_rhds_renderer/rhds_renderer_one_card_test.py#L14)
```python
class TestOneCardRHDSRendererWithShareableTests(BaseOneCardRendererTests):
    """Test class for RHDS renderer using shared test cases for one-card component."""

    def get_strategy_factory(self) -> StrategyFactory:
        return RhdsStrategyFactory()
```
As a result all tests implemented in [BaseOneCardRendererTests](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/libs/next_gen_ui_agent/renderer/one_card_shareable_tests.py#L27) will be automatically executed as part of your testsuite.