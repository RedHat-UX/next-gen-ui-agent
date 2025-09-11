from typing import Any, Literal

from typing_extensions import TypedDict


class ResponseEvent(TypedDict):
    """NextGenUILlamaStackAgent response event."""

    event_type: Literal["component_metadata", "rendering"]
    payload: Any
