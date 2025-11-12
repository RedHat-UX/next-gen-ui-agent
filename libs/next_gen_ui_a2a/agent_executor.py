import json
from uuid import uuid4

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import DataPart, Message, TextPart
from a2a.utils import new_agent_text_message
from next_gen_ui_agent import InputData, NextGenUIAgent
from next_gen_ui_agent.model import InferenceBase
from next_gen_ui_agent.types import AgentConfig, UIBlock


class NextGenUIAgentExecutor(AgentExecutor):
    """Next Gen UI Agent Executor. AgentConfig is required"""

    def __init__(self, inference: InferenceBase, config: AgentConfig):
        self.ngui_agent = NextGenUIAgent(inference=inference, config=config)

    def _data_selection(self, message: Message) -> tuple[str, list[InputData]]:
        """Get data from the message parts."""
        input_data_list = []
        user_prompt = ""

        for p in message.parts:
            id = uuid4().hex
            part_root = p.root
            if not user_prompt and isinstance(part_root, TextPart):
                user_prompt = part_root.text
                # Try to get data from metadata.datas
                if part_root.metadata and part_root.metadata.get("data"):
                    input_data_list.append(
                        InputData(
                            id=id,
                            data=json.dumps(part_root.metadata["data"]),
                            type=str(part_root.metadata.get("type")),
                        )
                    )

            if isinstance(part_root, DataPart):
                input_data_list.append(
                    InputData(id=id, data=json.dumps(part_root.data))
                )
            elif not user_prompt and isinstance(part_root, TextPart):
                input_data_list.append(InputData(id=id, data=part_root.text))

        return user_prompt, input_data_list

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        if not context.message:
            raise ValueError("No message provided")
        component_system = context.metadata.get("component_system", "json")

        user_prompt, input_data_list = self._data_selection(context.message)
        if len(input_data_list) == 0:
            # TODO: Throw a better error or map it to the right params error A2A error
            raise ValueError(
                "No input data gathered from either metadata of TextPart or DataPart"
            )
        for input_data in input_data_list:
            # 1. Component selection
            component_metadata = await self.ngui_agent.select_component(
                user_prompt=user_prompt, input_data=input_data
            )
            # 2. Data transformation
            components_data = self.ngui_agent.transform_data(
                input_data=input_data,
                component=component_metadata,
            )
            # 3. Design system rendering
            rendering = self.ngui_agent.generate_rendering(
                component=components_data,
                component_system=component_system,
            )
            block_config = self.ngui_agent.construct_UIBlockConfiguration(
                input_data=input_data,
                component_metadata=component_metadata,
            )
            ui_block = UIBlock(
                id=rendering.id, rendering=rendering, configuration=block_config
            )
            text = ui_block.model_dump_json(
                exclude_unset=True,
                exclude_defaults=True,
                exclude_none=True,
            )

            # TODO: Return same Output like MCPGenerateUIOutput !!!
            await event_queue.enqueue_event(new_agent_text_message(text))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise Exception("cancel not supported")
