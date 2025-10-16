import json
import logging
import os
from typing import Any

import pytest
from next_gen_ui_agent.data_transform.json_schema_config import CustomGenerateJsonSchema
from next_gen_ui_agent.types import MCPGenerateUIInput, MCPGenerateUIOutput
from pydantic import BaseModel

logger = logging.getLogger(__name__)


mcp_subdir = "mcp"
mcp_schemas: list[tuple[str, str, type[BaseModel]]] = [
    (mcp_subdir, "generate_ui_input.schema.json", MCPGenerateUIInput),
    (mcp_subdir, "generate_ui_output.schema.json", MCPGenerateUIOutput),
]


@pytest.mark.parametrize("dir,filename,schema_model", mcp_schemas)
def test_schema(dir: str, filename: str, schema_model: BaseModel) -> None:
    schema = schema_model.model_json_schema(schema_generator=CustomGenerateJsonSchema)
    with open(schema_file_path(dir, filename)) as file:
        file_content = file.read()
    assert json.dumps(schema, indent=2) == file_content


def schema_file_path(spec_subdir: str, filename: str) -> str:
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), spec_subdir, filename)
    )


def save_schema(dir: str, filename: str, schema: dict[str, Any]) -> None:
    file_path = schema_file_path(dir, filename)
    with open(file_path, "w") as file:
        logger.info("Saving schema for mcp output to %s", file_path)
        file.write(json.dumps(schema, indent=2))


def regenerate_schemas() -> None:
    """Regnerate schema store in /spec/mcp directory"""

    for sub_dir, filename, schema_model in mcp_schemas:
        save_schema(
            sub_dir,
            filename,
            schema_model.model_json_schema(schema_generator=CustomGenerateJsonSchema),
        )


# Run this file to regenerate all schemas
if __name__ == "__main__":
    logging.basicConfig()
    logger.setLevel(logging.INFO)
    regenerate_schemas()
