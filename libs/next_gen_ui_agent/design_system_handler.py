import logging

from .base_renderer import RendererContext, StrategyFactory
from .types import UIComponentMetadata

logger = logging.getLogger(__name__)


def design_system_handler(
    components: list[UIComponentMetadata],
    factory: StrategyFactory,
) -> list[UIComponentMetadata]:
    for component in components:
        logger.debug(
            "\n\n---design_system_handler processing component id: %s with %s renderer",
            component["id"],
            factory.__class__.__name__,
        )
        output = "There was an internal issue while rendering.\n"
        try:
            renderer = RendererContext(factory.get_render_strategy(component))
            output = renderer.render(component)
        except ValueError as e:
            logger.exception(
                "Component selection used non-supported component name\n", e
            )
        except Exception as e:
            logger.exception(
                "There was an issue while rendering component template\n", e
            )

        logger.info("%s=%s", component["id"], output)
        component["rendition"] = output
    return components
