import json
import logging
import os
from typing import Any

from next_gen_ui_agent.data_transform.image import ImageDataTransformer
from next_gen_ui_agent.data_transform.one_card import OneCardDataTransformer
from next_gen_ui_agent.data_transform.types import (
    ComponentDataImage,
    ComponentDataOneCard,
    CustomGenerateJsonSchema,
)

logger = logging.getLogger(__name__)


def test_schema_no_title() -> None:
    schema = ComponentDataOneCard.model_json_schema(
        schema_generator=CustomGenerateJsonSchema
    )
    schema_str = json.dumps(schema, indent=2)
    assert '"title": "Title"' not in schema_str


def test_one_card_schema() -> None:
    schema = ComponentDataOneCard.model_json_schema(
        schema_generator=CustomGenerateJsonSchema
    )
    with open(schema_file_path(OneCardDataTransformer.COMPONENT_NAME), "r") as file:
        file_content = file.read()
    assert '"title": "Title"' not in file_content
    assert json.dumps(schema, indent=2) == file_content


def test_image_schema() -> None:
    schema = ComponentDataImage.model_json_schema(
        schema_generator=CustomGenerateJsonSchema
    )
    with open(schema_file_path(ImageDataTransformer.COMPONENT_NAME), "r") as file:
        file_content = file.read()
    assert '"title": "Title"' not in file_content
    assert json.dumps(schema, indent=2) == file_content


def schema_file_path(component_name) -> str:
    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "./component",
            f"{component_name}.schema.json",
        )
    )


def save_schema(component_name: str, schema: dict[str, Any]) -> None:
    file_path = schema_file_path(component_name)
    with open(file_path, "w") as file:
        logger.info("Saving schema for component '%s' to %s", component_name, file_path)
        file.write(json.dumps(schema, indent=2))


def regenerate_schemas() -> None:
    """Regnerate schema store in /spec/component directory"""

    save_schema(
        OneCardDataTransformer.COMPONENT_NAME,
        ComponentDataOneCard.model_json_schema(
            schema_generator=CustomGenerateJsonSchema
        ),
    )
    save_schema(
        ImageDataTransformer.COMPONENT_NAME,
        ComponentDataImage.model_json_schema(schema_generator=CustomGenerateJsonSchema),
    )


if __name__ == "__main__":
    logging.basicConfig()
    logger.setLevel(logging.INFO)
    regenerate_schemas()
