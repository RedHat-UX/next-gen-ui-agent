from next_gen_ui_llama_stack import NextGenUILlamaStackAgent
from llama_stack_client import LlamaStackClient


def test_next_gen_ui_llama_stack() -> None:
    client = LlamaStackClient()
    NextGenUILlamaStackAgent(client=client, model="model")
