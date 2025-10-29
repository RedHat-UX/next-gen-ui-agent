from next_gen_ui_agent.data_transform.types import ComponentDataBase
from next_gen_ui_rhds_renderer.rhds_renderer import (
    RhdsStrategyBase,
    RhdsStrategyFactory,
)


class HbcExampleRhdsStrategyFactory(RhdsStrategyFactory):
    """Example extension of RhdsStrategyFactory demonstrating how to add custom hand build components handling."""

    # Example hardcoded array of custom HBC (Human Build Components) supported components
    CUSTOM_HBC_COMPONENTS = [
        "hbc-example-component",
        "DUMMY_COMPONENT_TYPE",  # This is purely for shareable tests to work
    ]

    def get_component_system_name(self) -> str:
        """Override to return custom renderer name."""
        return "hbc-example-rhds"

    def default_render_strategy_handler(self, component: ComponentDataBase):
        """Override to provide example of checking against custom HBC components."""
        # Check if the component type matches any custom HBC components
        if component.component in self.CUSTOM_HBC_COMPONENTS:
            # Return a basic strategy for custom HBC components which assumes that the component name is the same as the template name.
            return HbcExampleRhdsStrategy()

        # If no custom HBC component matches, throw ValueError as in default implementation
        raise ValueError(
            f"This component: {component.component} is not supported by Red Hat Design System rendering plugin."
        )


class HbcExampleRhdsStrategy(RhdsStrategyBase):
    """
    Example strategy for HBC components that loads templates from the next_gen_ui_rhds_hbc_example_renderer module.
    In case you need to load templates from a different folder you can override the __init__ method.
    Usage:
        class MyStrategy(HbcExampleRhdsStrategyBase):
            def __init__(self):
                super().__init__("my_templates")
    """

    pass
