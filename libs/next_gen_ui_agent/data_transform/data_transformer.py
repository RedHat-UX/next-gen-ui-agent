import json
from abc import ABC
from typing import Any, Callable, Generic, TypeVar

from next_gen_ui_agent.data_transform.types import (
    IMAGE_SUFFIXES,
    ComponentDataAudio,
    ComponentDataBase,
    ComponentDataBaseWithFileds,
    ComponentDataImage,
    ComponentDataOneCard,
    ComponentDataSetOfCard,
    ComponentDataVideo,
)
from next_gen_ui_agent.types import (
    DataField,
    DataFieldDataType,
    InputData,
    UIComponentMetadata,
)

T = TypeVar(
    "T",
    ComponentDataBase,
    ComponentDataAudio,
    ComponentDataImage,
    ComponentDataOneCard,
    ComponentDataSetOfCard,
    ComponentDataVideo,
)


class DataTransformerBase(ABC, Generic[T]):
    """Data transformer"""

    def __init__(self):
        self._component_data: T = None

    def preprocess_rendering_context(self, component: UIComponentMetadata):
        """Prepare ComponentData property for further use"""
        fields = component.fields
        self._component_data.title = component.title
        self._component_data.id = component.id  # type: ignore
        if isinstance(self._component_data, ComponentDataBaseWithFileds):
            self._component_data.fields = fields.copy()

    def main_processing(self, component: UIComponentMetadata, data: Any):
        """Main processing of the component data from UIComponentMetadata and JSON parsed data"""
        pass

    def post_processing(self, component: UIComponentMetadata, data: Any):
        """Post processing of the component data from UIComponentMetadata and JSON parsed data"""
        pass

    def process(self, component: UIComponentMetadata, data: InputData) -> T:
        """Transform the component metadata and data into final structure passed to the rendering, via running pre-
        main-post processing flow."""

        # TODO some system error should be thrown if no data are found for the component["id"]
        data_content = data["data"]
        # TODO: Investigate why is problem with \n in content
        json_data = json.loads(data_content.replace("\n", ""))

        self.preprocess_rendering_context(component)
        self.main_processing(component, json_data)
        self.post_processing(component, json_data)
        return self._component_data

    @staticmethod
    def find_field_by_data_value(
        fields: list[DataField],
        field_data_predicate: Callable[[DataFieldDataType], bool],
    ) -> DataField | None:
        """Helper methods for to find field based on predicate."""
        return next(
            (field for field in fields for d in field.data if field_data_predicate(d)),
            None,
        )

    @staticmethod
    def find_field_by_data_path(
        fields: list[DataField],
        data_path_predicate: Callable[[str], bool],
    ) -> DataField | None:
        """Helper methods for to find field based on its data_path predicate. Predicate's argument is lowered field `data_path`"""
        return next(
            (
                field
                for field in fields
                if field.data_path and data_path_predicate(field.data_path.lower())
            ),
            None,
        )

    @staticmethod
    def find_data_value_in_field(
        items: list[DataFieldDataType],
        data_value_predicate: Callable[[DataFieldDataType], bool],
    ) -> DataFieldDataType | None:
        """Helper methods for to find field data value based on predicate."""
        return next(
            (value for value in items if data_value_predicate(value)),
            None,
        )

    @staticmethod
    def find_image(
        component: UIComponentMetadata,
    ) -> tuple[str, DataField] | tuple[None, None]:
        """Find image field with image. Return tuple with data value and DataField"""
        fields = component.fields
        field_with_image_suffix = DataTransformerBase.find_field_by_data_value(
            fields,
            lambda data: isinstance(data, str) and data.endswith(IMAGE_SUFFIXES),
        )
        if field_with_image_suffix:
            image = DataTransformerBase.find_data_value_in_field(
                field_with_image_suffix.data,
                lambda value: isinstance(value, str) and value.endswith(IMAGE_SUFFIXES),
            )
            if image:
                return str(image), field_with_image_suffix
        else:
            field_name_like_url = DataTransformerBase.find_field_by_data_path(
                fields,
                lambda name: name.endswith("link") or name.endswith("url"),
            )
            if field_name_like_url and len(field_name_like_url.data) > 0:
                return str(field_name_like_url.data[0]), field_name_like_url

        return None, None
