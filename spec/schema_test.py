import json
import logging

import pytest
from next_gen_ui_a2a.spec_schema import a2a_schemas
from next_gen_ui_a2a.spec_schema import regenerate_schemas as a2a_generate_schemas
from next_gen_ui_agent.data_transform.json_schema_config import CustomGenerateJsonSchema
from next_gen_ui_agent.spec_schema import component_schemas, config_schemas
from next_gen_ui_agent.spec_schema import regenerate_schemas as agent_generate_schemas
from next_gen_ui_agent.spec_schema import schema_file_path
from next_gen_ui_mcp.spec_schema import mcp_schemas
from next_gen_ui_mcp.spec_schema import regenerate_schemas as mcp_generate_schemas
from pydantic import BaseModel


def test_schema_no_title() -> None:
    _dir, _filename, schema_model = component_schemas[0]
    schema = schema_model.model_json_schema(schema_generator=CustomGenerateJsonSchema)
    schema_str = json.dumps(schema, indent=2)
    assert '"title": "Title"' not in schema_str


@pytest.mark.parametrize("dir,filename,schema_model", config_schemas)
def test_config_schemas(dir: str, filename: str, schema_model: BaseModel) -> None:
    with open(schema_file_path(dir, filename)) as file:
        file_content = file.read()

    # validate that schema is equal
    schema = schema_model.model_json_schema(schema_generator=CustomGenerateJsonSchema)
    assert (
        json.dumps(schema, indent=2) == file_content
    ), f"The schema stored in  {dir}/{filename} needs to be updated. It does not equal to actual Model. Please re-run schema generation by 'PYTHONPATH=./libs python spec/schema_test.py'"


@pytest.mark.parametrize("dir,filename,schema_model", component_schemas)
def test_component_schemas(dir: str, filename: str, schema_model: BaseModel) -> None:
    with open(schema_file_path(dir, filename)) as file:
        file_content = file.read()

    # validate that schema is equal
    schema = schema_model.model_json_schema(schema_generator=CustomGenerateJsonSchema)
    assert (
        json.dumps(schema, indent=2) == file_content
    ), f"The schema stored in  {dir}/{filename} needs to be updated. It does not equal to actual Model. Please re-run schema generation by 'PYTHONPATH=./libs python spec/schema_test.py'"


@pytest.mark.parametrize("dir,filename,schema_model", mcp_schemas)
def test_mcp_schemas(dir: str, filename: str, schema_model: BaseModel) -> None:
    with open(schema_file_path(dir, filename)) as file:
        file_content = file.read()

    # validate that schema is equal
    schema = schema_model.model_json_schema(schema_generator=CustomGenerateJsonSchema)
    assert (
        json.dumps(schema, indent=2) == file_content
    ), f"The schema stored in  {dir}/{filename} needs to be updated. It does not equal to actual Model. Please re-run schema generation by 'PYTHONPATH=./libs python spec/schema_test.py'"


@pytest.mark.parametrize("dir,filename,schema_model", a2a_schemas)
def test_a2a_schemas(dir: str, filename: str, schema_model: BaseModel) -> None:
    with open(schema_file_path(dir, filename)) as file:
        file_content = file.read()

    # validate that schema is equal
    schema = schema_model.model_json_schema(schema_generator=CustomGenerateJsonSchema)
    assert (
        json.dumps(schema, indent=2) == file_content
    ), f"The schema stored in  {dir}/{filename} needs to be updated. It does not equal to actual Model. Please re-run schema generation by 'PYTHONPATH=./libs python spec/schema_test.py'"


# Run this file to regenerate all schemas
if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    agent_generate_schemas()
    mcp_generate_schemas()
    a2a_generate_schemas()
