import logging
from typing import Any

from next_gen_ui_agent.component_selection_llm_strategy import (
    ComponentSelectionStrategy,
    trim_to_json,
)
from next_gen_ui_agent.model import InferenceBase
from next_gen_ui_agent.types import UIComponentMetadata
from pydantic_core import from_json

ui_components_description_supported = """
- 'one-card': component to show multiple fields from one-item data. One image can be shown if url is available together with other fields. Array of simple values from one-item data can be shown as a field. Array of objects can't be shown as a field.
- 'video-player': component to play video from one-item data. Videos like trailers, promo videos. Data must contain url pointing to the video to be shown, e.g. https://www.youtube.com/watch?v=v-PjgYDrg70
- 'image': component to show one image from one-item data. Images like posters, covers, pictures. Do not use for video! Do not use if other fields has to be shown, use `one-card` instead! Data must contain url pointing to the image to be shown, e.g. https://www.images.com/v-PjgYDrg70.jpeg
"""

ui_components_description_all = (
    ui_components_description_supported
    + """
- 'table': component to show array of objects with more than 6 items and small number of shown fields with short values.
- 'set-of-cards': component to show array of objects with less than 6 items, or high number of shown fields and fields with long values.
""".strip()
)


def get_ui_components_description(unsupported_components: bool) -> str:
    """Get UI components description for system prompt based on the unsupported_components flag."""
    if unsupported_components:
        return ui_components_description_all
    else:
        return ui_components_description_supported


logger = logging.getLogger(__name__)


class OnestepLLMCallComponentSelectionStrategy(ComponentSelectionStrategy):
    """Component selection strategy using one LLM inference call for both component selection and configuration."""

    def __init__(
        self,
        unsupported_components: bool = False,
        input_data_json_wrapping: bool = True,
    ):
        """
        Component selection strategy using one LLM inference call for both component selection and configuration.

        Args:
            unsupported_components: if True, generate all UI components, otherwise generate only supported UI components
            input_data_json_wrapping: if True, wrap the JSON input data into data type field if necessary due to its structure
        """
        super().__init__(logger, input_data_json_wrapping)
        self.unsupported_components = unsupported_components

    async def perform_inference(
        self,
        inference: InferenceBase,
        user_prompt: str,
        json_data: Any,
        input_data_id: str,
        previous_user_prompts: list[str] | None = None,
    ) -> list[str]:
        """Run Component Selection inference."""

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "---CALL component_selection_inference--- id: %s", {input_data_id}
            )
            # logger.debug(user_prompt)
            # logger.debug(input_data)

        sys_msg_content = """You are helpful and advanced user interface design assistant. Based on the "User query" and JSON formatted "Data", select the best UI component to visualize the "Data" to the user.
Generate response in the JSON format only. Select one component only into "component".
Provide the title for the component in "title".
Provide reason for the component selection in the "reasonForTheComponentSelection".
Provide your confidence for the component selection as a percentage in the "confidenceScore".
Provide list of "fields" to be visualized in the UI component. Select only relevant data fields to be presented in the component. Do not bloat presentation. Show all the important info about the data item. Mainly include information the user asks for in User query.
If the selected UI component requires specific fields mentioned in its description, provide them. Provide "name" for every field.
For every field provide "data_path" containing JSONPath to get the value from the Data. Do not use any formatting or calculation in the "data_path".
"""

        sys_msg_content += f"""
Select one from these UI components: {get_ui_components_description(self.unsupported_components)}
"""
        if previous_user_prompts and len(previous_user_prompts) > 0:
            sys_msg_content += """
Generate response for the current "User query" and "Data". Keep current UI component and its configuration consistent with the expected UI component generated previously for the "Previous user queries" if applicable for the current "User query" and "Data".
"""

        sys_msg_content += """
Response example for multi-item data:
{
    "title": "Orders",
    "reasonForTheComponentSelection": "More than 6 items in the data",
    "confidenceScore": "82%",
    "component": "table",
    "fields" : [
        {"name":"Name","data_path":"orders[*].name"},
        {"name":"Creation Date","data_path":"orders[*].creationDate"}
    ]
}

Response example for one-item data:
{
    "title": "Order CA565",
    "reasonForTheComponentSelection": "One item available in the data",
    "confidenceScore": "75%",
    "component": "one-card",
    "fields" : [
        {"name":"Name","data_path":"order.name"},
        {"name":"Creation Date","data_path":"order.creationDate"}
    ]
}"""

        prompt = f"""=== User query ===
{user_prompt}
"""

        if previous_user_prompts and len(previous_user_prompts) > 0:
            prompt += f"""
Previous user queries:
- {"\n- ".join(previous_user_prompts)}
"""

        prompt += f"""
=== Data ===
{str(json_data)}
"""

        # TODO remove this after testing
        # if previous_user_prompts and len(previous_user_prompts) > 0:
        #    print("prompt:", prompt)

        logger.debug("LLM system message:\n%s", sys_msg_content)
        logger.debug("LLM prompt:\n%s", prompt)

        response = trim_to_json(await inference.call_model(sys_msg_content, prompt))
        logger.debug("Component metadata LLM response: %s", response)

        return [response]

    def parse_infernce_output(
        self, inference_output: list[str], input_data_id: str
    ) -> UIComponentMetadata:
        """Parse inference output and return UIComponentMetadata or throw exception if inference output is invalid."""

        # allow values coercing by `strict=False`
        # allow partial json parsing by `allow_partial=True`, validation will fail on missing fields then. See https://docs.pydantic.dev/latest/concepts/json/#partial-json-parsing
        result: UIComponentMetadata = UIComponentMetadata.model_validate(
            from_json(inference_output[0], allow_partial=True), strict=False
        )
        result.id = input_data_id
        return result
