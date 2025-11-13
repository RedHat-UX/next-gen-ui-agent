import json
import logging

import pytest
from llama_stack_client import AsyncLlamaStackClient, LlamaStackClient
from llama_stack_client.types.inference_step import InferenceStep
from llama_stack_client.types.tool_execution_step import ToolExecutionStep
from next_gen_ui_agent.types import (
    AgentConfig,
    AgentConfigComponent,
    AgentConfigDataType,
    UIBlock,
    UIComponentMetadata,
)
from next_gen_ui_llama_stack import NextGenUILlamaStackAgent
from next_gen_ui_testing.data_set_movies import find_movie
from next_gen_ui_testing.model import MockedInference

logger = logging.getLogger(__name__)

user_input = "Tell me brief details of Toy Story"

step1_InferenceStep = """
 {
  "api_model_response": {
    "content": "{\\n    \\"thought\\": \\"I will use the tool 'movies' to get details of Toy Story\\",\\n    \\"action\\": {\\n        \\"tool_name\\": \\"movies\\",\\n        \\"tool_params\\": [{\\"name\\": \\"title\\", \\"value\\": \\"Toy Story\\"}]\\n    },\\n    \\"answer\\": null\\n}",
    "role": "assistant",
    "stop_reason": "end_of_turn",
    "tool_calls": []
  },
  "step_id": "1c072adb-1e68-415d-907a-046bf0248709",
  "step_type": "inference",
  "turn_id": "ce956552-1d35-45ac-850a-b44d61ed8c8c",
  "completed_at": "2025-03-14T10:52:14.891085Z",
  "started_at": "2025-03-14T10:52:09.760519Z"
}
"""
step1 = InferenceStep(
    **json.loads(step1_InferenceStep.replace("api_model_response", "model_response"))
)

movies_data = find_movie("Toy Story")

step2_ToolExecutionStep = {
    "step_id": "90cbfdfe-20ed-477d-9879-202c8103a6d3",
    "step_type": "tool_execution",
    "tool_calls": [],
    "tool_responses": [
        {
            "call_id": "b8807f6c-ea68-4f5f-a369-4a1542132e7a",
            "content": json.dumps(movies_data, default=str),
            "tool_name": "movies",
        }
    ],
    "turn_id": "a3c76fd9-2ee0-48ff-9622-8a92adf73a44",
    "completed_at": "2025-03-18T12:00:32.383978Z",
    "started_at": "2025-03-18T12:00:32.383978Z",
}
step2 = ToolExecutionStep.model_validate(step2_ToolExecutionStep)

step3_InferenceStep = """
 {
  "api_model_response": {
    "content": "{\\n    \\"thought\\": \\"I have retrieved the details of Toy Story from the movies database\\",\\n    \\"action\\": {\\n        \\"tool_name\\": \\"movies\\",\\n        \\"tool_params\\": [\\n            {\\"name\\": \\"title\\", \\"value\\": \\"Toy Story\\"}\\n        ]\\n    },\\n    \\"answer\\": \\"\\\\n    {\\\\n        \\\\\\"movie\\\\\\":{\\\\n        \\\\\\"languages\\\\\\":[\\\\n            \\\\\\"English\\\\\\"\\\\n        ],\\\\n        \\\\\\"year\\\\\\":1995,\\\\n        \\\\\\"imdbId\\\\\\":\\\\\\"0114709\\\\\\",\\\\n        \\\\\\"runtime\\\\\\":81,\\\\n        \\\\\\"imdbRating\\\\\\":8.3,\\\\n        \\\\\\"movieId\\\\\\":\\\\\\"1\\\\\\",\\\\n        \\\\\\"countries\\\\\\":[\\\\n            \\\\\\"USA\\\\\\"\\\\n        ],\\\\n        \\\\\\"imdbVotes\\\\\\":591836,\\\\n        \\\\\\"title\\\\\\":\\\\\\"Toy Story\\\\\\",\\\\n        \\\\\\"url\\\\\\":\\\\\\"https://themoviedb.org/movie/862\\\\\\",\\\\n        \\\\\\"revenue\\\\\\":373554033,\\\\n        \\\\\\"tmdbId\\\\\\":\\\\\\"862\\\\\\",\\\\n        \\\\\\"plot\\\\\\":\\\\\\"A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room.\\\\\\",\\\\n        \\\\\\"posterUrl\\\\\\":\\\\\\"https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg\\\\\\",\\\\n        \\\\\\"released\\\\\\":\\\\\\"1995-11-22\\\\\\",\\\\n        \\\\\\"trailerUrl\\\\\\": \\\\\\"https://www.youtube.com/watch?v=v-PjgYDrg70\\\\\\",\\\\n        \\\\\\"budget\\\\\\":30000000\\\\n        },\\\\n        \\\\\\"actors\\\\\\":[\\\\n        \\\\\\"Jim Varney\\\\\\",\\\\n        \\\\\\"Tim Allen\\\\\\",\\\\n        \\\\\\"Tom Hanks\\\\\\",\\\\n        \\\\\\"Don Rickles\\\\\\"\\\\n        ]\\\\n    }\\\\n\\" }",
    "role": "assistant",
    "stop_reason": "end_of_turn",
    "tool_calls": []
  },
  "step_id": "cad25fe5-9d11-42b4-9341-17d2dd698672",
  "step_type": "inference",
  "turn_id": "ce956552-1d35-45ac-850a-b44d61ed8c8c",
  "completed_at": "2025-03-14T10:52:32.440481Z",
  "started_at": "2025-03-14T10:52:14.951638Z"
}
"""
step3 = InferenceStep(
    **json.loads(step3_InferenceStep.replace("api_model_response", "model_response"))
)

