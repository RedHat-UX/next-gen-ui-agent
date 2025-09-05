# Next Gen UI Llama Stack Agent

Module category: `AI framework`  
Module status: `Supported`

Support for [Llama Stack](https://github.com/meta-llama/llama-stack).

Provides:

* `NextGenUILlamaStackAgent` - takes all tool messages from provided conversation turn steps (Llama Stack Agent API), and process data from them into UI components.
* `LlamaStackAgentInference` and `LlamaStackAsyncAgentInference` to use LLM hosted in Llama Stack server (Llama Stack Chat Completion API)

Tool name is used as `InputData.type` for each tool message, so can be used for [Hand Build Component](../../docs/guide/hand_build_components.md) selection based on mapping in UI Agent's configuration.

## Installation

```sh
pip install -U next_gen_ui_llama_stack
```

## Example

### Integrate Next Gen UI with your assistent

Let's have your ReAct Agent e.g. Movies agent like this:

```py
from llama_stack_client.lib.agents.react.agent import ReActAgent

client = LlamaStackClient(
    base_url=f"http://{LLAMA_STACK_HOST}:{LLAMA_STACK_PORT}",
)
INFERENCE_MODEL = "meta-llama/Llama-3.2-3B-Instruct"
movies_agent = ReActAgent(
    client=client,
    model=INFERENCE_MODEL,
    client_tools=[
        movies,
    ],
    json_response_format=True,
)

session_id = movies_agent.create_session("test-session")

# Send a query to your agent
response = movies_agent.create_turn(
    messages=[{"role": "user", "content": user_input}],
    session_id=session_id,
    stream=False,
)
```

Use `NextGenUILlamaStackAgent` class and just pass llama stack client and model name and 
pass steps from your movies agent to Next Gen UI Agent.

```py
from next_gen_ui_llama_stack import NextGenUILlamaStackAgent

# Pass steps to Next Gen UI Agent
ngui_agent = NextGenUILlamaStackAgent(client, INFERENCE_MODEL)
result = await ngui_agent.turn_from_steps(user_input, steps=response.steps)
```
