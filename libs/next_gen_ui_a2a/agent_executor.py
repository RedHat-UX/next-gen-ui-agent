import json
from uuid import uuid4

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import DataPart, Message, TextPart
from a2a.utils import new_agent_text_message
from next_gen_ui_agent import AgentInput, InputData, NextGenUIAgent
from next_gen_ui_agent.types import AgentConfig


class NextGenUIAgentExecutor(AgentExecutor):
    """Next Gen UI Agent Executor. AgentConfig is required"""

    def __init__(self, config: AgentConfig):
        self.ngui_agent = NextGenUIAgent(config)

    def _data_selection(self, message: Message) -> tuple[str, list[InputData]]:
        """Get data from the message parts."""
        input_data = []
        user_prompt = ""

        for p in message.parts:
            id = uuid4().hex
            part_root = p.root
            if not user_prompt and isinstance(part_root, TextPart):
                user_prompt = part_root.text
                # Try to get data from metadata.datas
                if part_root.metadata and part_root.metadata.get("data"):
                    input_data.append(
                        InputData(
                            id=id,
                            data=json.dumps(part_root.metadata["data"]),
                            type=str(part_root.metadata.get("type")),
                        )
                    )

            if isinstance(part_root, DataPart):
                input_data.append(InputData(id=id, data=json.dumps(part_root.data)))
            elif not user_prompt and isinstance(part_root, TextPart):
                input_data.append(InputData(id=id, data=part_root.text))

        return user_prompt, input_data

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        if not context.message:
            raise ValueError("No message provided")
        component_system = context.metadata.get("component_system", "json")

        user_prompt, input_data = self._data_selection(context.message)
        if len(input_data) == 0:
            # TODO: Throw a better error or map it to the right params error A2A error
            raise ValueError(
                "No input data gathered from either metadata of TextPart or DataPart"
            )
        input = AgentInput(
            user_prompt=user_prompt,
            input_data=input_data,
        )

        components = await self.ngui_agent.component_selection(input=input)
        components_data = self.ngui_agent.data_transformation(
            input_data=input_data,
            components=components,
        )
        renditions = self.ngui_agent.design_system_handler(
            components=components_data,
            component_system=component_system,
        )

        await event_queue.enqueue_event(new_agent_text_message(renditions[0].content))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise Exception("cancel not supported")