movies_data_2 = find_movie("Forrest Gump")
movies_data_3 = find_movie("The Matrix")

step2_two_tools = ToolExecutionStep.model_validate(
    {
        "step_id": "90cbfdfe-20ed-477d-9879-202c8103a6d3",
        "step_type": "tool_execution",
        "tool_calls": [],
        "tool_responses": [
            {
                "call_id": "b8807f6c-ea68-4f5f-a369-4a1542132e7a",
                "content": json.dumps(movies_data, default=str),
                "tool_name": "movies",
            },
            {
                "call_id": "c9918g7d-fb79-5g6g-b470-5b2653243f8b",
                "content": json.dumps(movies_data_2, default=str),
                "tool_name": "movies",
            },
        ],
        "turn_id": "a3c76fd9-2ee0-48ff-9622-8a92adf73a44",
        "completed_at": "2025-03-18T12:00:32.383978Z",
        "started_at": "2025-03-18T12:00:32.383978Z",
    }
)

step2_three_tools = ToolExecutionStep.model_validate(
    {
        "step_id": "90cbfdfe-20ed-477d-9879-202c8103a6d3",
        "step_type": "tool_execution",
        "tool_calls": [],
        "tool_responses": [
            {
                "call_id": "id-success-1",
                "content": json.dumps(movies_data, default=str),
                "tool_name": "movies",
            },
            {
                "call_id": "id-error",
                "content": json.dumps(movies_data_2, default=str),
                "tool_name": "movies",
            },
            {
                "call_id": "id-success-2",
                "content": json.dumps(movies_data_3, default=str),
                "tool_name": "movies",
            },
        ],
        "turn_id": "a3c76fd9-2ee0-48ff-9622-8a92adf73a44",
        "completed_at": "2025-03-18T12:00:32.383978Z",
        "started_at": "2025-03-18T12:00:32.383978Z",
    }
)

mocked_component_two_tools: UIComponentMetadata = UIComponentMetadata.model_validate(
    {
        "title": "Movie Details",
        "reasonForTheComponentSelection": "One item available in the data",
        "confidenceScore": "100%",
        "component": "one-card",
        "fields": [
            {"name": "Title", "data_path": "movie.title"},
            {"name": "Year", "data_path": "movie.year"},
            {"name": "IMDB Rating", "data_path": "movie.imdbRating"},
        ],
    }
)


@pytest.mark.asyncio
async def test_agent_turn_batch_from_steps() -> None:
    mocked_inference = MockedInference(mocked_component_two_tools)
    client = LlamaStackClient()
    ngui_agent = NextGenUILlamaStackAgent(
        client, "not-used", inference=mocked_inference, execution_mode="batch"
    )

    event_count = 0
    ui_block_ids_seen = set()

    async for ng_event in ngui_agent.create_turn(
        user_input, steps=[step1, step2_two_tools, step3], component_system="json"
    ):
        if ng_event["event_type"] == "success":
            event_count += 1
            logger.info(
                "Success event #%d with %d blocks",
                event_count,
                len(ng_event["payload"]),
            )

            # In batch mode, all blocks should be yielded at once
            assert (
                len(ng_event["payload"]) == 2
            ), "Batch mode should yield all UIBlocks at once"

            for ui_block in ng_event["payload"]:
                payload_success: UIBlock = ui_block
                assert payload_success is not None
                assert payload_success.rendering is not None
                rendering = json.loads(str(payload_success.rendering.content))
                assert rendering is not None
                assert "title" in rendering or "movie" in rendering
                ui_block_ids_seen.add(payload_success.id)
                logger.info("Processed UIBlock with id=%s", payload_success.id)

        elif ng_event["event_type"] == "error":
            assert False, "Should not receive error events"

    # Verify we got exactly one event with 2 UIBlocks
    assert event_count == 1, "Batch mode should yield all results in one event"
    assert len(ui_block_ids_seen) == 2, "Should process 2 different UI blocks"
    assert (
        "b8807f6c-ea68-4f5f-a369-4a1542132e7a" in ui_block_ids_seen
    ), f"Expected tool response ID not found in UI blocks: {ui_block_ids_seen}"
    assert (
        "c9918g7d-fb79-5g6g-b470-5b2653243f8b" in ui_block_ids_seen
    ), f"Expected tool response ID not found in UI blocks: {ui_block_ids_seen}"


