from next_gen_ui_agent.data_transform.types import ComponentDataBase

from .rhds_renderer import RhdsStrategyBase, RhdsStrategyFactory


class CustomRhdsStrategyFactory(RhdsStrategyFactory):
    """Example extension of RhdsStrategyFactory demonstrating how to add custom hand build components handling."""

    def get_component_system_name(self) -> str:
        """Override to return custom system name."""
        return "custom-rhds"

    def default_render_strategy_handler(self, component: ComponentDataBase):
        """Override to provide example of checking against imaginary components."""
        # Example hardcoded array of imaginary supported components
        imaginary_components = [
            "magic-widget",
            "super-chart",
            "awesome-form",
            "fantastic-dashboard",
            "incredible-card",
        ]

        # Check if the component type matches any imaginary components
        if component.component in imaginary_components:
            # Return a basic strategy for imaginary components
            # In a real implementation, you might have specific templates or logic
            return RhdsStrategyBase()

        # If no imaginary component matches, throw ValueError as in default implementation
        raise ValueError(
            f"This component: {component.component} is not supported by Red Hat Design System rendering plugin."
        )
