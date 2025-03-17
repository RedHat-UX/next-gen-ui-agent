from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class InputData:
    id: str
    data: str


@dataclass
class AgentInput:
    user_prompt: str
    input_data: list[InputData]


@dataclass(eq=False)
class DataPath:
    name: str
    data_path: str
    data: Optional[list[str]] = None

    def __eq__(self, other):
        return self.data_path == other.data_path


@dataclass(eq=False)
class UIComponentMetadata:
    id: str
    title: str
    reasonForTheComponentSelection: str
    confidenceScore: str
    component: str
    fields: list[DataPath]

    def __eq__(self, other):
        return self.id == other.id
