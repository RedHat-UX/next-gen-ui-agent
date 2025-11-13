from typing import Literal

from next_gen_ui_agent.types import UIBlock
from typing_extensions import TypedDict


class ResponseEventSuccess(TypedDict):
    """NextGenUILlamaStackAgent successfull processing response event."""

    event_type: Literal["success"]
    payload: list[UIBlock]


class ResponseEventError(TypedDict):
    """NextGenUILlamaStackAgent processing error response event."""

    event_type: Literal["error"]
    payload: Exception
