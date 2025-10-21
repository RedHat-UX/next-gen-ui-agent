from next_gen_ui_agent.types import InputData, UIBlock
from pydantic import BaseModel


class MCPGenerateUIInput(BaseModel):
    user_prompt: str
    "Original user query without any changes. Do not generate this."
    input_data: list[InputData]
    "Input Data. JSON Array of objects with 'id' and 'data' keys. Do not generate this."


class MCPGenerateUIOutput(BaseModel):
    """MCP Output for Generate UI"""

    blocks: list[UIBlock]
    "Array of UI Blocks"
    summary: str
    "Summary or rendered UI blocks"
