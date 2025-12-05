from uuid import uuid4

import pytest
from a2a.server.agent_execution import SimpleRequestContextBuilder
from a2a.server.events import EventQueue
from a2a.types import DataPart, Message, MessageSendParams, Part, Role, TextPart
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
async def test_agent_executor_one_message_and_metadata() -> None:
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
    assert ui_block.configuration.component_metadata is not None
    assert "one-card" == ui_block.configuration.component_metadata.component
    assert ui_block.rendering is not None
    c = ComponentDataOneCard.model_validate_json(ui_block.rendering.content)
    assert "one-card" == c.component
    assert "Toy Story Details" == c.title


@pytest.mark.asyncio
async def test_agent_executor_two_messages() -> None:
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
            Part(root=DataPart(data=movies_data_obj)),
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
    assert ui_block.configuration.component_metadata is not None
    assert "one-card" == ui_block.configuration.component_metadata.component
    assert ui_block.rendering is not None
    c = ComponentDataOneCard.model_validate_json(ui_block.rendering.content)
    assert "one-card" == c.component
    assert "Toy Story Details" == c.title
