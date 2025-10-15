import json
import logging
import os
from typing import Any

from next_gen_ui_agent.data_transform.json_schema_config import CustomGenerateJsonSchema
from next_gen_ui_agent.types import MCPGenerateUIOutput

logger = logging.getLogger(__name__)


def test_schema_generate_ui_output() -> None:
    schema = MCPGenerateUIOutput.model_json_schema(
        schema_generator=CustomGenerateJsonSchema
    )
    with open(schema_file_path(mcp_subdir, schema_generate_output)) as file:
        file_content = file.read()
    assert json.dumps(schema, indent=2) == file_content


def schema_file_path(spec_subdir: str, filename: str) -> str:
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), spec_subdir, filename)
    )


def save_schema(schema: dict[str, Any], dir: str, filename: str) -> None:
    file_path = schema_file_path(dir, filename)
    with open(file_path, "w") as file:
        logger.info("Saving schema for mcp output to %s", file_path)
        file.write(json.dumps(schema, indent=2))


mcp_subdir = "mcp"
schema_generate_output = "generate_ui_output.schema.json"


def regenerate_schemas() -> None:
    """Regnerate schema store in /spec/mcp directory"""

    save_schema(
        MCPGenerateUIOutput.model_json_schema(
            schema_generator=CustomGenerateJsonSchema
        ),
        mcp_subdir,
        schema_generate_output,
    )


# Run this file to regenerate all schemas
if __name__ == "__main__":
    logging.basicConfig()
    logger.setLevel(logging.INFO)
    regenerate_schemas()
