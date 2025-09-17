## https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/libs/next_gen_ui_llama_stack/examples/LLAMASTACK_DEV.md
## https://llama-stack.readthedocs.io/en/latest/distributions/self_hosted_distro/ollama.html#via-docker

#export OLLAMA_MODEL=llama3.2:latest
export OLLAMA_MODEL=granite3.3:2b
#export OLLAMA_MODEL=granite3.3:8b

#export LLAMASTACK_VERSION=latest
export LLAMASTACK_VERSION=0.2.16

if [ -z "$INFERENCE_MODEL" ]; then
    echo INFERENCE_MODEL env variable not set, setting it to default value $OLLAMA_MODEL
    export INFERENCE_MODEL=$OLLAMA_MODEL
else
    echo Using existing INFERENCE_MODEL env variable
fi


# create directory for LlamaStack persistence if is doesn't exist
mkdir -p ~/.llama

echo "Starting Ollama model $INFERENCE_MODEL..."

ollama run $INFERENCE_MODEL "/bye"

echo "Starting LlamaStack $LLAMASTACK_VERSION container..."

podman run -it --rm \
  -p 5001:5001 \
  -v ~/.llama:/root/.llama:z \
  llamastack/distribution-starter:$LLAMASTACK_VERSION \
  --port 5001 \
  --env INFERENCE_MODEL=$INFERENCE_MODEL \
  --env OLLAMA_URL=http://host.containers.internal:11434

