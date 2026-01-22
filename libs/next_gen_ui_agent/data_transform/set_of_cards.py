from typing import Any

from next_gen_ui_agent.data_transform import data_transformer_utils
from next_gen_ui_agent.data_transform.data_transformer import DataTransformerBase
from next_gen_ui_agent.data_transform.types import ComponentDataSetOfCards
from next_gen_ui_agent.types import UIComponentMetadata
from typing_extensions import override


class SetOfCardsDataTransformer(DataTransformerBase[ComponentDataSetOfCards]):
    COMPONENT_NAME = "set-of-cards"

    def __init__(self):
        self._component_data = ComponentDataSetOfCards.model_construct()

    @override
    def main_processing(self, data: Any, component: UIComponentMetadata):
        fields = self._component_data.fields
        data_transformer_utils.fill_fields_with_array_data(fields, data)

        image_field_idx, images = data_transformer_utils.find_image_array_field(fields)
        if image_field_idx is not None and images is not None:
            if any(img is not None for img in images):
                self._component_data.images = images
                fields.pop(image_field_idx)
