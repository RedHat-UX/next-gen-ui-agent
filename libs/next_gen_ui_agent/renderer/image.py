from next_gen_ui_agent.renderer.base_renderer import IMAGE_SUFFIXES, RenderStrategyBase
from next_gen_ui_agent.renderer.types import RenderContextImage
from next_gen_ui_agent.types import UIComponentMetadata


class ImageRenderStrategy(RenderStrategyBase[RenderContextImage]):
    COMPONENT_NAME = "image"

    def main_processing(self, component: UIComponentMetadata):
        # Trying to find field that would contain an image link
        fields = component["fields"]

        field_with_image_suffix = next(
            (
                field
                for field in fields
                for d in field["data"]
                if type(d) is str and d.endswith(IMAGE_SUFFIXES)
            ),
            None,
        )
        if field_with_image_suffix:
            image = next(
                (
                    data
                    for data in field_with_image_suffix["data"]
                    if type(data) is str and data.endswith(IMAGE_SUFFIXES)
                ),
                None,
            )
            if image:
                self._rendering_context["image"] = image
                self._rendering_context["fields"].remove(field_with_image_suffix)
