import asyncio
import logging
import pprint

from llama_stack_client import LlamaStackClient
from llama_stack_client.lib.agents.client_tool import client_tool
from llama_stack_client.lib.agents.react.agent import ReActAgent
from next_gen_ui_llama_stack import NextGenUILlamaStackAgent
from next_gen_ui_testing.data_set_movies import find_movie

user_input = "Tell me brief details of Toy Story"
# user_input = "Play Toy Story trailer"
# user_input = "Get me the poster for movie Toy Story"

LLAMA_STACK_HOST = "127.0.0.1"
LLAMA_STACK_PORT = 5001
# INFERENCE_MODEL = "granite3.1-dense:2b"
INFERENCE_MODEL = "llama3.2:latest"

client = LlamaStackClient(
    base_url=f"http://{LLAMA_STACK_HOST}:{LLAMA_STACK_PORT}",
)


# Movies Agent
@client_tool
def movies(title: str):
    """Get details of movie.

    :param title: movie title e.g. Toy Story
    :returns: detail about movie
    """
    logging.debug("Get movie, title: %s", title)
    response = find_movie(title)
    logging.debug("returning: %s", response)
    return response


movies_agent = ReActAgent(
    client=client,
    model=INFERENCE_MODEL,
    tools=[movies],
    json_response_format=True,
)

# Next Gen UI Agent
ngui_agent = NextGenUILlamaStackAgent(client, INFERENCE_MODEL)


async def run_movies_agent():
    print(f"------MOVIES Assistent, prompt='{user_input}'")
    session_id = movies_agent.create_session("test-session")

    # Send a query to the AI agent to get a movie
    response = movies_agent.create_turn(
        messages=[{"role": "user", "content": user_input}],
        session_id=session_id,
        stream=False,
    )

    # No Stream way, when stream=False,
    for step in response.steps:
        print(f"\n\n------MOVIES Agent step_type={step.step_type}")
        pprint.pp(step.model_dump(), width=120)

        if step.step_type == "tool_execution":
            async for ngui_event in ngui_agent.create_turn(user_input, steps=[step]):
                print(f"\n\n------NGUI Agent event_type={ngui_event['event_type']}")
                pprint.pp(ngui_event["payload"], width=120)

    # Stream way, when stream=True,
    # for chunk in response:
    #     payload = chunk.event.payload
    #     if payload.event_type == "step_complete":
    #         step = payload.step_details
    #         print(f"\n\n-------MOVIES Agent step_type={step.step_type}")
    #         if step.step_type == "tool_execution":
    #             pprint.pp(json.loads(step.tool_responses[0].content))
    #             async for ng_agent_event in ngui_agent.create_turn(user_input, steps=[step]):
    #                 print(f"\n\n-------NGUI Agent event_type={ng_agent_event['event_type']}")
    #                 pprint.pp(ng_agent_event["payload"], width=120)
    #         if step.step_type == "inference":
    #             pprint.pp(step.api_model_response.content, width=120)

    # from llama_stack_client.lib.agents.event_logger import EventLogger
    # for log in EventLogger().log(response):
    #     log.print()


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    asyncio.run(run_movies_agent())
