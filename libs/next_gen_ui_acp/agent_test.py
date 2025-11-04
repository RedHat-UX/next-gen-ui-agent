import json
from unittest.mock import patch

import pytest
from acp_sdk import Artifact, Message, MessagePart
from next_gen_ui_acp.agent import NextGenUIACPAgent
from next_gen_ui_agent.types import UIBlock, UIComponentMetadata
from next_gen_ui_testing.data_set_movies import find_movie
from next_gen_ui_testing.model import MockedInference

user_input = "Tell me brief details of Toy Story"
user_message = Message(
    role="user",
    parts=[MessagePart.model_validate({"content": user_input, "role": "user"})],
)

movies_data = find_movie("Toy Story")
tool_message = Message(
    role="agent",
    parts=[
        Artifact.model_validate(
            {
                "content": json.dumps(movies_data, default=str),
                "name": "tool_output",
            }
        )
    ],
)

# Create a second tool message for parallel processing tests
movies_data_2 = find_movie("The Matrix")
tool_message_2 = Message(
    role="agent",
    parts=[
        MessagePart.model_validate(
            {
                "content": json.dumps(movies_data_2, default=str),
                "metadata": {"kind": "trajectory", "tool_name": "my_tool"},
            }
        )
    ],
)


@pytest.mark.asyncio
async def test_agent_run_yields_messages_independently() -> None:
    """Test that run() yields each message independently."""
    mocked_component: UIComponentMetadata = UIComponentMetadata.model_validate(
        {
            "title": "Toy Story",
            "reasonForTheComponentSelection": "One item available in the data",
            "confidenceScore": "100%",
            "component": "one-card",
            "fields": [
                {"name": "Title", "data_path": "movie.title"},
                {"name": "Year", "data_path": "movie.year"},
                {"name": "IMDB Rating", "data_path": "movie.imdbRating"},
            ],
            "id": "2ff0f4bd-6b66-4b22-a7eb-8bb0365f52b1",
        }
    )

    mocked_inference = MockedInference(mocked_component)
    ngui_agent = NextGenUIACPAgent(
        component_system="json",
        inference=mocked_inference,
    )

    # Collect all yielded messages
    messages = []
    async for message in ngui_agent.run(input=[user_message, tool_message]):
        messages.append(message)

    # Should yield exactly one message for one tool message
    assert len(messages) == 1

    # Check the message structure
    message = messages[0]
    assert len(message.parts) == 1
    artifact = message.parts[0]
    assert artifact.name == "ui_block"
    assert artifact.content_type == "application/json"

    # Verify content contains expected data
    assert artifact.content is not None
    content = json.loads(artifact.content)
    assert "rendering" in content
    assert "configuration" in content


@pytest.mark.asyncio
async def test_agent_run_processes_multiple_tools_in_parallel() -> None:
    """Test that run() processes multiple tool messages in parallel."""
    mocked_component: UIComponentMetadata = UIComponentMetadata.model_validate(
        {
            "title": "Movie",
            "reasonForTheComponentSelection": "One item available in the data",
            "confidenceScore": "100%",
            "component": "one-card",
            "fields": [
                {"name": "Title", "data_path": "movie.title"},
                {"name": "Year", "data_path": "movie.year"},
            ],
            "id": "2ff0f4bd-6b66-4b22-a7eb-8bb0365f52b1",
        }
    )

    mocked_inference = MockedInference(mocked_component)
    ngui_agent = NextGenUIACPAgent(
        component_system="json",
        inference=mocked_inference,
    )

    # Collect all yielded messages
    messages = []
    async for message in ngui_agent.run(
        input=[user_message, tool_message, tool_message_2]
    ):
        messages.append(message)

    # Should yield two messages for two tool messages
    assert len(messages) == 2

    # Both should be valid ui_block artifacts
    for message in messages:
        assert len(message.parts) == 1
        artifact = message.parts[0]
        assert artifact.name == "ui_block"
        assert artifact.content_type == "application/json"
        assert message.role == "agent"
        assert artifact.content is not None
        UIBlock.model_validate(json.loads(artifact.content))


@pytest.mark.asyncio
async def test_agent_run_error_handling() -> None:
    """Test that run() handles errors gracefully and yields error messages."""
    mocked_component: UIComponentMetadata = UIComponentMetadata.model_validate(
        {
            "title": "Error Test",
            "reasonForTheComponentSelection": "Testing error handling",
            "confidenceScore": "100%",
            "component": "one-card",
            "fields": [
                {"name": "Title", "data_path": "movie.title"},
            ],
            "id": "error-test-id",
        }
    )

    mocked_inference = MockedInference(mocked_component)
    ngui_agent = NextGenUIACPAgent(
        component_system="json",
        inference=mocked_inference,
    )

    # Mock select_component to raise an exception
    with patch.object(
        ngui_agent.ngui_agent,
        "select_component",
        side_effect=Exception("Test error message"),
    ):
        # Collect all yielded messages
        messages = []
        async for message in ngui_agent.run(input=[user_message, tool_message]):
            messages.append(message)

        # Should still yield one message (error message)
        assert len(messages) == 1

        # Check it's an error message
        message = messages[0]
        assert len(message.parts) == 1
        artifact = message.parts[0]
        assert artifact.name == "error"
        assert artifact.content_type == "text/plain"
        assert (
            artifact.content
            == "Error processing input data into UI component: Test error message"
        )


@pytest.mark.asyncio
async def test_agent_run_mixed_success_and_error() -> None:
    """Test that run() handles a mix of successful and failed processing."""
    mocked_component: UIComponentMetadata = UIComponentMetadata.model_validate(
        {
            "title": "Mixed Test",
            "reasonForTheComponentSelection": "Testing mixed results",
            "confidenceScore": "100%",
            "component": "one-card",
            "fields": [
                {"name": "Title", "data_path": "movie.title"},
            ],
            "id": "mixed-test-id",
        }
    )

    mocked_inference = MockedInference(mocked_component)
    ngui_agent = NextGenUIACPAgent(
        component_system="json",
        inference=mocked_inference,
    )

    # Track call count to make first call fail and second succeed
    call_count = 0
    original_select = ngui_agent.ngui_agent.select_component

    async def select_component_mock(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise Exception("First tool failed")
        return await original_select(*args, **kwargs)

    with patch.object(
        ngui_agent.ngui_agent,
        "select_component",
        side_effect=select_component_mock,
    ):
        # Collect all yielded messages
        messages = []
        async for message in ngui_agent.run(
            input=[user_message, tool_message, tool_message_2]
        ):
            messages.append(message)

        # Should yield two messages (one error, one success)
        assert len(messages) == 2

        # Count error vs success messages
        error_messages = [m for m in messages if m.parts[0].name == "error"]
        success_messages = [m for m in messages if m.parts[0].name == "ui_block"]

        assert len(error_messages) == 1
        assert len(success_messages) == 1

        # Check error message
        error_artifact = error_messages[0].parts[0]
        assert error_artifact.content_type == "text/plain"
        assert error_artifact.name == "error"
        assert (
            error_artifact.content
            == "Error processing input data into UI component: First tool failed"
        )

        # Check success message
        assert success_messages[0].role == "agent"
        assert success_messages[0].parts[0].name == "ui_block"
        assert success_messages[0].parts[0].content_type == "application/json"
        assert success_messages[0].parts[0].content is not None
        UIBlock.model_validate(json.loads(success_messages[0].parts[0].content))
