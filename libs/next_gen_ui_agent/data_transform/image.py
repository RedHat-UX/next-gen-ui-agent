import logging
from typing import Any

from next_gen_ui_agent.data_transform import data_transformer_utils
from next_gen_ui_agent.data_transform.data_transformer import DataTransformerBase
from next_gen_ui_agent.data_transform.types import (
    ComponentDataImage,
    DataFieldSimpleValue,
)
from next_gen_ui_agent.data_transform.validation.assertions import is_url_http
from next_gen_ui_agent.data_transform.validation.types import (
    ComponentDataValidationError,
)
from next_gen_ui_agent.types import InputData, UIComponentMetadata
from typing_extensions import override

logger = logging.getLogger(__name__)


class ImageDataTransformer(DataTransformerBase[ComponentDataImage]):
    COMPONENT_NAME = "image"

    def __init__(self):
        self._component_data = ComponentDataImage.model_construct()

    @override
    def main_processing(self, json_data: Any, component: UIComponentMetadata):
        fields: list[
            DataFieldSimpleValue
        ] = data_transformer_utils.copy_simple_fields_from_ui_component_metadata(
            component.fields
        )
        data_transformer_utils.fill_fields_with_simple_data(fields, json_data)

        # Trying to find field that would contain an image link
        image, _f = data_transformer_utils.find_image(fields)
        # If the image like URL is present, then set it, otherwise leave it blank
        if image:
            self._component_data.image = image
        else:
            logger.warning("No image found in Image Component")

    @override
    def validate(
        self,
        component: UIComponentMetadata,
        data: InputData,
        errors: list[ComponentDataValidationError],
    ) -> ComponentDataImage:
        ret = super().validate(component, data, errors)

        imageUrl = self._component_data.image

        if imageUrl:
            if not is_url_http(imageUrl):
                errors.append(
                    ComponentDataValidationError(
                        "image.invalidUrl", f"Image URL '{imageUrl}' is not a valid URL"
                    )
                )
        else:
            errors.append(
                ComponentDataValidationError("image.missing", "Image URL is missing")
            )
        return ret
