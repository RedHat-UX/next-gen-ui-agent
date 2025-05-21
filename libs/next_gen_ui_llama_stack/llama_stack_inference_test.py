import asyncio
import os

from llama_stack_client import LlamaStackClient
from llama_stack_client.types.shared import (
    ChatCompletionResponse,
    CompletionMessage,
    SystemMessage,
    UserMessage,
)
from next_gen_ui_llama_stack.llama_stack_inference import (
    LlamaStackAgentInference,
    process_response,
)
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


if __name__ == "__main__":
    """Allows to run inference test against real LLamaStack model"""

    host = os.getenv("LLAMA_STACK_HOST", default="localhost")
    port = os.getenv("LLAMA_STACK_PORT", default="5001")
    base_url = f"http://{host}:{port}"

    model = os.getenv("INFERENCE_MODEL", default="granite3.2:latest")

    client = LlamaStackClient(base_url=base_url)
    inference = LlamaStackAgentInference(client, model)
    response = asyncio.run(
        inference.call_model(
            "use tool named get_current_time to get the current time",
            "what is the current time?",
        )
    )

    print("Response: " + response)
