import logging

from next_gen_ui_agent.renderer.base_renderer import RenderStrategyBase
from next_gen_ui_agent.renderer.types import RenderContextImage
from next_gen_ui_agent.types import UIComponentMetadata

logger = logging.getLogger(__name__)


class ImageRenderStrategy(RenderStrategyBase[RenderContextImage]):
    COMPONENT_NAME = "image"

    def __init__(self):
        self._rendering_context = RenderContextImage.model_construct()

    def main_processing(self, component: UIComponentMetadata):
        # Trying to find field that would contain an image link
        image, _f = self.find_image(component)
        # If the image like URL is present, then set it, otherwise leave it blank
        if image:
            self._rendering_context.image = str(image)
        else:
            logger.warning("No image found in Image Component")
