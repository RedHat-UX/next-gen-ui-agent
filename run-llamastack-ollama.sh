## https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/libs/next_gen_ui_llama_stack/examples/LLAMASTACK_DEV.md
## https://llama-stack.readthedocs.io/en/latest/distributions/self_hosted_distro/ollama.html#via-docker

#export OLLAMA_MODEL=llama3.2:latest
export OLLAMA_MODEL=granite3.1-dense:2b

export LLAMASTACK_VERSION=0.1.9
#export LLAMASTACK_VERSION=latest
#export LLAMASTACK_VERSION=0.2.1

# create directory for LlamaStack persistence if is doesn't exist
mkdir -p ~/.llama

echo "Starting Ollama model $OLLAMA_MODEL..."

ollama run $OLLAMA_MODEL "/bye"

echo "Starting LlamaStack $LLAMASTACK_VERSION container..."

podman run -it --rm \
  -p 5001:5001 \
  -v ~/.llama:/root/.llama:z \
  llamastack/distribution-ollama:$LLAMASTACK_VERSION \
  --port 5001 \
  --env INFERENCE_MODEL=$OLLAMA_MODEL \
  --env OLLAMA_URL=http://host.containers.internal:11434