@pytest.mark.asyncio
async def test_agent_turn_batch_with_exception() -> None:
    """Test batch mode handles exceptions and yields error event."""
    mocked_inference = MockedInference(mocked_component_two_tools)
    client = LlamaStackClient()
    ngui_agent = NextGenUILlamaStackAgent(
        client, "not-used", inference=mocked_inference, execution_mode="batch"
    )

    # Patch transform_data to throw exception for specific ID
    original_transform = ngui_agent.ngui_agent.transform_data

    def transform_with_error(input_data, component):
        if input_data["id"] == "c9918g7d-fb79-5g6g-b470-5b2653243f8b":
            raise ValueError(f"Simulated error for component {component.id}")
        return original_transform(input_data, component)

    ngui_agent.ngui_agent.transform_data = transform_with_error  # type: ignore

    success_count = 0
    error_count = 0

    async for ng_event in ngui_agent.create_turn(
        user_input, steps=[step1, step2_two_tools, step3], component_system="json"
    ):
        event_type = ng_event["event_type"]

        if event_type == "success":
            success_count += 1
            logger.info("Unexpected success event in batch mode with exception")
            assert (
                False
            ), "Should not receive success events when batch processing fails"

        elif event_type == "error":
            error_count += 1
            payload_error = ng_event["payload"]
            assert payload_error is not None
            assert isinstance(payload_error, Exception)
            logger.info("Error event: %s", str(payload_error))
            assert isinstance(payload_error, ValueError)
            assert "Simulated error" in str(payload_error)

    # Verify we got expected events: 0 successes and 1 error
    # In batch mode, if any component fails, the entire batch fails
    assert success_count == 0, f"Should receive 0 success events, got {success_count}"
    assert error_count == 1, f"Should receive 1 error event, got {error_count}"

    logger.info(
        "Batch mode with exception test completed: %d success, %d error events",
        success_count,
        error_count,
    )


@pytest.mark.asyncio
async def test_agent_turn_batch_from_steps_async() -> None:
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
    client = AsyncLlamaStackClient()
    ngui_agent = NextGenUILlamaStackAgent(
        client, "not-used", inference=mocked_inference, execution_mode="batch"
    )

    async for ng_event in ngui_agent.create_turn(
        user_input, steps=[step1, step2, step3], component_system="json"
    ):
        if ng_event["event_type"] == "success":
            payload_success: UIBlock = ng_event["payload"][0]
            assert payload_success is not None
            assert payload_success.rendering is not None
            rendering = json.loads(str(payload_success.rendering.content))
            assert rendering is not None
            assert rendering["title"] == "Toy Story"
        elif ng_event["event_type"] == "error":
            assert False, "Should not receive error events"


@pytest.mark.asyncio
async def test_agent_turn_batch_from_steps_async_hbc() -> None:
    """Test that hand-build components are selected correctly based on tool name."""
    client = AsyncLlamaStackClient()
    ngui_agent = NextGenUILlamaStackAgent(
        client,
        "not-used",
        # register HBC for `movies` tool_name
        config=AgentConfig(
            data_types={
                "movies": AgentConfigDataType(
                    components=[AgentConfigComponent(component="my-ui-component")]
                )
            }
        ),
    )

    async for ng_event in ngui_agent.create_turn(
        user_input, steps=[step1, step2, step3], component_system="json"
    ):
        if ng_event["event_type"] == "success":
            payload_success: UIBlock = ng_event["payload"][0]
            assert payload_success is not None
            assert payload_success.rendering is not None
            assert payload_success.configuration is not None
            assert payload_success.configuration.component_metadata is not None
            assert (
                payload_success.configuration.component_metadata.component
                == "hand-build-component"
            )
            rendering = json.loads(str(payload_success.rendering.content))
            assert rendering is not None
            assert rendering["component"] == "my-ui-component"
        elif ng_event["event_type"] == "error":
            assert False, "Should not receive error events"


