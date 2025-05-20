import logging

from next_gen_ui_agent.data_transform.types import ComponentDataBase
from next_gen_ui_agent.renderer.base_renderer import RendererContext, StrategyFactory
from next_gen_ui_agent.types import Rendition

logger = logging.getLogger(__name__)


def design_system_handler(
    components: list[ComponentDataBase],
    factory: StrategyFactory,
) -> list[Rendition]:
    outputs = []
    for component in components:
        logger.debug(
            "\n\n---design_system_handler processing component id: %s with %s renderer",
            component.id,
            factory.__class__.__name__,
        )
        output = "There was an internal issue while rendering.\n"
        try:
            renderer = RendererContext(factory.get_render_strategy(component))
            output = renderer.render(component)
        except ValueError as e:
            logger.exception("Component selection used non-supported component name")
            raise e
        except Exception as e:
            logger.exception("There was an issue while rendering component template")
            raise e

        logger.info("%s=%s", component.id, output)
        outputs.append(
            Rendition(
                id=component.id,
                content=output,
                component_system=factory.get_component_system_name(),
                mime_type=factory.get_output_mime_type(),
            )
        )
    return outputs
