import json
from typing import Any

import pytest
from next_gen_ui_agent.data_transform.data_transformer import DataTransformerBase
from next_gen_ui_agent.data_transform.types import ComponentDataBase
from next_gen_ui_agent.types import InputData, UIComponentMetadata


class TestDataTransformer(DataTransformerBase):
    json_data: Any = None

    def __init__(self):
        self._component_data = ComponentDataBase.model_construct()

    def main_processing(self, json_data: Any, component: UIComponentMetadata) -> None:
        self.json_data = json_data


def test_process_no_data_in_input() -> None:
    data_transformer = TestDataTransformer()
    component = UIComponentMetadata.model_validate(
        {
            "id": "test_id_1",
            "title": "Toy Story Details",
            "component": "one-card",
            "fields": [],
            "json_data": {},  # even data are here, error is thrown as data in InputData is empty
        }
    )
    data = InputData(
        id="test_id_1",
        data="",
    )

    with pytest.raises(
        ValueError, match="No data content found for the component test_id_1"
    ):
        data_transformer.process(component, data)


def test_process_no_data_in_component() -> None:
    data_transformer = TestDataTransformer()
    component = UIComponentMetadata.model_validate(
        {
            "id": "test_id_1",
            "title": "Toy Story Details",
            "component": "one-card",
            "fields": [],
        }
    )
    data_str = '{"movie": {"title": "Toy Story"}}'
    data = InputData(
        id="test_id_1",
        data=data_str,
    )

    data_transformer.process(component, data)

    assert data_transformer.json_data == json.loads(data_str)


def test_process_data_in_component() -> None:
    data_transformer = TestDataTransformer()
    data_str = '{"movie": {"title": "Toy Story"}}'
    component = UIComponentMetadata.model_validate(
        {
            "id": "test_id_1",
            "title": "Toy Story Details",
            "component": "one-card",
            "fields": [],
            "json_data": json.loads(data_str),
            "input_data_type": "test_input_data_type",
        }
    )

    data = InputData(
        id="test_id_1",
        data="{}",  # put empty data here to test that component.json_data is really used with preference over InputData.data
    )

    data_transformer.process(component, data)

    assert data_transformer.json_data == json.loads(data_str)
    assert data_transformer._component_data.input_data_type == "test_input_data_type"
