import logging

from next_gen_ui_a2a.agent_config import A2AAgentConfig
from next_gen_ui_agent.data_transform.json_schema_config import CustomGenerateJsonSchema
from next_gen_ui_agent.spec_schema import save_schema
from pydantic import BaseModel

a2a_subdir = "a2a"
a2a_schemas: list[tuple[str, str, type[BaseModel]]] = [
    (a2a_subdir, "a2a_agent_config.schema.json", A2AAgentConfig),
]


def regenerate_schemas() -> None:
    """Regnerate schema store in /spec/a2a directory"""

    for sub_dir, filename, schema_model in a2a_schemas:
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
