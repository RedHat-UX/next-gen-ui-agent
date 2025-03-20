import asyncio
import json
import logging

import pytest
from llama_stack_client import LlamaStackClient
from llama_stack_client.types.inference_step import InferenceStep
from llama_stack_client.types.tool_execution_step import ToolExecutionStep
from next_gen_ui_agent.types import UIComponentMetadata
from next_gen_ui_llama_stack import NextGenUILlamaStackAgent
from next_gen_ui_testing.data_set_movies import find_movie
from next_gen_ui_testing.model import MockedInference

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
            "content": json.dumps(movies_data),
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


@pytest.mark.asyncio
async def test_agent_turn_from_steps() -> None:
    mocked_component: UIComponentMetadata = {
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

    mocked_inference = MockedInference(mocked_component)
    client = LlamaStackClient()
    ngui_agent = NextGenUILlamaStackAgent(
        client, "not-used", inference=mocked_inference
    )

    async for ng_event in ngui_agent.create_turn(
        user_input, steps=[step1, step2, step3]
    ):
        if ng_event["event_type"] == "component_metadata":
            logging.info("Result: %s", ng_event["payload"])
            assert ng_event["payload"][0]["component"] == "one-card"


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    asyncio.run(test_agent_turn_from_steps())
