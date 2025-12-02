# Next Gen UI A2A Server

[![Module Category](https://img.shields.io/badge/Module%20Category-AI%20Protocol-red)](https://github.com/RedHat-UX/next-gen-ui-agent)
[![Module Status](https://img.shields.io/badge/Module%20Status-Tech%20Preview-orange)](https://github.com/RedHat-UX/next-gen-ui-agent)

[A2A Protocol](https://a2a-protocol.org/) provides standard how to communicate with agent
and provides interoparability by client SDKs in different languages.

## Provides

* `__main__.py` to run the MCP server as the standalone server
* `NextGenUIAgentExecutor` - standard A2A API to the Next Gen UI agent

To interact with agent via A2A protocol use any A2A client implemntation.

## Installation

```sh
pip install -U next_gen_ui_a2a
```

To run the server using `__main__.py`, you also have to install http framework, eg:

```sh
pip install a2a-sdk[http-server] uvicorn
```

Depending on your use case you may need additional packages for inference provider or design component renderers. More about this in the next sections.

## Usage

### Running the standalone server

To get help how to run the server and pass the arguments run it with `-h` parameter:

```sh
python -m next_gen_ui_a2a -h

```
### Configuration Reference

Server can be configured using commandline arguments, or environment variables. CLI has precedence over env variable.

| Commandline Argument          | Environment Variable              | Default Value | Description                                                                                                                           |
| ----------------------------- | --------------------------------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `--config-path`               | `NGUI_CONFIG_PATH`                | -             | Path to [Next Gen UI YAML configuration files](https://redhat-ux.github.io/next-gen-ui-agent/guide/configuration/) (to merge more yaml files, multiple commandline args can be used/comma separated in env variable). |
| `--component-system`          | `NGUI_COMPONENT_SYSTEM`           | `json`        | UI Component system (`json` + any installed). Overrides value from YAML config file if used.                                          |
| `--host`                      | `A2A_HOST`                        | `127.0.0.1`   | Host to bind to.                                                                                                                      |
| `--port`                      | `A2A_PORT`                        | `8000`        | Port to bind to.                                                                                                                      |
| `--provider`                  | `NGUI_PROVIDER`                   | `openai`      | LLM inference provider (`openai`, `anthropic-vertexai`), for details see below.                                                       |
| `--model`                     | `NGUI_MODEL`                      | -             | Model name. Required for `openai`, `anthropic-vertexai`.                                                                              |
| `--base-url`                  | `NGUI_PROVIDER_API_BASE_URL`      | -             | Base URL for API, provider specific defaults. Used by `openai`, `anthropic-vertexai`.                                                 |
| `--api-key`                   | `NGUI_PROVIDER_API_KEY`           | -             | API key for the LLM provider. Used by `openai`, `anthropic-vertexai`.                                                                 |
| `--temperature`               | `NGUI_PROVIDER_TEMPERATURE`       | -             | Temperature for model inference, float value (defaults to `0.0` for deterministic responses). Used by `openai`, `anthropic-vertexai`. |
| `--sampling-max-tokens`       | `NGUI_SAMPLING_MAX_TOKENS`        | -             | Maximum LLM generated tokens, integer value. Used by `anthropic-vertexai` (defaults to `4096`).                                       |
| `--anthropic-version`         | `NGUI_PROVIDER_ANTHROPIC_VERSION` | -             | Anthropic version value used in the API call (defaults to `vertex-2023-10-16`). Used by `anthropic-vertexai`.                         |
| `--debug`                     | -                                 |               | Enable debug logging.                                                                                                                 |

### LLM Inference Providers

The Next Gen UI A2A server supports multiple inference providers, controlled by the `--provider` commandline argument / `NGUI_PROVIDER` environment variable:

#### Provider **`openai`**:

Uses [LangChain OpenAI inference provider](https://redhat-ux.github.io/next-gen-ui-agent/guide/ai_apps_binding/pythonlib/#provides), 
so can be used with any OpenAI compatible APIs, eg. OpenAI API itself,
or [Ollama](https://ollama.com/) for localhost inference,
or [Llama Stack server v0.3.0+](https://llamastack.github.io/docs/api/create-chat-completions).

Requires additional package to be installed:

```sh
"pip install langchain-openai"
```

Requires:

- `NGUI_MODEL`: Model name (e.g., `gpt-4o`, `llama3.2`).
- `NGUI_PROVIDER_API_KEY`: API key for the provider.
- `NGUI_PROVIDER_API_BASE_URL` (optional): Custom base URL for OpenAI-compatible APIs like Ollama or Llama Stack. OpenAI API by default.
- `NGUI_PROVIDER_TEMPERATURE` (optional): Temperature for model inference (defaults to `0.0` for deterministic responses).

Base URL examples:

- OpenAI: `https://api.openai.com/v1` (default)
- Ollama at localhost: `http://localhost:11434/v1`
- Llama Stack server at localhost port `5001` called from MCP server running in image: `http://host.containers.internal:5001/v1`

#### Provider **`anthropic-vertexai`**:

Uses [Anthropic/Claude models from proxied Google Vertex AI API endpoint](https://redhat-ux.github.io/next-gen-ui-agent/guide/ai_apps_binding/pythonlib/#provides).

Called API url is constructed as `{BASE_URL}/models/{MODEL}:streamRawPredict`. 
API key is sent as `Bearer` token in `Authorization` http request header.

Requires:

  - `NGUI_MODEL`: Model name.
  - `NGUI_PROVIDER_API_BASE_URL`: Base URL of the API.
  - `NGUI_PROVIDER_API_KEY`: API key for the provider.
  - `NGUI_PROVIDER_TEMPERATURE` (optional): Temperature for model inference (defaults to `0.0` for deterministic responses).
  - `NGUI_PROVIDER_ANTHROPIC_VERSION` (optional): Anthropic version to use in API call (defaults to `vertex-2023-10-16`).
  - `NGUI_SAMPLING_MAX_TOKENS` (optional): Maximum LLM generated tokens, integer value (defaults to `4096`).

### Running Server locally from Git Repo

If you are running this from inside of our [NextGenUI Agent GitHub repo](https://github.com/RedHat-UX/next-gen-ui-agent) then our `pants` repository manager can help you satisfy all dependencies. 
In such case you can run the commands in the following way:

```bash
  # Run directly
  PYTHONPATH=./libs python libs/next_gen_ui_a2a -h
```

Run with real config arguments or env variables.

### Example A2A client

Example A2A client to call Next Gen UI A2A server

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
## Links

* [Documentation](https://redhat-ux.github.io/next-gen-ui-agent/guide/ai_apps_binding/a2a-library/)
* [Source Codes](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs/next_gen_ui_a2a)
* [Contributing](https://redhat-ux.github.io/next-gen-ui-agent/development/contributing/)
