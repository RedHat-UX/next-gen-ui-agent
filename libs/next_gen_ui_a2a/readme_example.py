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

    # --8<-- [start:A2ACardResolver]

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
