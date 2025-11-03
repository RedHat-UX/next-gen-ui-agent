from typing import cast

from next_gen_ui_agent.data_transform.types import ComponentDataOneCard
from next_gen_ui_agent.data_transformation import generate_component_data
from next_gen_ui_agent.types import InputData, UIComponentMetadata


def test_generate_component_data() -> None:
    input_data = InputData(
        id="123",
        data="""{"name": "John Doe"}""",
    )
    component = UIComponentMetadata.model_validate(
        {
            "id": "123",
            "title": "John Doe",
            "component": "one-card",
            "fields": [
                {"name": "Name", "data_path": "name"},
            ],
        }
    )
    component_data = cast(
        ComponentDataOneCard, generate_component_data(input_data, component)
    )
    assert component_data.title == "John Doe"
    assert component_data.id == "123"
    assert component_data.component == "one-card"
    assert component_data.fields[0].name == "Name"
    assert component_data.fields[0].data == ["John Doe"]
