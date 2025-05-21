from typing import Any

from next_gen_ui_agent.data_transform import data_transformer_utils
from next_gen_ui_agent.data_transform.data_transformer import DataTransformerBase
from next_gen_ui_agent.data_transform.types import ComponentDataOneCard
from next_gen_ui_agent.data_transform.validation.assertions import is_url_http
from next_gen_ui_agent.data_transform.validation.types import (
    ComponentDataValidationError,
)
from next_gen_ui_agent.types import InputData, UIComponentMetadata
from typing_extensions import override


class OneCardDataTransformer(DataTransformerBase[ComponentDataOneCard]):
    COMPONENT_NAME = "one-card"

    def __init__(self):
        self._component_data = ComponentDataOneCard.model_construct()

    @override
    def main_processing(self, json_data: Any, component: UIComponentMetadata):
        fields = self._component_data.fields
        data_transformer_utils.fill_fields_with_simple_data(fields, json_data)

        # Trying to find field that would contain an image link
        image, field = data_transformer_utils.find_image(fields)
        if image:
            self._component_data.image = image
        if field:
            self._component_data.fields.remove(field)

    @override
    def validate(
        self,
        component: UIComponentMetadata,
        data: InputData,
        errors: list[ComponentDataValidationError],
    ) -> ComponentDataOneCard:
        ret = super().validate(component, data, errors)

        imageUrl = self._component_data.image

        if imageUrl:
            if not is_url_http(imageUrl):
                errors.append(
                    ComponentDataValidationError(
                        "image.invalidUrl", f"Image URL '{imageUrl}' is not a valid URL"
                    )
                )
        return ret
