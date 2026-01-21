from typing import Any

from next_gen_ui_agent.data_transform import data_transformer_utils
from next_gen_ui_agent.data_transform.data_transformer import DataTransformerBase
from next_gen_ui_agent.data_transform.types import ComponentDataTable
from next_gen_ui_agent.types import UIComponentMetadata
from typing_extensions import override


class TableDataTransformer(DataTransformerBase):
    COMPONENT_NAME = "table"

    def __init__(self):
        self._component_data = ComponentDataTable.model_construct()

    @override
    def preprocess_rendering_context(self, component: UIComponentMetadata):
        """Prepare _component_data property for further use in the transformer"""
        super().preprocess_rendering_context(component)
        # Copy on_row_click from component metadata to component data
        if component.on_row_click:
            self._component_data.on_row_click = component.on_row_click

    @override
    def main_processing(self, data: Any, component: UIComponentMetadata):
        fields = self._component_data.fields
        data_transformer_utils.fill_fields_with_array_data(fields, data)
