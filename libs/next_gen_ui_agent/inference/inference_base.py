from abc import ABC, abstractmethod


class InferenceBase(ABC):
    """
    Abstract base class for inference providers used by UI Agent.
    All inference providers must inherit from this class and implement the `call_model` method.
    """

    @abstractmethod
    async def call_model(self, system_msg: str, prompt: str) -> str:
        """
        Call the LLM model with the given system message and user prompt and return response.
        LLM should always return the same response for the same system message and user prompt (eg. by tempetrature set to 0).
        """
        pass
