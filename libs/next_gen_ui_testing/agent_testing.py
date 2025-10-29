from next_gen_ui_agent.renderer.base_renderer import (
    PLUGGABLE_RENDERERS_NAMESPACE,
    StrategyFactory,
)
from stevedore.extension import Extension, ExtensionManager


def extension_manager_for_testing(name: str, obj: StrategyFactory):
    """Returns extension manager with registered StrategyFactory

    Args:
        name: The name for the Extension.
        obj: The StrategyFactory instance to use.

    Returns:
        ExtensionManager with the registered extension.

    Raises:
        ValueError: If name is not provided or is empty.
    """
    if not name:
        raise ValueError("name parameter must be provided and cannot be empty")

    extension = Extension(name=name, entry_point=None, plugin=None, obj=obj)
    em = ExtensionManager(PLUGGABLE_RENDERERS_NAMESPACE).make_test_instance(
        extensions=[extension], namespace=PLUGGABLE_RENDERERS_NAMESPACE
    )
    return em
