from typing import NotRequired, TypedDict

BASE_MODULE_PATH = "tests/ai_eval_components/"
BASE_DATASET_PATH = BASE_MODULE_PATH + "dataset/"
DATASET_FILE_SUFFIX = ".json"


class EvalError:
    code: str
    message: str

    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return f'"{self.code}: {self.message}"'

    def __repr__(self):
        return f'"{self.code}: {self.message}"'


class DatasetRowSrc(TypedDict):
    prompt_file: NotRequired[str]
    data_file: NotRequired[str]


class DatasetRow(TypedDict):
    id: str
    user_prompt: str
    backend_data: str
    expected_component: str
    src: NotRequired[DatasetRowSrc]


class DatasetRowAgentEvalResult:
    errors: list[EvalError]
    llm_output: str

    def __init__(self, llm_output, errors):
        self.llm_output = llm_output
        self.errors = errors


class ItemsGenerate(TypedDict):
    prompts_file: str
    backend_data_files: list[str]
