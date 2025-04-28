from next_gen_ui_agent.model import InferenceBase
from next_gen_ui_agent.types import UIComponentMetadata


class MockedInference(InferenceBase):
    """Mocked Inference to return defined reponse."""

    def __init__(self, response: UIComponentMetadata):
        super().__init__()
        self.response = response

    async def call_model(self, system_msg: str, prompt: str) -> str:
        return self.response.model_dump_json()
