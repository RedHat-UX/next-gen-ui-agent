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
    def main_processing(self, data: Any, component: UIComponentMetadata):
        fields = self._component_data.fields
        data_transformer_utils.fill_fields_with_array_data(fields, data)
