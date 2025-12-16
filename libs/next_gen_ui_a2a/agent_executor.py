import json
import uuid

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import DataPart, Message, Part, Role, TextPart
from next_gen_ui_agent import AgentConfig, InputData, NextGenUIAgent, UIBlock
from next_gen_ui_agent.inference.inference_base import InferenceBase


class NextGenUIAgentExecutor(AgentExecutor):
    """Next Gen UI Agent Executor. AgentConfig is required"""

    def __init__(self, inference: InferenceBase, config: AgentConfig):
        self.ngui_agent = NextGenUIAgent(inference=inference, config=config)

    def _data_selection(self, message: Message) -> tuple[str, list[InputData]]:
        """Get data from the message parts."""
        input_data_list = []
        user_prompt = ""
        # TODO: NGUI-495 stabilize input data selection
        metadata = message.metadata

        for p in message.parts:
            id = str(uuid.uuid4())
            part_root = p.root
            if not user_prompt and isinstance(part_root, TextPart):
                user_prompt = part_root.text
                # Try to get data from metadata
                if not metadata and part_root.metadata:
                    metadata = part_root.metadata

                if metadata and metadata.get("data"):
                    if isinstance(metadata.get("data"), str):
                        data = metadata["data"]
                    else:
                        data = json.dumps(metadata["data"])

                    data_type = None
                    if metadata.get("type"):
                        data_type = str(metadata.get("type"))

                    input_data_list.append(
                        InputData(
                            id=id,
                            data=data,
                            type=data_type,
                        )
                    )

            if isinstance(part_root, DataPart):
                data_type = None
                if part_root.metadata and part_root.metadata.get("type"):
                    data_type = str(part_root.metadata.get("type"))

                input_data_list.append(
                    InputData(id=id, data=json.dumps(part_root.data), type=data_type)
                )

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
                "No input data gathered from either Message metadata or TextPart metadata or DataPart"
            )
        # TODO: Parallelize per input data if needed (depends on NGUI-495	Stabilize input/output A2A schemas, sync with MCP)
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

            summary = f"Component is rendered in UI. {self.ngui_agent.component_info(ui_block.configuration)}"
            message = Message(
                role=Role.agent,
                parts=[
                    Part(
                        root=TextPart(
                            text=summary,
                            # metadata={"structured_data": ui_block},
                        )
                    ),
                    Part(
                        root=DataPart(
                            data=ui_block.model_dump(
                                exclude_unset=True,
                                exclude_defaults=True,
                                exclude_none=True,
                            )
                        )
                    ),
                ],
                message_id=str(uuid.uuid4()),
                task_id=None,
                context_id=None,
            )
            await event_queue.enqueue_event(message)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise Exception("cancel not supported")
