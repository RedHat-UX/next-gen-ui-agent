from typing import Any, Literal, TypedDict


class ResponseEvent(TypedDict):
    """NextGenUILlamaStackAgent response event."""

    event_type: Literal["component_metadata", "rendering"]
    payload: Any
