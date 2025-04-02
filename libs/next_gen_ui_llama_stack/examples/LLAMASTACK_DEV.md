# Llama Stack Local Server Development

## Run Llama Stack

Install [Ollama](https://ollama.com/download) and make sure it is running.

Run model for the first time to download/install it into the local Ollama server.

```sh
ollama run llama3.2:latest
```

Tested models: `granite3.1-dense:2b` or `llama3.2:latest`

Create empty `~/.llama` directory first, if it doesn't exist on your filesystem. It is used to persist LlamaStack platform data (configuration, etc).

Ollama model must be running during the LlamaStack startup, so you have to run it shortly before each LlamaStack start, or run it with `-keepalive` in another terminal.

```sh
ollama run llama3.2:latest --keepalive 60m 
```

Start [LlamaStack Ollama distribution](https://llama-stack.readthedocs.io/en/latest/distributions/self_hosted_distro/ollama.html#ollama-distribution) container.

```sh
podman run -it --rm \
  -p 5001:5001 \
  -v ~/.llama:/root/.llama:z \
  llamastack/distribution-ollama:latest \
  --port 5001 \
  --env INFERENCE_MODEL="llama3.2:latest" \
  --env OLLAMA_URL=http://host.containers.internal:11434
```
**Notes:** 
* `:z` qualifier on `/root/.llama` volume mount in necessary for Fedora Linux
* use `--env INFERENCE_MODEL="granite3.1-dense:2b" \` to add this model into your LlamaStack instance

Output:

```sh
INFO 2025-03-14 08:10:46,174 llama_stack.providers.remote.inference.ollama.ollama:74: checking connectivity to Ollama at `http://host.containers.internal:11434`...
INFO 2025-03-14 08:10:46,453 httpx:1740: HTTP Request: GET http://host.containers.internal:11434/api/ps "HTTP/1.1 200 OK"
...
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     ASGI 'lifespan' protocol appears unsupported.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://['::', '0.0.0.0']:5001 (Press CTRL+C to quit)
```

You can use `run-llamastack-ollama.sh` script found in this directory which performs described steps to run LLamaStack.

## Running Examples

Navigate to selected example.py file in VS code.

In VSCode switch to `Run and Debug` view and hit `Python Debugger: Current File` (`Run` on top right of the `*.py` file doesn't work)