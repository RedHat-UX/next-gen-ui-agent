from typing import Any

from next_gen_ui_agent.data_transform.data_transformer import DataTransformerBase
from next_gen_ui_agent.data_transform.types import ComponentDataOneCard
from next_gen_ui_agent.types import UIComponentMetadata


class OneCardDataTransformer(DataTransformerBase[ComponentDataOneCard]):
    COMPONENT_NAME = "one-card"

    def __init__(self):
        self._component_data = ComponentDataOneCard.model_construct()

    def main_processing(self, component: UIComponentMetadata, data: Any):
        # Trying to find field that would contain an image link
        image, field = self.find_image(component)
        if image:
            self._component_data.image = image
        if field:
            self._component_data.fields.remove(field)
