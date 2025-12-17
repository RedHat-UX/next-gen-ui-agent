from uuid import uuid4

import pytest
from a2a.server.agent_execution import SimpleRequestContextBuilder
from a2a.server.events import EventQueue
from a2a.types import DataPart, Message, MessageSendParams, Part, Role, TextPart
from a2a.utils.errors import ServerError
from langchain_core.language_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage
from next_gen_ui_a2a.agent_executor import NextGenUIAgentExecutor
from next_gen_ui_agent.data_transform.types import ComponentDataOneCard
from next_gen_ui_agent.inference.langchain_inference import LangChainModelInference
from next_gen_ui_agent.types import AgentConfig, UIBlock

USER_PROMPT = "Tell me brief details of Toy Story"
movies_data_obj = {
    "movie": {
        "languages": ["English"],
        "year": 1995,
        "imdbId": "0114709",
        "runtime": 81,
        "imdbRating": 8.3,
        "movieId": "1",
        "countries": ["USA"],
        "imdbVotes": 591836,
        "title": "Toy Story",
        "url": "https://themoviedb.org/movie/862",
        "revenue": 373554033,
        "tmdbId": "862",
        "plot": "A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room.",
        "posterUrl": "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
        "released": "2022-11-02",
        "trailerUrl": "https://www.youtube.com/watch?v=v-PjgYDrg70",
        "budget": 30000000,
    },
    "actors": ["Jim Varney", "Tim Allen", "Tom Hanks", "Don Rickles"],
}
LLM_RESPONSE = """
    {
        "title": "Toy Story Details",
        "reasonForTheComponentSelection": "One item available in the data",
        "confidenceScore": "100%",
        "component": "one-card",
        "fields" : [
            {"id": "title", "name":"Title","data_path":"movie.title"},
            {"id": "year", "name":"Year","data_path":"movie.year"},
            {"id": "imdb", "name":"IMDB Rating","data_path":"movie.imdbRating"},
            {"id": "released", "name":"Release Date","data_path":"movie.released"}
        ]
    }
    """


@pytest.mark.asyncio
async def test_agent_executor_one_part_input_with_metadata() -> None:
    msg = AIMessage(content=LLM_RESPONSE)
    llm = FakeMessagesListChatModel(responses=[msg])
    inference = LangChainModelInference(llm)

    executor = NextGenUIAgentExecutor(inference=inference, config=AgentConfig())

    message = Message(
        role=Role.user,
        parts=[
            Part(
                root=TextPart(
                    text="Tell me details about Toy Story",
                    metadata={
                        "data": movies_data_obj,
                        "type": "search_movie",
                    },
                )
            ),
        ],
        message_id=str(uuid4()),
    )

    context = await SimpleRequestContextBuilder().build(
        params=MessageSendParams(message=message)
    )

    event_queue = EventQueue()
    await executor.execute(context, event_queue)

    event = await event_queue.dequeue_event(no_wait=True)
    assert isinstance(event, Message)
    assert len(event.parts) == 2

    assert isinstance(event.parts[0].root, TextPart)
    assert event.parts[0].root.text.startswith("Component is rendered in UI.")
    assert "title: 'Toy Story Details'" in event.parts[0].root.text
    assert "component_type: one-card" in event.parts[0].root.text

    assert isinstance(event.parts[1].root, DataPart)
    ui_block = UIBlock.model_validate(event.parts[1].root.data)
    assert ui_block.configuration is not None
    assert ui_block.configuration.data_type == "search_movie"
    assert ui_block.configuration.component_metadata is not None
    assert "one-card" == ui_block.configuration.component_metadata.component
    assert ui_block.rendering is not None
    c = ComponentDataOneCard.model_validate_json(ui_block.rendering.content)
    assert "one-card" == c.component
    assert "Toy Story Details" == c.title


