from next_gen_ui_beeai.beeai_inference import BeeAIInference


def test_init() -> None:
    BeeAIInference(model="ollama:llama3.2")
