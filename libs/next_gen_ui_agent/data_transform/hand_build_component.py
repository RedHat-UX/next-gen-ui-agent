from typing import Any

from next_gen_ui_agent.data_transform.data_transformer import DataTransformerBase
from next_gen_ui_agent.data_transform.types import ComponentDataHandBuildComponent
from next_gen_ui_agent.types import (
    UIComponentMetadata,
    UIComponentMetadataHandBuildComponent,
)
from typing_extensions import override


class HandBuildComponentDataTransformer(
    DataTransformerBase[ComponentDataHandBuildComponent]
):
    COMPONENT_NAME = "hand-build-component"

    def __init__(self):
        self._component_data = ComponentDataHandBuildComponent.model_construct()

    @override
    def main_processing(self, json_data: Any, component: UIComponentMetadata):
        if not isinstance(component, UIComponentMetadataHandBuildComponent):
            raise ValueError(f"Component {component.id} is not a hand-build component")

        self._component_data.data = json_data
        self._component_data.component = component.component_type