@pytest.mark.asyncio
async def test_agent_executor_one_part_input_with_message_metadata() -> None:
    msg = AIMessage(content=LLM_RESPONSE)
    llm = FakeMessagesListChatModel(responses=[msg])
    inference = LangChainModelInference(llm)

    executor = NextGenUIAgentExecutor(inference=inference, config=AgentConfig())

    message = Message(
        role=Role.user,
        parts=[
            Part(
                root=TextPart(
                    text="Tell me details about Toy Story",
                )
            ),
        ],
        message_id=str(uuid4()),
        metadata={
            "data": movies_data_obj,  # intentionally without type
        },
    )

    context = await SimpleRequestContextBuilder().build(
        params=MessageSendParams(message=message)
    )

    event_queue = EventQueue()
    await executor.execute(context, event_queue)

    event = await event_queue.dequeue_event(no_wait=True)
    assert isinstance(event, Message)
    assert len(event.parts) == 2

    assert isinstance(event.parts[0].root, TextPart)
    assert event.parts[0].root.text.startswith("Component is rendered in UI.")
    assert "title: 'Toy Story Details'" in event.parts[0].root.text
    assert "component_type: one-card" in event.parts[0].root.text

    assert isinstance(event.parts[1].root, DataPart)
    ui_block = UIBlock.model_validate(event.parts[1].root.data)
    assert ui_block.configuration is not None
    assert ui_block.configuration.data_type is None
    assert ui_block.configuration.component_metadata is not None
    assert "one-card" == ui_block.configuration.component_metadata.component
    assert ui_block.rendering is not None
    c = ComponentDataOneCard.model_validate_json(ui_block.rendering.content)
    assert "one-card" == c.component
    assert "Toy Story Details" == c.title


@pytest.mark.asyncio
async def test_error_when_no_message_provided() -> None:
    """Executor should raise InvalidParamsError when context.message is None."""
    msg = AIMessage(content=LLM_RESPONSE)
    llm = FakeMessagesListChatModel(responses=[msg])
    inference = LangChainModelInference(llm)
    executor = NextGenUIAgentExecutor(inference=inference, config=AgentConfig())

    class DummyContext:
        def __init__(self) -> None:
            self.message = None
            self.metadata = None

    context = DummyContext()
    event_queue = EventQueue()
    with pytest.raises(ServerError, match="No message provided"):
        await executor.execute(context, event_queue)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_error_when_no_input_data() -> None:
    """Executor should raise InvalidParamsError when there are no inputs gathered."""
    msg = AIMessage(content=LLM_RESPONSE)
    llm = FakeMessagesListChatModel(responses=[msg])
    inference = LangChainModelInference(llm)
    executor = NextGenUIAgentExecutor(inference=inference, config=AgentConfig())

    message = Message(role=Role.user, parts=[], message_id=str(uuid4()))
    context = await SimpleRequestContextBuilder().build(
        params=MessageSendParams(message=message)
    )
    event_queue = EventQueue()
    with pytest.raises(
        ServerError,
        match="No input data gathered from either Message metadata or TextPart metadata or DataPart",
    ):
        await executor.execute(context, event_queue)


@pytest.mark.asyncio
async def test_invalid_json_in_metadata_records_failure() -> None:
    """Malformed JSON in metadata should be recorded as a failure and included in summary."""
    msg = AIMessage(content=LLM_RESPONSE)
    llm = FakeMessagesListChatModel(responses=[msg])
    inference = LangChainModelInference(llm)
    executor = NextGenUIAgentExecutor(inference=inference, config=AgentConfig())

    message = Message(
        role=Role.user,
        parts=[
            Part(
                root=TextPart(
                    text="Generate UI (bad json)",
                    metadata={"data": "{not: json}", "type": "search_movie"},
                )
            ),
        ],
        message_id=str(uuid4()),
    )
    context = await SimpleRequestContextBuilder().build(
        params=MessageSendParams(message=message)
    )
    event_queue = EventQueue()
    await executor.execute(context, event_queue)

    # Drain events and check final summary
    from asyncio import QueueEmpty

    events = []
    while True:
        try:
            events.append(await event_queue.dequeue_event(no_wait=True))
        except QueueEmpty:
            break
    assert len(events) >= 1
    summary = events[-1]
    assert isinstance(summary, Message)
    assert isinstance(summary.parts[0].root, TextPart)
    txt = summary.parts[0].root.text
    assert "Successfully generated 0" in txt
    assert "Failed: 1" in txt
    assert "Failed component generation:" in txt
    assert "Invalid JSON format" in txt


@pytest.mark.asyncio
async def test_success_only_summary_failed_zero() -> None:
    """When there is only a valid input, final summary should report Failed: 0."""
    msg = AIMessage(content=LLM_RESPONSE)
    llm = FakeMessagesListChatModel(responses=[msg])
    inference = LangChainModelInference(llm)
    executor = NextGenUIAgentExecutor(inference=inference, config=AgentConfig())

    message = Message(
        role=Role.user,
        parts=[
            Part(
                root=TextPart(
                    text="Generate UI",
                    metadata={"data": movies_data_obj, "type": "search_movie"},
                )
            )
        ],
        message_id=str(uuid4()),
    )
    context = await SimpleRequestContextBuilder().build(
        params=MessageSendParams(message=message)
    )
    event_queue = EventQueue()
    await executor.execute(context, event_queue)

    # Drain events and check final summary
    from asyncio import QueueEmpty

    events = []
    while True:
        try:
            events.append(await event_queue.dequeue_event(no_wait=True))
        except QueueEmpty:
            break
    assert len(events) >= 1
    summary = events[-1]
    assert isinstance(summary, Message)
    assert isinstance(summary.parts[0].root, TextPart)
    txt = summary.parts[0].root.text
    assert "Successfully generated 1" in txt
    assert "Failed: 0" in txt


