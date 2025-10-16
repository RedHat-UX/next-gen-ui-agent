import logging

from next_gen_ui_agent.data_transform.json_schema_config import CustomGenerateJsonSchema
from next_gen_ui_agent.spec_schema import save_schema
from next_gen_ui_mcp.types import MCPGenerateUIInput, MCPGenerateUIOutput
from pydantic import BaseModel

mcp_subdir = "mcp"
mcp_schemas: list[tuple[str, str, type[BaseModel]]] = [
    (mcp_subdir, "generate_ui_input.schema.json", MCPGenerateUIInput),
    (mcp_subdir, "generate_ui_output.schema.json", MCPGenerateUIOutput),
]


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
    logging.getLogger().setLevel(logging.INFO)
    regenerate_schemas()
