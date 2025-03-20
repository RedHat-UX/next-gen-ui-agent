from .base_renderer import RendererContext, JsonStrategyFactory, StrategyFactory
from .types import UIComponentMetadata
import pprint

### Nodes
def design_system_handler(components: list[UIComponentMetadata], component_system: str = None) -> list[UIComponentMetadata]:

    # WORK IN PROGRESS CODE

    # setuptools.setup(name="next_gen_ui_rhds_renderer",
    #     version="0.0.1",
    #     description="Next Gen UI Red Hat Design System Renderer",
    #     entry_points={
    #         'next_gen_ui.agent.renderer_factory': [
    #             'rhds = next_gen_ui_rhds_renderer.rhds_renderer:RhdsStrategyFactory'
    #         ],
    #     })
    # driver.NamedExtensionManager.make_test_instance()
    # driver.DriverManager.make_test_instance()
    # renderer_strategy_factory = driver.DriverManager(
    #     namespace = 'next_gen_ui.agent.renderer_factory',
    #     name = component_system,
    #     invoke_on_load = False) if component_system else JsonStrategyFactory()

    # Hardocded JSON factory till we make plugins work
    renderer_strategy_factory = JsonStrategyFactory()
    
    for component in components:
        print(f"\n\n---CALL {component_system}--- id: {component['id']}")
        output = "There was an internal issue while rendering.\n"
        try:
            renderer = RendererContext(renderer_strategy_factory.get_render_strategy(component))
            output = renderer.render(component)
        except ValueError as e:
            print("Component selection used non-supported component name\n", e)
        except Exception as e:
            print("There was an issue while rendering component template\n", e)

        pprint.pp(f"{component['id']}={output}")
        component["rendition"] = output
        print(f"Generated component: {output}")
    return components