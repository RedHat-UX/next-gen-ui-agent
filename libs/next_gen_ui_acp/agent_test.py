import json

import pytest
from acp_sdk import Artifact, Message, MessagePart
from next_gen_ui_acp.agent import NextGenUIACPAgent
from next_gen_ui_agent.types import UIComponentMetadata
from next_gen_ui_testing.data_set_movies import find_movie
from next_gen_ui_testing.model import MockedInference

user_input = "Tell me brief details of Toy Story"
user_message = Message(
    parts=[MessagePart.model_validate({"content": user_input, "role": "user"})]
)

movies_data = find_movie("Toy Story")
tool_message = Message(
    parts=[
        Artifact.model_validate(
            {
                "content": json.dumps(movies_data, default=str),
                "name": "tool_output",
                "role": "tool",
                "id": "test_id",
            }
        )
    ]
)


@pytest.mark.asyncio
async def test_agent_run() -> None:
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
    response = await ngui_agent.run(input=[user_message, tool_message])
    artifact = response[0]
    assert artifact.name == "rendering"
    assert '"data":[1995]' in str(artifact.content)
