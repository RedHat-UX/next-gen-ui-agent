from next_gen_ui_agent.renderer.base_renderer import IMAGE_SUFFIXES, RenderStrategyBase
from next_gen_ui_agent.renderer.types import RenderContextOneCard
from next_gen_ui_agent.types import UIComponentMetadata


class OneCardRenderStrategy(RenderStrategyBase[RenderContextOneCard]):
    COMPONENT_NAME = "one-card"

    def __init__(self):
        self._rendering_context = RenderContextOneCard.model_construct()

    def main_processing(self, component: UIComponentMetadata):
        # Trying to find field that would contain an image link
        fields = component.fields

        field_with_image_suffix = RenderStrategyBase.find_field(
            fields,
            lambda data: isinstance(data, str) and data.endswith(IMAGE_SUFFIXES),
        )
        if field_with_image_suffix:
            image = RenderStrategyBase.find_field_data_value(
                field_with_image_suffix.data,
                lambda data: isinstance(data, str) and data.endswith(IMAGE_SUFFIXES),
            )
            if image:
                self._rendering_context.image = str(image)
                self._rendering_context.fields.remove(field_with_image_suffix)
