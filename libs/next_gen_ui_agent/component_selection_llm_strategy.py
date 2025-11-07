import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Any

from next_gen_ui_agent.array_field_reducer import reduce_arrays
from next_gen_ui_agent.json_data_wrapper import wrap_json_data, wrap_string_as_json
from next_gen_ui_agent.model import InferenceBase
from next_gen_ui_agent.types import AgentInput, InputData, UIComponentMetadata

MAX_STRING_DATA_LENGTH_FOR_LLM = 1000
"""Maximum length of the string data passed to the LLM in characters."""

MAX_ARRAY_SIZE_FOR_LLM = 6
"""Maximum size of the array data passed to the LLM in items. `reduce_arrays` function is used to reduce arrays size. LLM prompts must be tuned to handle the reduced arrays size."""


class ComponentSelectionStrategy(ABC):
    """Abstract base class for LLM-based component selection and configuration strategies."""

    logger: logging.Logger
    input_data_json_wrapping: bool
    """
    If `True`, the agent will wrap the JSON input data into data type field if necessary due to its structure.
    If `False`, the agent will never wrap the JSON input data into data type field.
    """

    def __init__(self, logger: logging.Logger, input_data_json_wrapping: bool):
        self.logger = logger
        self.input_data_json_wrapping = input_data_json_wrapping

    async def select_components(
        self, inference: InferenceBase, input: AgentInput
    ) -> list[UIComponentMetadata]:
        """
        Select UI components based on input data and user prompt.
        Args:
            inference: Inference to use to call LLM by the agent
            input: Agent input
            json_data: optional JSON data parsed into python objects to be processed
        Returns:
            List of `UIComponentMetadata`
        """
        self.logger.debug("---CALL component_selection---")
        components = await asyncio.gather(
            *[
                self.component_selection_run(inference, input["user_prompt"], data)
                for data in input["input_data"]
            ]
        )
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(components)

        return components

    async def component_selection_run(
        self,
        inference: InferenceBase,
        user_prompt: str,
        input_data: InputData,
    ) -> UIComponentMetadata:
        """Run Component Selection task."""

        input_data_id = input_data["id"]
        self.logger.debug("---CALL component_selection_run--- id: %s", {input_data_id})

        json_data = input_data.get("json_data")

        if not json_data:
            json_data = json.loads(input_data["data"])

        if isinstance(json_data, str):
            # wrap string as JSON - necessary for the output of the `noop` input data transformer to be processed by the LLM
            json_data_for_llm = wrap_string_as_json(
                json_data, input_data.get("type"), MAX_STRING_DATA_LENGTH_FOR_LLM
            )
            json_data = wrap_string_as_json(json_data, input_data.get("type"))

        else:
            # wrap parsed JSON data structure into data type field if allowed and necessary
            if self.input_data_json_wrapping:
                json_data = wrap_json_data(json_data, input_data.get("type"))
            # we have to reduce arrays size to avoid LLM context window limit
            json_data_for_llm = reduce_arrays(json_data, MAX_ARRAY_SIZE_FOR_LLM)

        inference_output = await self.perform_inference(
            inference, user_prompt, json_data_for_llm, input_data_id
        )

        try:
            result = self.parse_infernce_output(inference_output, input_data_id)
            result.json_data = json_data
            return result
        except Exception as e:
            self.logger.exception("Cannot decode the json from LLM response")
            raise e

    @abstractmethod
    async def perform_inference(
        self,
        inference: InferenceBase,
        user_prompt: str,
        json_data: Any,
        input_data_id: str,
    ) -> list[str]:
        """
        Perform inference to select UI components and configure them.
        Multiple LLM calls can be performed and inference results can be returned as a list of strings.

        Args:
            inference: Inference to use to call LLM by the agent
            user_prompt: User prompt to be processed
            json_data: JSON data parsed into python objects to be processed
            input_data_id: ID of the input data

        Returns:
            List of strings with LLM inference outputs
        """
        pass

    @abstractmethod
    def parse_infernce_output(
        self, inference_output: list[str], input_data_id: str
    ) -> UIComponentMetadata:
        """
        Parse LLM inference outputs from `perform_inference` and return `UIComponentMetadata`
        or throw exception if it can't be constructed because of invalid LLM outputs.

        Args:
            inference_output: List of strings with LLM inference outputs generated from perform_inference method
            input_data_id: ID of the input data

        Returns:
            `UIComponentMetadata`
        """
        pass


def trim_to_json(text: str) -> str:
    """
    Remove all characters from the string before `</think>` tag if present.
    Then remove all characters until the first occurrence of '{' or '[' character. String is not modified if these character are not found.
    Everything after the last '}' or ']' character is stripped also.

    Args:
        text: The input string to process

    Returns:
        The string starting from the first '{' or '[' character and ending at the last '}' or ']' character,
        or the original string if neither character is found
    """

    # check if text contains </think> tag
    if "</think>" in text:
        text = text.split("</think>")[1]

    # Find the start of JSON (first { or [)
    start_index = -1
    for i, char in enumerate(text):
        if char in "{[":
            start_index = i
            break

    if start_index == -1:
        return text

    # Find the end of JSON (last } or ])
    end_index = -1
    for i in range(len(text) - 1, start_index - 1, -1):
        if text[i] in "]}":
            end_index = i + 1
            break

    if end_index == -1:
        return text[start_index:]

    return text[start_index:end_index]


def correct_chart_component_name(json_str: str) -> str:
    """
    Correct common LLM mistakes where it outputs chart type as component name.
    
    LLMs sometimes output "bar-chart", "line-chart", etc. as component names
    instead of using "chart" with a separate "chartType" field.
    
    This function automatically corrects:
    - "bar-chart" → "chart" with "chartType": "bar"
    - "line-chart" → "chart" with "chartType": "line"
    - "pie-chart" → "chart" with "chartType": "pie"
    - "donut-chart" → "chart" with "chartType": "donut"
    - "mirrored-bar-chart" → "chart" with "chartType": "mirrored-bar"
    
    Args:
        json_str: JSON string potentially containing incorrect component names
        
    Returns:
        Corrected JSON string with proper component/chartType structure
    """
    chart_type_mapping = {
        "bar-chart": "bar",
        "line-chart": "line",
        "pie-chart": "pie",
        "donut-chart": "donut",
        "mirrored-bar-chart": "mirrored-bar"
    }
    
    for wrong_name, chart_type in chart_type_mapping.items():
        if f'"{wrong_name}"' in json_str:
            print(f"[ComponentSelection] Correcting component name: {wrong_name} -> chart (chartType: {chart_type})")
            # Handle both with and without spaces after colon
            json_str = json_str.replace(
                f'"component":"{wrong_name}"', 
                f'"component":"chart","chartType":"{chart_type}"'
            )
            json_str = json_str.replace(
                f'"component": "{wrong_name}"', 
                f'"component": "chart", "chartType": "{chart_type}"'
            )
    
    return json_str
