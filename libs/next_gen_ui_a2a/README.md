# Next Gen UI A2A Server

This module is part of the [Next Gen UI Agent project](https://github.com/RedHat-UX/next-gen-ui-agent).

[![Module Category](https://img.shields.io/badge/Module%20Category-AI%20Protocol-red)](https://github.com/RedHat-UX/next-gen-ui-agent)
[![Module Status](https://img.shields.io/badge/Module%20Status-Tech%20Preview-orange)](https://github.com/RedHat-UX/next-gen-ui-agent)

[A2A Protocol](https://a2a-protocol.org/) provides standard how to communicate with AI agents
and provides interoparability by client SDKs in different languages. 
Use any A2A client implemntation to interact with the UI agent via A2A protocol.
For details see [expected inputs and returned outputs](#agent-inputs-and-outputs).

## Provides

* `NextGenUIAgentExecutor` - standard [A2A SDK AgentExecutor implementation](https://github.com/a2aproject/a2a-python) to expose the Next Gen UI Agent functionality
* `__main__.py` to run standalone A2A server


## Installation

**Note:** alternatively, you can use [container image](https://redhat-ux.github.io/next-gen-ui-agent/guide/ai_apps_binding/a2a-container/) to easily install and run the server.


```sh
pip install -U next_gen_ui_a2a
```

To run the standalone server using `__main__.py`, you also have to install http framework, eg:

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
You can choose `openai` or `anthropic-vertexai` inference provider.
You have to add the necessary dependencies to your python environment to do so, otherwise the application will complain about them missing.
See detailed documentation below.

Similarly pluggable component systems such as `rhds` also require certain imports, `next_gen_ui_rhds_renderer` in this particular case. 
`json` renderrer is installed by default.

### Configuration Reference

Server can be configured using commandline arguments, or environment variables. CLI has precedence over env variable.

| Commandline Argument          | Environment Variable              | Default Value | Description                                                                                                                           |
| ----------------------------- | --------------------------------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `--config-path`               | `NGUI_CONFIG_PATH`                | -             | Path to [YAML configuration files](#yaml-configuration) (to merge more yaml files, multiple commandline args can be used/comma separated in env variable). |
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

#### Provider **`openai`**

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

#### Provider **`anthropic-vertexai`**

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

### YAML configuration

Common [Next Gen UI YAML configuration files](https://redhat-ux.github.io/next-gen-ui-agent/guide/configuration/) can be used to configure UI Agent functionality.

Configuration file extension is available to provide ability to fine-tune details in 
the [A2A Agent Card and Skills](https://a2a-protocol.org/latest/tutorials/python/3-agent-skills-and-card/) 
to get better performance in your A2A system.
For details [see `a2a` field in the Schema Definition](https://redhat-ux.github.io/next-gen-ui-agent/spec/a2a/#agent-configuration).

Examle of the a2a yaml configuration extension:

```yaml
a2a:
  agent_card:
    name: UI component agent
    description: This agent processes user prompt nd related structured data to generate the best UI component to visualize them
  skills:
    generate_ui_components:
      name: Generate UI components to visualize data
      tags:
      - ui
      - frontend

# other UI Agent configurations

```

### Running Server locally from Git Repo

If you are running this from inside of our [NextGenUI Agent GitHub repo](https://github.com/RedHat-UX/next-gen-ui-agent) then our `pants` repository manager can help you satisfy all dependencies. 
In such case you can run the commands in the following way:

```bash
# Run directly
PYTHONPATH=./libs python libs/next_gen_ui_a2a -h
```

Run it with real config arguments or env variables.

### Example A2A client

See [A2A client example code](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/libs/next_gen_ui_a2a/readme_example.py).

## Agent inputs and outputs

**TODO** define expected agent input and structure of the output


## Links

* [Documentation](https://redhat-ux.github.io/next-gen-ui-agent/guide/ai_apps_binding/a2a-library/)
* [Source Codes](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs/next_gen_ui_a2a)
* [Contributing](https://redhat-ux.github.io/next-gen-ui-agent/development/contributing/)
