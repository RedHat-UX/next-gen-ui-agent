import itertools
import json
import logging
import os
from typing import Any

from next_gen_ui_agent import AgentConfig
from next_gen_ui_agent.data_transform.hand_build_component import (
    HandBuildComponentDataTransformer,
)
from next_gen_ui_agent.data_transform.image import ImageDataTransformer
from next_gen_ui_agent.data_transform.json_schema_config import CustomGenerateJsonSchema
from next_gen_ui_agent.data_transform.one_card import OneCardDataTransformer
from next_gen_ui_agent.data_transform.set_of_cards import SetOfCardsDataTransformer
from next_gen_ui_agent.data_transform.table import TableDataTransformer
from next_gen_ui_agent.data_transform.types import (
    ComponentDataHandBuildComponent,
    ComponentDataImage,
    ComponentDataOneCard,
    ComponentDataSetOfCards,
    ComponentDataTable,
    ComponentDataVideo,
)
from next_gen_ui_agent.data_transform.video import VideoPlayerDataTransformer
from pydantic import BaseModel

logger = logging.getLogger(__name__)

config_subdir = "config"
config_schemas: list[tuple[str, str, type[BaseModel]]] = [
    (config_subdir, "agent_config.schema.json", AgentConfig),
]

component_dir = "component"
component_schemas: list[tuple[str, str, type[BaseModel]]] = [
    (
        component_dir,
        f"{OneCardDataTransformer.COMPONENT_NAME}.schema.json",
        ComponentDataOneCard,
    ),
    (
        component_dir,
        f"{SetOfCardsDataTransformer.COMPONENT_NAME}.schema.json",
        ComponentDataSetOfCards,
    ),
    (
        component_dir,
        f"{TableDataTransformer.COMPONENT_NAME}.schema.json",
        ComponentDataTable,
    ),
    (
        component_dir,
        f"{ImageDataTransformer.COMPONENT_NAME}.schema.json",
        ComponentDataImage,
    ),
    (
        component_dir,
        f"{VideoPlayerDataTransformer.COMPONENT_NAME}.schema.json",
        ComponentDataVideo,
    ),
    (
        component_dir,
        f"{HandBuildComponentDataTransformer.COMPONENT_NAME}.schema.json",
        ComponentDataHandBuildComponent,
    ),
]


def schema_file_path(spec_subdir: str, filename: str) -> str:
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../spec", spec_subdir, filename)
    )


def save_schema(dir: str, filename: str, schema: dict[str, Any]) -> None:
    file_path = schema_file_path(dir, filename)
    with open(file_path, "w") as file:
        logger.info("Saving schema to %s", file_path)
        file.write(json.dumps(schema, indent=2))


def regenerate_schemas() -> None:
    """Regnerate schema store in /spec directory"""

    for sub_dir, filename, schema_model in itertools.chain(
        config_schemas, component_schemas
    ):
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
