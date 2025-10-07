import json
import logging
import os
from typing import Any

from next_gen_ui_agent.data_transform.json_schema_config import CustomGenerateJsonSchema
from next_gen_ui_agent.types import AgentConfig

logger = logging.getLogger(__name__)


def test_schema() -> None:
    schema = AgentConfig.model_json_schema(schema_generator=CustomGenerateJsonSchema)
    assert schema is not None


def schema_file_path() -> str:
    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "./config",
            "agent_config.schema.json",
        )
    )


def save_schema(schema: dict[str, Any]) -> None:
    file_path = schema_file_path()
    with open(file_path, "w") as file:
        logger.info("Saving schema for configuration to %s", file_path)
        file.write(json.dumps(schema, indent=2))


def regenerate_schemas() -> None:
    """Regnerate schema store in /spec/config directory"""

    save_schema(
        AgentConfig.model_json_schema(schema_generator=CustomGenerateJsonSchema),
    )


# Run this file to regenerate all schemas
if __name__ == "__main__":
    logging.basicConfig()
    logger.setLevel(logging.INFO)
    regenerate_schemas()
