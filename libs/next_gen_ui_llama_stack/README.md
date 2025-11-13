# Next Gen UI Llama Stack Integration

This module is part of the [Next Gen UI Agent project](https://github.com/RedHat-UX/next-gen-ui-agent).

[![Module Category](https://img.shields.io/badge/Module%20Category-AI%20Framework-darkred)](https://github.com/RedHat-UX/next-gen-ui-agent)
[![Module Status](https://img.shields.io/badge/Module%20Status-Supported-green)](https://github.com/RedHat-UX/next-gen-ui-agent)

Support for [Llama Stack](https://github.com/meta-llama/llama-stack) framework.

## Provides

* `NextGenUILlamaStackAgent` - takes all tool messages from provided conversation turn steps (Llama Stack Agent API), and process data from them into UI components.
    * Tool name is used as `InputData.type` for the UI Agent, so [distinct configurations](https://redhat-ux.github.io/next-gen-ui-agent/guide/configuration/#data_types-dictstr-agentconfigdatatype-optional) 
      can be applied based on it, like input data transformations, defined UI components (dynamic ot Hand Build) etc.
    * Two event types can be emitted during the processing:
        * `success` with output from the UI Agent processing. Payload is array of `UIBlock`.
        * `error` with error from the UI Agent processing. Payload is `Exception`.
    * Depending on the agent's `execution_mode`, processing is performed as:
        * `stream`: Process individual data in parallel, yield each result as an independent event immediatelly as processing completes/fails.
          So overall number of produced events is the same as number of data pieces. Each `success` event contains exactly one `UIBlock` in the payload array. (default)
        * `batch`: Process individual data in parallel, yield all results as one event containing results for all the data, 
          or one `error` event if processing of any data fails.
* `LlamaStackAgentInference` and `LlamaStackAsyncAgentInference` to use LLM hosted in Llama Stack server (Llama Stack Chat Completion API)

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

# Pass steps to Next Gen UI Agent for processing. Events with results are emitted.
ngui_agent = NextGenUILlamaStackAgent(client, INFERENCE_MODEL)
result = await ngui_agent.create_turn(user_input, steps=response.steps)
```

## Links

* [Documentation](https://redhat-ux.github.io/next-gen-ui-agent/guide/ai_apps_binding/llamastack/)
* [Source Codes](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs/next_gen_ui_llama_stack)
* [Contributing](https://redhat-ux.github.io/next-gen-ui-agent/development/contributing/)
