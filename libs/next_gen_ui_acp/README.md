# Next Gen UI ACP Server

This module is part of the [Next Gen UI Agent project](https://github.com/RedHat-UX/next-gen-ui-agent).

[![Module Category](https://img.shields.io/badge/Module%20Category-AI%20Protocol-red)](https://github.com/RedHat-UX/next-gen-ui-agent)
[![Module Status](https://img.shields.io/badge/Module%20Status-Deprecated-lightgray)](https://github.com/RedHat-UX/next-gen-ui-agent)

Support for [Agent Communication Protocol (ACP)](https://agentcommunicationprotocol.dev/)

**Important Note**: ACP is depracated and is now part of A2A under the Linux Foundation!

## Provides

* `NextGenUIACPAgent` - code for easy implementation of the ACP server
    * processes data from every message after latest `role=user` (including), from the first part if it contains `Artifact` or has `trajectory` metadata
    * `tool_name` from the `trajectory` metadata is used as UI Agent `InputData.type` if present
    * UI Agent `InputData.id` is randomly generted
    * processes data in parallel, yields `Message` for every processed piece of data, 
      with `role=agent` and one `Artifact` containing `trajectory` metadata with `tool_name=next_gen_ui_agent`:
        * success - Artifact with `name`=`ui_block` and `content_type`=`application/json` and serialized `UIBlock` as a `content`.
        * error - Artifact with `name`=`error` and `content_type`=`text/plain` and error message as a `content`.

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
   return agent.run(input)

if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    server.run(port=8001)
```

## Links

* [Documentation](https://redhat-ux.github.io/next-gen-ui-agent/guide/ai_apps_binding/acp/)
* [Source Codes](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs/next_gen_ui_acp)
* [Contributing](https://redhat-ux.github.io/next-gen-ui-agent/development/contributing/)
