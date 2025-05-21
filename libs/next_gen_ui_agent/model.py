from abc import ABC, abstractmethod


class InferenceBase(ABC):
    @abstractmethod
    async def call_model(self, system_msg: str, prompt: str) -> str:
        """
        Call the LLM model with the given system message and prompt and return response.
        LLM should always return the same response for the same system message and prompt (eg. by tempetrature set to 0).
        """
        pass


class LangChainModelInference(InferenceBase):
    """Class wrapping Langchain langchain_core.language_models.BaseChatModel
    class."""

    def __init__(self, model):
        super().__init__()
        self.model = model

    async def call_model(self, system_msg: str, prompt: str) -> str:
        sys_msg = {"role": "system", "content": system_msg}
        human_message = {"role": "user", "content": prompt}
        response = await self.model.ainvoke([sys_msg, human_message])
        return str(response.content)
