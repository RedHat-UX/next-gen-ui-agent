import json
import logging
from abc import ABC
from typing import Any, Generic, TypeVar

from next_gen_ui_agent.data_transform.data_transformer_utils import (
    copy_array_fields_from_ui_component_metadata,
    copy_simple_fields_from_ui_component_metadata,
    sanitize_data_path,
)
from next_gen_ui_agent.data_transform.types import (
    ComponentDataAudio,
    ComponentDataBase,
    ComponentDataBaseWithArrayValueFileds,
    ComponentDataBaseWithSimpleValueFileds,
    ComponentDataBaseWithTitle,
    ComponentDataHandBuildComponent,
    ComponentDataImage,
    ComponentDataOneCard,
    ComponentDataSetOfCards,
    ComponentDataTable,
    ComponentDataVideo,
)
from next_gen_ui_agent.data_transform.validation.types import (
    ComponentDataValidationError,
)
from next_gen_ui_agent.types import InputData, UIComponentMetadata

T = TypeVar(
    "T",
    ComponentDataBase,
    ComponentDataBaseWithTitle,
    ComponentDataAudio,
    ComponentDataImage,
    ComponentDataOneCard,
    ComponentDataSetOfCards,
    ComponentDataTable,
    ComponentDataVideo,
    ComponentDataHandBuildComponent,
)

logger = logging.getLogger(__name__)


class DataTransformerBase(ABC, Generic[T]):
    """Data transformer"""

    def __init__(self):
        self._component_data: T = None  # type: ignore

    def preprocess_rendering_context(self, component: UIComponentMetadata):
        """Prepare _component_data property for further use in the transformer"""
        self._component_data.id = component.id  # type: ignore
        if isinstance(self._component_data, ComponentDataBaseWithTitle):
            self._component_data.title = component.title
        if isinstance(self._component_data, ComponentDataBaseWithSimpleValueFileds):
            self._component_data.fields = copy_simple_fields_from_ui_component_metadata(
                component.fields
            )
        elif isinstance(self._component_data, ComponentDataBaseWithArrayValueFileds):
            self._component_data.fields = copy_array_fields_from_ui_component_metadata(
                component.fields
            )

    def main_processing(self, json_data: Any, component: UIComponentMetadata):
        """IMPLEMENT: Main processing of the _component_data from parsed JSON data, UIComponentMetadata passed here also if necessary"""
        pass

    def post_processing(self, json_data: Any, component: UIComponentMetadata):
        """IMPLEMENT: Post processing of the _component_data from parsed JSON data, UIComponentMetadata passed here also if necessary"""
        pass

    def process(self, component: UIComponentMetadata, data: InputData) -> T:
        """Transform the component metadata and data into final structure passed to the rendering, via running pre-
        main-post processing flow. You can use `data_transformer_utils` for the implementation.
        """

        data_content = data["data"]
        if not data_content:
            raise ValueError(f"No data content found for the component {data['id']}")

        json_data = json.loads(data_content)

        self.preprocess_rendering_context(component)
        self.main_processing(json_data, component)
        self.post_processing(json_data, component)
        return self._component_data

    def validate(
        self,
        component: UIComponentMetadata,
        data: InputData,
        errors: list[ComponentDataValidationError],
    ) -> T:
        """
        Validate the component configuration agains provided data. Basic implementation inits `_component_data` and then validates the data paths and data presence for `fields`.
        You can override it to perform more complex validation for components with specific type (you should always call super().validate() in your implementation).
        """

        self.process(component, data)

        if isinstance(
            self._component_data, ComponentDataBaseWithSimpleValueFileds
        ) or isinstance(self._component_data, ComponentDataBaseWithArrayValueFileds):
            # variable for check of data length used for array components only. start with minimal data len here, until we fill it with real data len from field, to make sure all fields select data of the same length
            data_len = 2
            for i, field in enumerate(self._component_data.fields):
                fn = f"fields[{i}]."
                sanitized_data_path = sanitize_data_path(field.data_path)
                if not sanitized_data_path or sanitized_data_path == "":
                    errors.append(
                        ComponentDataValidationError(
                            fn + "data_path.invalid_format",
                            f"Generated data_path='{field.data_path}' is not valid",
                        )
                    )
                elif not field.data or (
                    isinstance(
                        self._component_data, ComponentDataBaseWithArrayValueFileds
                    )
                    and (field.data == [])
                ):
                    # we cant perform full incorrect path check for `ComponentDataBaseWithSimpleValueFileds` as `[]` is valid value here for input data fields containing empty array :-(
                    errors.append(
                        ComponentDataValidationError(
                            fn + "data_path.invalid",
                            f"No value found in input data for data_path='{field.data_path}'",
                        )
                    )
                elif isinstance(
                    self._component_data, ComponentDataBaseWithArrayValueFileds
                ):
                    # check of data length used for array components only
                    if len(field.data) < data_len:
                        errors.append(
                            ComponentDataValidationError(
                                fn + "data_path.not_enough_values",
                                f"Not enough values for array component found in the input data for data_path='{field.data_path}'",
                            )
                        )
                    else:
                        data_len = len(field.data)

        return self._component_data
