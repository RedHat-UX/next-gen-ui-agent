import logging

from .base_renderer import RendererContext, StrategyFactory
from .types import UIComponentMetadata


def design_system_handler(
    components: list[UIComponentMetadata],
    factory: StrategyFactory,
) -> list[UIComponentMetadata]:
    for component in components:
        logging.debug(
            f"\n\n---design_system_handler processing component id: {component['id']} with {factory.__class__.__name__} renderer"
        )
        output = "There was an internal issue while rendering.\n"
        try:
            renderer = RendererContext(factory.get_render_strategy(component))
            output = renderer.render(component)
        except ValueError as e:
            logging.error("Component selection used non-supported component name\n", e)
        except Exception as e:
            logging.error("There was an issue while rendering component template\n", e)

        logging.info(f"{component['id']}={output}")
        component["rendition"] = output
    return components
