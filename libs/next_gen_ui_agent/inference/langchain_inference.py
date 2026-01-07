from next_gen_ui_agent.inference.inference_base import InferenceBase


class LangChainModelInference(InferenceBase):
    """Inference implementation for Langchain langchain_core.language_models.BaseChatModel class."""

    def __init__(self, model):
        """
        Initialize LangChainModelInference.

        Args:
            model: Langchain langchain_core.language_models.BaseChatModel instance.
        """
        super().__init__()
        self.model = model

    async def call_model(self, system_msg: str, prompt: str) -> str:
        sys_msg = {"role": "system", "content": system_msg}
        human_message = {"role": "user", "content": prompt}
        response = await self.model.ainvoke([sys_msg, human_message])
        return str(response.content)
