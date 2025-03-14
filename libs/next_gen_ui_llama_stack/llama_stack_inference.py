from llama_stack_client import LlamaStackClient
from llama_stack_client.lib.agents.agent import Agent
from llama_stack_client.types.shared import UserMessage
from next_gen_ui_agent.model import InferenceBase


class LlamaStackAgentInference(InferenceBase):
    """Class wrapping Langchain langchain_core.language_models.BaseChatModel
    class."""

    def __init__(self, client: LlamaStackClient, model: str):
        super().__init__()
        self.model = model
        self.client = client

    async def call_model(self, system_msg: str, prompt: str) -> str:
        agent = Agent(
            client=self.client,
            model=self.model,
            instructions=system_msg,
            enable_session_persistence=False,
        )
        # Create a session
        session_id = agent.create_session(session_name="ngui")
        # Non-streaming API
        response = agent.create_turn(
            session_id=session_id,
            messages=[UserMessage(content=prompt, role="user")],
            stream=False,
        )

        # print("Inputs:")
        # print(response.input_messages)
        # print("Output:")
        # print(response.output_message.content)
        # print("Steps:")
        # print(response.steps)
        result = response.output_message.content  # type: ignore

        if isinstance(result, str):
            return result
        return str(result)
