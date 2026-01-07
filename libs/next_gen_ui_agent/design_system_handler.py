import logging

from next_gen_ui_agent.data_transform.types import ComponentDataBase
from next_gen_ui_agent.renderer.base_renderer import RendererContext, StrategyFactory
from next_gen_ui_agent.renderer.json.json_renderer import JsonStrategyFactory
from next_gen_ui_agent.types import UIBlockRendering
from stevedore import ExtensionManager

logger = logging.getLogger(__name__)

PLUGGABLE_RENDERERS_NAMESPACE = "next_gen_ui.agent.renderer_factory"

EXTENSION_MANAGER = ExtensionManager(
    namespace=PLUGGABLE_RENDERERS_NAMESPACE, invoke_on_load=True
)


def get_component_system_factory(component_system: str) -> StrategyFactory:
    """Get the factory for the given component system name."""

    if component_system == "json":
        return JsonStrategyFactory()
    elif component_system not in EXTENSION_MANAGER.names():
        raise ValueError(
            f"UI component system '{component_system}' is not found. "
            + "Make sure you install appropriate dependency."
        )
    else:
        return EXTENSION_MANAGER[component_system].obj  # type: ignore


def get_component_system_names() -> list[str]:
    """Get the list of all supported/installed component system names."""
    return ["json"] + EXTENSION_MANAGER.names()  # type: ignore


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
