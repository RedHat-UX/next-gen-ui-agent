from typing import Any

from next_gen_ui_agent.data_transform.data_transformer import DataTransformerBase
from next_gen_ui_agent.data_transform.types import (
    IMAGE_SUFFIXES,
    ComponentDataSetOfCard,
)
from next_gen_ui_agent.types import UIComponentMetadata


class SetOfCardsDataTransformer(DataTransformerBase[ComponentDataSetOfCard]):
    COMPONENT_NAME = "set-of-cards"

    def __init__(self):
        self._component_data = ComponentDataSetOfCard.model_construct()

    def main_processing(self, component: UIComponentMetadata, data: Any):
        # TODO: Use super()._find_field
        subtitle_field = next(
            (
                field
                for field in component.fields
                if field.name.lower() in ["title", "name", "header"]
            ),
            None,
        )
        if subtitle_field:
            self._component_data.subtitle_field = subtitle_field
            self._component_data.fields.remove(subtitle_field)

        image_field = next(
            (
                field
                for field in component.fields
                for d in field.data
                if type(d) is str and d.endswith(IMAGE_SUFFIXES)
            ),
            None,
        )
        if image_field:
            self._component_data.image_field = image_field
            self._component_data.fields.remove(image_field)
