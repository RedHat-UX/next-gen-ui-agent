# Llama Stack Local Server Development

## Run Llama Stack

Install [Ollama](https://ollama.com/download)

Run model for the first time to download/install it into local ollama.

Tested models: `granite3.1-dense:2b` or `llama3.2:latest`

Model must be running durin the LlamaStack startup (at least sometimes ;-), so you can run it with `-keepalive`.

```sh
ollama run llama3.2:latest --keepalive 60m 
```

Start [LlamaStack Ollama distribution](https://llama-stack.readthedocs.io/en/latest/distributions/self_hosted_distro/ollama.html#ollama-distribution)

Create empty `~/.llama` directory first, if it doesn't exist on your filesystem. It is used to store some LlamaStack platform data.

```sh
podman run -it --rm \
  -p 5001:5001 \
  -v ~/.llama:/root/.llama:z \
  llamastack/distribution-ollama:0.1.5.1 \
  --port 5001 \
  --env INFERENCE_MODEL="llama3.2:latest" \
  --env OLLAMA_URL=http://host.containers.internal:11434
```
**Notes:** 
* `:v` qualifier on `/root/.llama` volume mount in necessary for Fedora Linux!
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

## Run Example

Navigate to selected example.py
In VSCode switch to `Run and debug` view and hit `Python Debugger: Current File`