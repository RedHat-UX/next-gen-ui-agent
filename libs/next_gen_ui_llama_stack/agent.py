import asyncio
import logging
from typing import AsyncIterator, Literal, Optional

from llama_stack_client import AsyncLlamaStackClient, LlamaStackClient
from llama_stack_client.types.agents.turn import Step
from next_gen_ui_agent import (
    AgentConfig,
    InputData,
    NextGenUIAgent,
    UIComponentMetadata,
)
from next_gen_ui_agent.model import InferenceBase
from next_gen_ui_agent.types import UIBlock
from next_gen_ui_llama_stack.llama_stack_inference import (
    LlamaStackAgentInference,
    LlamaStackAsyncAgentInference,
)
from next_gen_ui_llama_stack.types import ResponseEventError, ResponseEventSuccess

logger = logging.getLogger(__name__)


class NextGenUILlamaStackAgent:
    """Next Gen UI Agen as Llama stack agent."""

    def __init__(
        self,
        client: LlamaStackClient | AsyncLlamaStackClient,
        model: str,
        inference: Optional[InferenceBase] = None,
        config: Optional[AgentConfig] = None,
        execution_mode: Literal["stream", "batch"] = "stream",
    ):
        """
        Initialize Next Gen UI Agent as Llama stack agent.
        Inference is created based on provided client and model if not provided (either directly or in config).

        Args:
            client: LlamaStack client (sync or async)
            model: Model name to use
            inference: Optional custom inference implementation
            config: Optional agent configuration
            execution_mode: Processing execution mode:
                - "batch": Process all components in parallel, yield results as one event containing all results, or one error event if processing of any data fails
                - "stream": Process in parallel but yield event for each data item as it completes (default)
        """
        if not inference:
            if isinstance(client, LlamaStackClient):
                inference = LlamaStackAgentInference(client, model)
            else:
                inference = LlamaStackAsyncAgentInference(client, model)

        self.client = client
        self.stream_mode = execution_mode
        config = config if config else AgentConfig()
        self.ngui_agent = NextGenUIAgent(config=config, inference=inference)

    def _data_selection(self, steps: list[Step]) -> list[InputData]:
        """Get data from all tool messages."""
        data = []
        for s in steps:
            if not s.step_type == "tool_execution":
                continue
            for r in s.tool_responses:
                d = InputData(id=r.call_id, data=str(r.content), type=r.tool_name)
                data.append(d)

        return data

    async def create_turn(
        self, user_prompt, steps: list[Step], component_system: Optional[str] = None
    ) -> AsyncIterator[ResponseEventSuccess | ResponseEventError]:
        """
        Process one conversation turn to render UI.
        Get data from all tool messages found in provided turn steps, and runs
        'UI Agent' for them to generate UI components.
        `ToolResponse.tool_name` is used as `InputData.type` so can be used for
        HBC selection through mapping in UI Agent's configuration.

        Behavior depends on stream_mode:
        - "batch": All components are processed in parallel and results are yielded in batches
        - "progressive": Components are processed in parallel but yielded individually as they complete
        """

        logger.debug("create_turn. user_prompt: %s", user_prompt)
        tool_data_list = self._data_selection(steps)

        logger.info("------NGUI Agent, tool_data_list: %s", tool_data_list)

        if self.stream_mode == "batch":
            # Solution 1: Fully parallel processing with batch yields
            async for event in self._create_turn_batch(
                user_prompt, tool_data_list, component_system
            ):
                yield event
        else:  # progressive
            # Solution 3: Hybrid approach - parallel selection with progressive yields
            async for event in self._create_turn_progressive(
                user_prompt, tool_data_list, component_system
            ):
                yield event

    async def _create_turn_batch(
        self,
        user_prompt: str,
        tool_data_list: list[InputData],
        component_system: Optional[str],
    ) -> AsyncIterator[ResponseEventSuccess | ResponseEventError]:
        """
        Process all components in parallel and yield results in batches.
        Maximum parallelization with batch results.
        """
        # TODO error handling for component selection and rendering - how to do it?
        try:
            # Process all input_data in parallel for component selection
            components = await asyncio.gather(
                *[
                    self.ngui_agent.select_component(user_prompt, input_data)
                    for input_data in tool_data_list
                ]
            )

            # Transform data for each component (synchronous operations)
            components_data = [
                self.ngui_agent.transform_data(input_data, component)
                for input_data, component in zip(tool_data_list, components)
            ]

            # Render all components (synchronous operations)
            renderings = [
                self.ngui_agent.generate_rendering(component_data, component_system)
                for component_data in components_data
            ]

            # Yield all renderings at once
            yield ResponseEventSuccess(
                event_type="success",
                payload=[
                    UIBlock(
                        id=input_data["id"],
                        rendering=rendering,
                        configuration=self.ngui_agent.construct_UIBlockConfiguration(
                            input_data, component
                        ),
                    )
                    for input_data, component, rendering in zip(
                        tool_data_list, components, renderings
                    )
                ],
            )
        except Exception as e:
            logger.exception("Error processing components in batch mode")
            yield ResponseEventError(event_type="error", payload=e)

    async def _create_turn_progressive(
        self,
        user_prompt: str,
        tool_data_list: list[InputData],
        component_system: Optional[str],
    ) -> AsyncIterator[ResponseEventSuccess | ResponseEventError]:
        """
        Process components in parallel but yield each result progressively as it completes.
        Parallel component selection with progressive feedback.
        """

        # Create a lookup map from id to input_data for quick retrieval
        id_to_input_data = {
            input_data["id"]: input_data for input_data in tool_data_list
        }

        # Create all selection tasks in parallel
        selection_tasks = [
            asyncio.create_task(
                self.ngui_agent.select_component(user_prompt, input_data)
            )
            for input_data in tool_data_list
        ]

        # Process results as they complete
        for completed_task in asyncio.as_completed(selection_tasks):
            try:
                component: UIComponentMetadata = await completed_task

                # Find the corresponding input_data by matching the id from the component
                input_data = id_to_input_data[component.id]  # type: ignore

                # Transform and render immediately
                component_data = self.ngui_agent.transform_data(input_data, component)
                rendering = self.ngui_agent.generate_rendering(
                    component_data, component_system
                )

                # Construct UI block configuration and yield it immediately
                ui_block = UIBlock(
                    id=component.id,  # type: ignore
                    rendering=rendering,
                    configuration=self.ngui_agent.construct_UIBlockConfiguration(
                        input_data, component
                    ),
                )
                yield ResponseEventSuccess(event_type="success", payload=[ui_block])
            except Exception as e:
                logger.exception("Error processing component in progressive mode")
                yield ResponseEventError(event_type="error", payload=e)
