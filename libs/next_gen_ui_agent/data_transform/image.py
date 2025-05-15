import logging
from typing import Any

from next_gen_ui_agent.data_transform.data_transformer import DataTransformerBase
from next_gen_ui_agent.data_transform.types import ComponentDataImage
from next_gen_ui_agent.types import UIComponentMetadata

logger = logging.getLogger(__name__)


class ImageDataTransformer(DataTransformerBase[ComponentDataImage]):
    COMPONENT_NAME = "image"

    def __init__(self):
        self._component_data = ComponentDataImage.model_construct()

    def main_processing(self, component: UIComponentMetadata, data: Any):
        # Trying to find field that would contain an image link
        image, _f = self.find_image(component)
        # If the image like URL is present, then set it, otherwise leave it blank
        if image:
            self._component_data.image = str(image)
        else:
            logger.warning("No image found in Image Component")
