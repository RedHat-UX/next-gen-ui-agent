from abc import ABC, abstractmethod


class InferenceBase(ABC):
    @abstractmethod
    async def call_model(self, system_msg: str, prompt: str) -> str:
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
