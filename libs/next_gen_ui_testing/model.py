from next_gen_ui_agent.model import InferenceBase
from next_gen_ui_agent.types import UIComponentMetadata


class MockedInference(InferenceBase):
    """Mocked Inference to return defined reponse
    or throw an error if defined string in throw_exception_string is present in the prompt (data)
    """

    def __init__(
        self,
        response: UIComponentMetadata,
        throw_exception_string: str | None = None,
    ):
        super().__init__()
        self.response = response
        self.throw_exception_string = throw_exception_string

    async def call_model(self, system_msg: str, prompt: str) -> str:
        if self.throw_exception_string and self.throw_exception_string in prompt:
            raise Exception(self.throw_exception_string)
        return self.response.model_dump_json()


class MockedExceptionInference(InferenceBase):
    """Mocked Inference to throw an error."""

    def __init__(self, exception: Exception):
        super().__init__()
        self.exception = exception

    async def call_model(self, system_msg: str, prompt: str) -> str:
        raise self.exception
