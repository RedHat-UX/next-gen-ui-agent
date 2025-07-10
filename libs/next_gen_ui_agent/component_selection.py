import asyncio
import json
import logging
import os

from next_gen_ui_agent.array_field_reducer import reduce_arrays
from next_gen_ui_agent.model import InferenceBase
from next_gen_ui_agent.types import AgentInput, InputData, UIComponentMetadata
from pydantic_core import from_json

ui_components_description_all = """
* table - component to visualize array of data items with size over 6. Better suitable for small number of shown fields with shorter values.
* set-of-cards - component to visualize array of data items with size up to 6. Better suitable for high numbers of shown fields and for fields withlonger values.
* one-card - component to visualize one data item.
* video-player - component to play video from one item data. Field must contain url pointing to the video to be shown, e.g. https://www.youtube.com/watch?v=v-PjgYDrg70
* image - component to show one image from one item data. Field must contain url pointing to the image to be shown, e.g. https://www.images.com/v-PjgYDrg70.jpeg
"""

ui_components_description_supported = """
* one-card - component to visualize one data item.
* video-player - component to play video from one item data. Field must contain url pointing to the video to be shown, e.g. https://www.youtube.com/watch?v=v-PjgYDrg70
* image - component to show one image from one item data. Field must contain url pointing to the image to be shown, e.g. https://www.images.com/v-PjgYDrg70.jpeg
"""

""" Load environment variable `NEXT_GEN_UI_AGENT_USE_ALL_COMPONENTS` to decide which set of allowed components to use for the LLM prompt.
If False then only supported components from `ui_components_description_supported` are used.
If True then all components from `ui_components_description_all` are used.
"""
if os.getenv("NEXT_GEN_UI_AGENT_USE_ALL_COMPONENTS", "False").lower() == "true":
    ui_components_description = ui_components_description_all
else:
    ui_components_description = ui_components_description_supported

logger = logging.getLogger(__name__)


async def component_selection(
    inference: InferenceBase, input: AgentInput
) -> list[UIComponentMetadata]:
    logger.debug("---CALL component_selection---")
    components = await asyncio.gather(
        *[
            component_selection_run(input["user_prompt"], inference, data)
            for data in input["input_data"]
        ]
    )
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(components)

    return components


async def component_selection_inference(
    user_prompt: str,
    inference: InferenceBase,
    input_data: InputData,
) -> str:
    """Run Component Selection inference."""

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(
            "---CALL component_selection_inference--- id: %s", {input_data["id"]}
        )
        # logger.debug(user_prompt)
        # logger.debug(input_data)

    sys_msg_content = f"""You are helpful and advanced user interface design assistant. Based on the "User query" and JSON formatted "Data", select the best UI component to visualize the "Data" to the user.
Generate response in the JSON format only. Select one component only into "component".
Provide the title for the component in "title".
Provide reason for the component selection in the "reasonForTheComponentSelection".
Provide your confidence for the component selection as a percentage in the "confidenceScore".
Provide list of "fields" to be visualized in the UI component. Select only relevant data fields to be presented in the component. Do not bloat presentation. Show all the important info about the data item. Mainly include information the user asks for in User query.
If the selected UI component requires specific fields mentioned in its description, provide them. Provide "name" for every field.
For every field provide "data_path" containing path to get the value from the data. Do not use any formatting or calculations in the "data_path".

Select one from there UI components: {ui_components_description}
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

Response example for one item data:
{
    "title": "Order CA565",
    "reasonForTheComponentSelection": "One item available in the data",
    "confidenceScore": "35%",
    "component": "one-card",
    "fields" : [
        {"name":"Name","data_path":"order.name"},
        {"name":"Creation Date","data_path":"order.creationDate"}
    ]
}
"""

    # we have to parse JSON data to reduce arrays
    json_data = json.loads(input_data["data"])
    data = reduce_arrays(json_data, 6)

    prompt = f"""=== User query ===
{user_prompt}

=== Data ===
{str(data)}
    """

    logger.debug("LLM system message:\n%s", sys_msg_content)
    logger.debug("LLM prompt:\n%s", prompt)

    response = await inference.call_model(sys_msg_content, prompt)
    logger.debug("Component metadata LLM response: %s", response)

    return response


async def component_selection_run(
    user_prompt: str,
    inference: InferenceBase,
    input_data: InputData,
) -> UIComponentMetadata:
    """Run Component Selection task."""

    logger.debug("---CALL component_selection_run--- id: %s", {input_data["id"]})

    response = await component_selection_inference(user_prompt, inference, input_data)

    try:
        # allow values coercing by `strict=False`
        # allow partial json parsing by `allow_partial=True`, validation will fail on missing fields then. See https://docs.pydantic.dev/latest/concepts/json/#partial-json-parsing
        result: UIComponentMetadata = UIComponentMetadata.model_validate(
            from_json(response, allow_partial=True), strict=False
        )
        result.id = input_data["id"]
        return result
    except Exception as e:
        logger.exception("Cannot decode the json from LLM response")
        raise e
