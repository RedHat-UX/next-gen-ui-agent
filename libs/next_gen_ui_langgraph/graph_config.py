from typing import Literal, Optional, TypedDict

from langgraph.graph import MessagesState


class DataPath(TypedDict):
    name: str
    data_path: str
    data: list[str]


class BackendData(TypedDict):
    id: str
    data: str


class UIComponent(TypedDict):
    id: str
    title: str
    component: str
    fields: list[DataPath]


# Graph State Schema
class AgentState(MessagesState):
    backend_data: list[BackendData]
    user_prompt: str
    components: list[UIComponent]


class AgentInputState(MessagesState):
    backend_data: list[BackendData]
    user_prompt: str


class AgentOutputState(MessagesState):
    components: list[UIComponent]


# Graph Config Schema
class AgentConfig(TypedDict):
    model: Optional[str]
    model_api_base_url: Optional[str]
    model_api_token: Optional[str]
    component_system: Literal["none", "patternfly", "rhds"]
