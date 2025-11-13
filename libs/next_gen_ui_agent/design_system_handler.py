import logging

from next_gen_ui_agent.data_transform.types import ComponentDataBase
from next_gen_ui_agent.renderer.base_renderer import RendererContext, StrategyFactory
from next_gen_ui_agent.types import UIBlockRendering

logger = logging.getLogger(__name__)


def render_component(
    component: ComponentDataBase,
    factory: StrategyFactory,
) -> UIBlockRendering:
    """Render the component with the given UI renderer factory."""
    logger.debug(
        "\n\n---design_system_handler processing component id: %s with %s renderer",
        component.id,
        factory.__class__.__name__,
    )

    try:
        renderer = RendererContext(factory.get_render_strategy(component))
        output = renderer.render(component)
        logger.info("Rendered component %s as %s", component.id, output)
        return UIBlockRendering(
            id=component.id,
            content=output,
            component_system=factory.get_component_system_name(),
            mime_type=factory.get_output_mime_type(),
        )
    except ValueError as e:
        logger.exception("Component selection used non-supported component name")
        raise e
    except Exception as e:
        logger.exception("There was an issue while rendering component template")
        raise e
