import asyncio
import logging
import os

from llama_stack.core.library_client import (  # type: ignore[import-untyped]
    AsyncLlamaStackAsLibraryClient,
)
from llama_stack_client import LlamaStackClient
from next_gen_ui_agent.model import InferenceBase
from next_gen_ui_llama_stack.llama_stack_inference import (
    LlamaStackAgentInference,
    LlamaStackAsyncAgentInference,
)

logger = logging.getLogger(__name__)


class LlamaStackEmbeddedAsyncAgentInference(InferenceBase):
    """Class providing inference using embedded LlamaStack from wrapped AsyncLlamaStackAsLibraryClient and LlamaStackAsyncAgentInference"""

    def __init__(self, config_file: str, model: str):
        """
        Initialize LlamaStackAsyncAgentInferenceEmbedded.

        * `config_file` - path to LlamaStack config file to use for embedded LlamaStack
        * `model` - LLM model to use
        """
        super().__init__()
        self.model = model
        client_a = AsyncLlamaStackAsLibraryClient(config_file)
        asyncio.run(client_a.initialize())

        self.inference = LlamaStackAsyncAgentInference(client_a, model)

    async def call_model(self, system_msg: str, prompt: str) -> str:
        return await self.inference.call_model(system_msg, prompt)


LLAMA_STACK_PORT_DEFAULT = "5001"


def init_inference_from_env(
    default_model: str | None = None, default_config_file: str | None = None
) -> InferenceBase | None:
    """
    Initialize LlamaStack inference from environment variables.
    Either remote or embedded is created based on the provided environment variables.
    Returns `None` if neither remote nor embedded is configured.

    Parameters:
    * `default_model` - default model to use if `INFERENCE_MODEL` env variableis not set
    * `default_config_file` - default config file to use if `LLAMA_STACK_CONFIG_FILE` env variable is not set

    Environment variables:
    * `INFERENCE_MODEL` - LLM model to use - inference is not created if undefined
    * `LLAMA_STACK_HOST` - remote LlamaStack host - if defined then it is used with LLAMA_STACK_PORT to create remote LlamaStack inference
    * `LLAMA_STACK_PORT` - remote LlamaStack port - optional, defaults to `5001`
    * `LLAMA_STACK_URL` - remote LlamaStack url - if `LLAMA_STACK_HOST` is not defined, but this url is defined, then it is used to create remote LlamaStack inference
    * `LLAMA_STACK_CONFIG_FILE` - path to embedded LlamaStack config file, used only if no remote LlamaStack is configured
    """

    model = os.getenv("INFERENCE_MODEL", default_model)
    if not model:
        return None

    host = os.getenv("LLAMA_STACK_HOST")
    url = os.getenv("LLAMA_STACK_URL")
    if host or url:
        # use remote llama stack if host or url is configured
        if host:
            port = os.getenv("LLAMA_STACK_PORT", default=LLAMA_STACK_PORT_DEFAULT)
            base_url = f"http://{host}:{port}"
        elif url:
            base_url = url

        logger.info(
            "Creating UI Agent with remote LlamaStack host=%s and LLM=%s",
            base_url,
            model,
        )

        client = LlamaStackClient(
            base_url=base_url,
        )

        return LlamaStackAgentInference(client, model)

    else:
        config_file = os.getenv("LLAMA_STACK_CONFIG_FILE", default_config_file)

        if not config_file:
            return None

        logger.info(
            "Creating UI Agent with embedded LlamaStack config='%s' and LLM='%s'",
            config_file,
            model,
        )

        return LlamaStackEmbeddedAsyncAgentInference(config_file, model)
