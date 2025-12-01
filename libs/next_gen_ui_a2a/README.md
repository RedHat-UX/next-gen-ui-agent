# Next Gen UI Agent A2A Protocol Integration (Dev Preview)

[![Module Category](https://img.shields.io/badge/Module%20Category-AI%20Protocol-red)](https://github.com/RedHat-UX/next-gen-ui-agent)
[![Module Status](https://img.shields.io/badge/Module%20Status-Dev%20Preview-yellow)](https://github.com/RedHat-UX/next-gen-ui-agent)

[A2A Protocol](https://a2a-protocol.org/) provides standard how to communicate with agent
and provides interoparability by client SDKs in different languages.

## Provides

1. Standard A2A API to the Next Gen UI agent
2. HTTP Server to run the A2A API and execute the agent
3. Docker image

To interact with agent via A2A protocol use any A2A client implemntation.

## Installation

```sh
pip install -U next_gen_ui_a2a
```

## Example

TODO: NGUI-493 - Improve documentation. Move code examples to docs. Keep README minimal.

### Run A2A server with Next Gen UI agent

```py
import uvicorn 
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler 
from a2a.server.tasks import InMemoryTaskStore 
from langchain_openai import ChatOpenAI 

from next_gen_ui_a2a.agent_card import card
from next_gen_ui_a2a.agent_executor import NextGenUIAgentExecutor
from next_gen_ui_agent.model import LangChainModelInference
from next_gen_ui_agent.types import AgentConfig

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "ollama"
model = os.getenv("INFERENCE_MODEL", "llama3.2")
base_url = os.getenv("OPEN_API_URL", "http://localhost:11434/v1")

# Create Chat API used by next_gen_ui agent
llm = ChatOpenAI(model=model, base_url=base_url)
inference = LangChainModelInference(llm)
config = AgentConfig(inference=inference)

request_handler = DefaultRequestHandler(
    agent_executor=NextGenUIAgentExecutor(config),
    task_store=InMemoryTaskStore(),
)

server = A2AStarletteApplication(
    agent_card=card,
    http_handler=request_handler,
)

uvicorn.run(server.build(), host="0.0.0.0", port=9999)
```

### Run A2A client

```py
import logging
from uuid import uuid4

import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (  # SendStreamingMessageRequest,
    AgentCard,
    Message,
    MessageSendParams,
    Part,
    Role,
    SendMessageRequest,
    TextPart,
)
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH


async def main() -> None:
    # Configure logging to show INFO level messages
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)  # Get a logger instance

    base_url = "http://localhost:9999"

    async with httpx.AsyncClient(timeout=120) as httpx_client:
        # Initialize A2ACardResolver
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
            # agent_card_path uses default, extended_agent_card_path also uses default
        )

        # Fetch Public Agent Card and Initialize Client
        final_agent_card_to_use: AgentCard | None = None

        try:
            logger.info(
                f"Attempting to fetch public agent card from: {base_url}{AGENT_CARD_WELL_KNOWN_PATH}"
            )
            _public_card = (
                await resolver.get_agent_card()
            )  # Fetches from default public path
            logger.info("Successfully fetched public agent card:")
            logger.info(_public_card.model_dump_json(indent=2, exclude_none=True))
            final_agent_card_to_use = _public_card
            logger.info(
                "\nUsing PUBLIC agent card for client initialization (default)."
            )

        except Exception as e:
            logger.exception("Critical error fetching public agent card")
            raise RuntimeError(
                "Failed to fetch the public agent card. Cannot continue."
            ) from e

        client = A2AClient(
            httpx_client=httpx_client,
            agent_card=final_agent_card_to_use,
        )
        logger.info("A2AClient initialized.")

        movies_data = {
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

        message = Message(
            role=Role.user,
            parts=[
                Part(
                    root=TextPart(
                        text="Tell me details about Toy Story",
                        metadata={
                            "data": movies_data,
                            "type": "search_movie",
                        },
                    )
                ),
                # Part(root=DataPart(data=movies_data)),
            ],
            message_id=str(uuid4()),
        )
        request = SendMessageRequest(
            id=str(uuid4()), params=MessageSendParams(message=message)
        )

        response = await client.send_message(request)
        logger.info("Execution finished.")
        print(response.model_dump(mode="json", exclude_none=True))

        # streaming_request = SendStreamingMessageRequest(
        #     id=str(uuid4()), params=MessageSendParams(message=message)
        # )
        # stream_response = client.send_message_streaming(streaming_request)
        # async for chunk in stream_response:
        #     print(chunk.model_dump(mode="json", exclude_none=True))


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
```
