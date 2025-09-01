from next_gen_ui_agent.data_transform.types import ComponentDataHandBuildComponent
from next_gen_ui_agent.renderer.hand_build_component import (
    HandBuildComponentRenderStrategy,
)


def test_process() -> None:
    c = ComponentDataHandBuildComponent.model_validate(
        {
            "id": "test_id_1",
            "component": "hand-build-component",
            "component_type": "one-card-special",
            "data": {
                "movies": [
                    {"title": "Toy Story", "authors": ["A1", "A2"]},
                    {"title": "Toy Story 2", "authors": ["A3"]},
                ]
            },
        }
    )
    result = HandBuildComponentRenderStrategy().render(c)
    assert result == c.model_dump_json()
