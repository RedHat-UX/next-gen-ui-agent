from typing import NotRequired, TypedDict

from next_gen_ui_agent.data_transform.types import ComponentDataBase
from next_gen_ui_agent.data_transform.validation.types import (
    ComponentDataValidationError,
)

BASE_MODULE_PATH = "tests/ai_eval_components/"
BASE_DATASET_PATH = BASE_MODULE_PATH + "dataset/"
DATASET_FILE_SUFFIX = ".json"


class DatasetRowSrc(TypedDict):
    prompt_file: NotRequired[str]
    data_file: NotRequired[str]


class DatasetRow(TypedDict):
    id: str
    user_prompt: str
    backend_data: str
    expected_component: str
    warn_only: NotRequired[bool]
    src: NotRequired[DatasetRowSrc]


class DatasetRowAgentEvalResult:
    errors: list[ComponentDataValidationError]
    llm_output: str
    data: ComponentDataBase | None

    def __init__(
        self,
        llm_output: str,
        errors: list[ComponentDataValidationError],
        data: ComponentDataBase | None,
    ):
        self.llm_output = llm_output
        self.errors = errors
        self.data = data


class ItemsGenerate(TypedDict):
    prompts_file: str
    backend_data_files: list[str]
    warn_only: NotRequired[bool]
