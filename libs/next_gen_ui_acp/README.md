# Next Gen UI ACP Server

Module category: `AI Protocol`  
Module status: `Tech Preview`

Support for [Agent Communication Protocol (ACP)](https://agentcommunicationprotocol.dev/)

Provides:

* `NextGenUIACPAgent` - code for easy implementation of ACP server

## Installation

```sh
pip install -U next_gen_ui_acp
```

Additionally install AI framework support for interaction with inference e.g. `next_gen_ui_beeai` or any other.

```sh
pip install -U next_gen_ui_beeai
```

## Example

### ACP Server


```py
import logging
from collections.abc import AsyncGenerator

from acp_sdk import Artifact
from acp_sdk.models import Message
from acp_sdk.server import RunYield, RunYieldResume, Server

from next_gen_ui_acp import NextGenUIACPAgent
from next_gen_ui_beeai import BeeAIInference

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

server = Server()

agent = NextGenUIACPAgent(
    component_system="rhds",
    inference=BeeAIInference(model="ollama:llama3.2"),
)


@server.agent(name="next_gen_ui")
async def ngui_agent(
    input: list[Message],
) -> AsyncGenerator[RunYield, RunYieldResume]:
    try:
        parts = await agent.run(input)
        yield Message(parts=parts)

    except Exception as e:
        logger.exception("Error during ngui run")
        yield Message(parts=[Artifact(content=e, name="error", role="tool")])


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    server.run(port=8001)
```