@pytest.mark.asyncio
async def test_agent_turn_streamdefault_from_steps_async() -> None:
    """Test progressive streaming mode where success events are yielded as components complete."""
    mocked_inference = MockedInference(mocked_component_two_tools)
    client = AsyncLlamaStackClient()
    ngui_agent = NextGenUILlamaStackAgent(
        client, "not-used", inference=mocked_inference
    )

    success_count = 0
    event_sequence = []
    ui_block_ids_seen = set()

    async for ng_event in ngui_agent.create_turn(
        user_input, steps=[step1, step2_two_tools, step3], component_system="json"
    ):
        event_type = ng_event["event_type"]
        event_sequence.append(event_type)

        if event_type == "success":
            success_count += 1
            # In progressive mode, payload should be a single-item list of UIBlock
            payload_success: UIBlock = ng_event["payload"][0]  # type: ignore
            assert payload_success is not None
            assert payload_success.rendering is not None
            logger.info(
                "Progressive success event #%d, id=%s",
                success_count,
                payload_success.id,
            )

            ui_block_ids_seen.add(payload_success.id)
        elif event_type == "error":
            assert False, "Should not receive error events"

    # Verify we got the expected number of success events
    assert success_count == 2, "Should receive 2 success events (one per component)"

    # Verify both components were processed with the correct IDs from tool responses
    assert len(ui_block_ids_seen) == 2, "Should process 2 different UI blocks"
    assert (
        "b8807f6c-ea68-4f5f-a369-4a1542132e7a" in ui_block_ids_seen
    ), f"Expected tool response ID not found in UI blocks: {ui_block_ids_seen}"
    assert (
        "c9918g7d-fb79-5g6g-b470-5b2653243f8b" in ui_block_ids_seen
    ), f"Expected tool response ID not found in UI blocks: {ui_block_ids_seen}"

    # Verify all events were success
    assert event_sequence.count("success") == 2
    assert event_sequence.count("error") == 0

    logger.info(
        "Progressive mode test completed successfully with %d success events",
        success_count,
    )


@pytest.mark.asyncio
async def test_agent_turn_stream_with_exception() -> None:
    """Test progressive mode handles exceptions and yields error events."""
    mocked_inference = MockedInference(mocked_component_two_tools)
    client = AsyncLlamaStackClient()
    ngui_agent = NextGenUILlamaStackAgent(
        client, "not-used", inference=mocked_inference, execution_mode="stream"
    )

    # Patch transform_data to throw exception for specific ID
    original_transform = ngui_agent.ngui_agent.transform_data

    def transform_with_error(input_data, component):
        if input_data["id"] == "id-error":
            raise ValueError(f"Simulated error for component {component.id}")
        return original_transform(input_data, component)

    ngui_agent.ngui_agent.transform_data = transform_with_error  # type: ignore

    success_count = 0
    error_count = 0
    event_sequence = []

    async for ng_event in ngui_agent.create_turn(
        user_input, steps=[step1, step2_three_tools, step3], component_system="json"
    ):
        event_type = ng_event["event_type"]
        event_sequence.append(event_type)

        if event_type == "success":
            success_count += 1
            payload_success: UIBlock = ng_event["payload"][0]  # type: ignore
            assert payload_success is not None
            assert payload_success.rendering is not None
            rendering = json.loads(str(payload_success.rendering.content))
            assert rendering is not None
            logger.info("Success event for id=%s", payload_success.id)
            assert payload_success.id in ["id-success-1", "id-success-2"]

        elif event_type == "error":
            error_count += 1
            payload_error = ng_event["payload"]
            assert payload_error is not None
            assert isinstance(payload_error, Exception)
            logger.info("Error event: %s", str(payload_error))
            assert isinstance(payload_error, ValueError)
            assert "Simulated error" in str(payload_error)

    # Verify we got expected events: 2 successes and 1 error
    assert success_count == 2, f"Should receive 2 success events, got {success_count}"
    assert error_count == 1, f"Should receive 1 error event, got {error_count}"

    # Verify event counts
    assert event_sequence.count("success") == 2
    assert event_sequence.count("error") == 1

    logger.info(
        "Progressive mode with exception test completed: %d success, %d error events",
        success_count,
        error_count,
    )
