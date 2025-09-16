import asyncio
import os

from llama_stack_client import LlamaStackClient
from next_gen_ui_llama_stack.llama_stack_inference import LlamaStackAgentInference
from next_gen_ui_llama_stack_embedded import init_inference_from_env


def test_init_response_NOT_CONFIGURED() -> None:
    os.environ.clear()
    inference = init_inference_from_env()
    assert inference is None


def test_init_response_CONFIGURED_REMOTE_HOST() -> None:
    os.environ.clear()
    os.environ["INFERENCE_MODEL"] = "granite3.2:latest"
    os.environ["LLAMA_STACK_HOST"] = "localhost"
    inference = init_inference_from_env()
    assert inference is not None
    assert isinstance(inference, LlamaStackAgentInference)
    assert inference.model == "granite3.2:latest"
    assert isinstance(inference.client, LlamaStackClient)
    assert inference.client.base_url == "http://localhost:5001"


def test_init_response_CONFIGURED_REMOTE_HOST_PORT() -> None:
    os.environ.clear()
    os.environ["INFERENCE_MODEL"] = "granite3.2:latest"
    os.environ["LLAMA_STACK_HOST"] = "localhost"
    os.environ["LLAMA_STACK_PORT"] = "5002"
    inference = init_inference_from_env()
    assert inference is not None
    assert isinstance(inference, LlamaStackAgentInference)
    assert inference.model == "granite3.2:latest"
    assert isinstance(inference.client, LlamaStackClient)
    assert inference.client.base_url == "http://localhost:5002"


def test_init_response_CONFIGURED_REMOTE_URL() -> None:
    os.environ.clear()
    os.environ["INFERENCE_MODEL"] = "granite3.2:latest"
    os.environ["LLAMA_STACK_URL"] = "https://localhost:5003"
    inference = init_inference_from_env()
    assert inference is not None
    assert isinstance(inference, LlamaStackAgentInference)
    assert inference.model == "granite3.2:latest"
    assert isinstance(inference.client, LlamaStackClient)
    assert inference.client.base_url == "https://localhost:5003"


def test_init_response_CONFIGURED_EMBEDDED() -> None:
    os.environ.clear()
    os.environ["INFERENCE_MODEL"] = "granite3.2:latest"
    # start with example ollama config and check expeced error is raised
    test_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(test_dir, "examples", "llamastack-ollama.yaml")
    os.environ["LLAMA_STACK_CONFIG_FILE"] = config_file

    try:
        init_inference_from_env()
    except ValueError:
        # commented out as other exception is raised in Pants because path to config file is invalid in Pants, probably another root is used
        # assert str(e).startswith(
        #     "Model 'granite3.2:latest' is not available in Ollama."
        # )
        pass
    else:
        assert False, "Exception not raised"


if __name__ == "__main__":
    """Allows to run inference test against real LLamaStack model"""

    inference = init_inference_from_env()

    if inference:
        response = asyncio.run(
            inference.call_model(
                "use tool named get_current_time to get the current time",
                "what is the current time?",
            )
        )

        print("Response: " + response)
    else:
        print("Inference not initialized because not configured in env variables")
