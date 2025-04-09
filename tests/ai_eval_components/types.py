from typing import TypedDict

from next_gen_ui_agent.types import UIComponentMetadata


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


class DatasetRow(TypedDict):
    id: str
    user_prompt: str
    backend_data: str
    expected_component: str


class DatasetRowAgentEvalResult:
    errors: list[EvalError]
    component: UIComponentMetadata

    def __init__(self, component, errors):
        self.component = component
        self.errors = errors
