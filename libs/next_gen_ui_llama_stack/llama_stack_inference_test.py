from llama_stack_client.types.shared import (
    ChatCompletionResponse,
    CompletionMessage,
    SystemMessage,
    UserMessage,
)
from next_gen_ui_llama_stack.llama_stack_inference import process_response
from pytest import fail

INPUT_MESSAGES = [
    SystemMessage(role="system", content="sys prompt"),
    UserMessage(role="user", content="usr prompt"),
]


def test_process_response_INVALID_OBJECT() -> None:
    try:
        process_response("", INPUT_MESSAGES)
        fail("NotImplementedError expected")
    except NotImplementedError:
        pass


def test_process_response_OK_CONTENT_STR() -> None:
    res = ChatCompletionResponse(
        completion_message=CompletionMessage(
            content="res message", role="assistant", stop_reason="end_of_turn"
        )
    )
    response = process_response(res, INPUT_MESSAGES)

    assert response == "res message"


def test_process_response_OK_CONTENT_NONSTR() -> None:
    res = ChatCompletionResponse(
        completion_message=CompletionMessage(
            content={"text": "res content 1", "type": "text"},  # type: ignore
            role="assistant",
            stop_reason="end_of_turn",
        )
    )
    response = process_response(res, INPUT_MESSAGES)

    assert response == "TextContentItem(text='res content 1', type='text')"
