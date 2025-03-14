import asyncio
import json

import pytest
from llama_stack_client import LlamaStackClient
from llama_stack_client.lib.agents.client_tool import client_tool
from llama_stack_client.lib.agents.react.agent import ReActAgent
from llama_stack_client.types.inference_step import InferenceStep
from llama_stack_client.types.tool_execution_step import ToolExecutionStep

from . import NextGenUILlamaStackAgent

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

step2_ToolExecutionStep = """
{
  "step_id": "fc929422-49f7-4d2c-a81f-53f4e426e606",
  "step_type": "tool_execution",
  "tool_calls": [],
  "tool_responses": [
    {
      "call_id": "5d4e9535-d791-432e-828b-44596296847d",
      "content": "\\"\\\\n    [\\\\n    {\\\\n        \\\\\\"movie\\\\\\":{\\\\n        \\\\\\"languages\\\\\\":[\\\\n            \\\\\\"English\\\\\\"\\\\n        ],\\\\n        \\\\\\"year\\\\\\":1995,\\\\n        \\\\\\"imdbId\\\\\\":\\\\\\"0114709\\\\\\",\\\\n        \\\\\\"runtime\\\\\\":81,\\\\n        \\\\\\"imdbRating\\\\\\":8.3,\\\\n        \\\\\\"movieId\\\\\\":\\\\\\"1\\\\\\",\\\\n        \\\\\\"countries\\\\\\":[\\\\n            \\\\\\"USA\\\\\\"\\\\n        ],\\\\n        \\\\\\"imdbVotes\\\\\\":591836,\\\\n        \\\\\\"title\\\\\\":\\\\\\"Toy Story\\\\\\",\\\\n        \\\\\\"url\\\\\\":\\\\\\"https://themoviedb.org/movie/862\\\\\\",\\\\n        \\\\\\"revenue\\\\\\":373554033,\\\\n        \\\\\\"tmdbId\\\\\\":\\\\\\"862\\\\\\",\\\\n        \\\\\\"plot\\\\\\":\\\\\\"A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room.\\\\\\",\\\\n        \\\\\\"posterUrl\\\\\\":\\\\\\"https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg\\\\\\",\\\\n        \\\\\\"released\\\\\\":\\\\\\"1995-11-22\\\\\\",\\\\n        \\\\\\"trailerUrl\\\\\\": \\\\\\"https://www.youtube.com/watch?v=v-PjgYDrg70\\\\\\",\\\\n        \\\\\\"budget\\\\\\":30000000\\\\n        },\\\\n        \\\\\\"actors\\\\\\":[\\\\n        \\\\\\"Jim Varney\\\\\\",\\\\n        \\\\\\"Tim Allen\\\\\\",\\\\n        \\\\\\"Tom Hanks\\\\\\",\\\\n        \\\\\\"Don Rickles\\\\\\"\\\\n        ]\\\\n    }\\\\n    ]\\\\n\\"",
      "tool_name": "movies",
      "metadata": null
    }
  ],
  "turn_id": "ce956552-1d35-45ac-850a-b44d61ed8c8c",
  "completed_at": "2025-03-14T10:52:14.939331Z",
  "started_at": "2025-03-14T10:52:14.939331Z"
}
"""
step2 = ToolExecutionStep(**json.loads(step2_ToolExecutionStep))

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

LLAMA_STACK_HOST = "127.0.0.1"
LLAMA_STACK_PORT = 5001
INFERENCE_MODEL = "meta-llama/Llama-3.2-3B-Instruct"


@pytest.mark.skip(reason="Mocked agent implemented needed")
@pytest.mark.asyncio
async def test_agent_turn_from_steps() -> None:
    client = LlamaStackClient(
        base_url=f"http://{LLAMA_STACK_HOST}:{LLAMA_STACK_PORT}",
    )
    ngui_agent = NextGenUILlamaStackAgent(client, INFERENCE_MODEL)
    steps = [step1, step2, step3]
    result = await ngui_agent.turn_from_steps(user_input, steps=steps)  # type: ignore
    print(result)
    assert result[0].component == "one-card"


@client_tool
def movies(title: str = "Toy Story") -> str:
    """Get details of movie.

    :param title: movie title e.g. Toy Story
    :returns: detail about movie
    """
    print("Get movie, title:", title)
    response = step2.tool_responses[0].content
    print("returning:", response)
    return str(response)


def run_movies_agent():
    client = LlamaStackClient(
        base_url=f"http://{LLAMA_STACK_HOST}:{LLAMA_STACK_PORT}",
    )
    movies_agent = ReActAgent(
        client=client,
        model=INFERENCE_MODEL,
        client_tools=[
            movies,
        ],
        json_response_format=True,
    )

    session_id = movies_agent.create_session("test-session")

    # Send a query to the AI agent to get a movie
    response = movies_agent.create_turn(
        messages=[{"role": "user", "content": user_input}],
        session_id=session_id,
        stream=False,
    )

    for step in response.steps:
        steps_dump = step.model_dump_json(indent=2).replace("\\", "\\\\")
        print(f"\nSTEP {type(step).__name__}:\n", steps_dump)


if __name__ == "__main__":
    # run_movies_agent()
    asyncio.run(test_agent_turn_from_steps())
