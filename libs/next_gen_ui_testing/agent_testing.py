from next_gen_ui_agent.renderer.base_renderer import PLUGGABLE_RENDERERS_NAMESPACE
from next_gen_ui_rhds_renderer import RhdsStrategyFactory
from stevedore.extension import Extension, ExtensionManager


def extension_manager_rhds():
    """Returns extension manager with registered RhdsStrategyFactory"""
    extension = Extension(
        name="rhds", entry_point=None, plugin=None, obj=RhdsStrategyFactory()
    )
    em = ExtensionManager(PLUGGABLE_RENDERERS_NAMESPACE).make_test_instance(
        extensions=[extension], namespace=PLUGGABLE_RENDERERS_NAMESPACE
    )
    return em