@pytest.mark.asyncio
async def test_agent_executor_summary_includes_failures(monkeypatch) -> None:
    # Arrange: model + executor
    msg = AIMessage(content=LLM_RESPONSE)
    llm = FakeMessagesListChatModel(responses=[msg])
    inference = LangChainModelInference(llm)
    executor = NextGenUIAgentExecutor(inference=inference, config=AgentConfig())

    # Patch: fail deterministically on the second call (patch the class method)
    original_select = type(executor.ngui_agent).select_component
    call_counter = {"n": 0}

    async def fail_on_second(self, *, user_prompt: str, input_data):
        call_counter["n"] += 1
        if call_counter["n"] == 2:
            raise Exception("forced fail for test")
        return await original_select(
            self, user_prompt=user_prompt, input_data=input_data
        )

    monkeypatch.setattr(
        type(executor.ngui_agent), "select_component", fail_on_second, raising=False
    )

    # Two inputs
    good = {"movie": {"title": "Toy Story"}}
    bad = {"movie": {"title": "Toy Story 2"}}

    message = Message(
        role=Role.user,
        parts=[
            Part(root=TextPart(text="Tell me details about Toy Story")),
            Part(root=DataPart(data=good)),
            Part(root=DataPart(data=bad)),
        ],
        message_id=str(uuid4()),
    )

    context = await SimpleRequestContextBuilder().build(
        params=MessageSendParams(message=message)
    )

    # Act
    event_queue = EventQueue()
    await executor.execute(context, event_queue)

    # Drain all events; EventQueue raises asyncio.QueueEmpty when empty
    from asyncio import QueueEmpty

    events = []
    while True:
        try:
            ev = await event_queue.dequeue_event(no_wait=True)
            events.append(ev)
        except QueueEmpty:
            break

    # Assert: final event is the summary with one failure recorded
    assert len(events) >= 1
    final = events[-1]
    assert isinstance(final, Message)
    assert len(final.parts) >= 1
    assert isinstance(final.parts[0].root, TextPart)
    txt = final.parts[0].root.text
    assert "Successfully generated" in txt
    assert "Failed: 1" in txt
    assert "Failed component generation:" in txt
    assert "forced fail for test" in txt


@pytest.mark.asyncio
async def test_agent_executor_two_parts_input() -> None:
    msg = AIMessage(content=LLM_RESPONSE)
    llm = FakeMessagesListChatModel(responses=[msg])
    inference = LangChainModelInference(llm)

    executor = NextGenUIAgentExecutor(inference=inference, config=AgentConfig())

    message = Message(
        role=Role.user,
        parts=[
            Part(
                root=TextPart(
                    text="Tell me details about Toy Story",
                )
            ),
            Part(
                root=DataPart(
                    data=movies_data_obj,
                    metadata={
                        "type": "search_detail",
                    },
                )
            ),
        ],
        message_id=str(uuid4()),
    )

    context = await SimpleRequestContextBuilder().build(
        params=MessageSendParams(message=message)
    )

    event_queue = EventQueue()
    await executor.execute(context, event_queue)

    event = await event_queue.dequeue_event(no_wait=True)
    assert isinstance(event, Message)
    assert len(event.parts) == 2

    assert isinstance(event.parts[0].root, TextPart)
    assert event.parts[0].root.text.startswith("Component is rendered in UI.")
    assert "title: 'Toy Story Details'" in event.parts[0].root.text
    assert "component_type: one-card" in event.parts[0].root.text

    assert isinstance(event.parts[1].root, DataPart)
    ui_block = UIBlock.model_validate(event.parts[1].root.data)
    assert ui_block.configuration is not None
    assert ui_block.configuration.data_type == "search_detail"
    assert ui_block.configuration.component_metadata is not None
    assert "one-card" == ui_block.configuration.component_metadata.component
    assert ui_block.rendering is not None
    c = ComponentDataOneCard.model_validate_json(ui_block.rendering.content)
    assert "one-card" == c.component
    assert "Toy Story Details" == c.title
