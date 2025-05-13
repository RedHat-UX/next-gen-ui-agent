from next_gen_ui_agent.renderer.base_renderer import RenderStrategyBase
from next_gen_ui_agent.renderer.types import RenderContextOneCard
from next_gen_ui_agent.types import UIComponentMetadata


class OneCardRenderStrategy(RenderStrategyBase[RenderContextOneCard]):
    COMPONENT_NAME = "one-card"

    def __init__(self):
        self._rendering_context = RenderContextOneCard.model_construct()

    def main_processing(self, component: UIComponentMetadata):
        # Trying to find field that would contain an image link
        image, field = self.find_image(component)
        if image:
            self._rendering_context.image = image
        if field:
            self._rendering_context.fields.remove(field)
