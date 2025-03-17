import asyncio
import json
import traceback

from .model import InferenceBase
from .types import AgentInput, InputData, UIComponentMetadata

ui_components_description = """
* none - component to use when the data are not appropriate to be shown for user's query.
* table - component to visualize multi-item data with more items (more than 6). Better for small number of shown fields.
* set-of-cards - component to visualize multi-item data with few items (up to 6). Better for high numbers of shown fields.
* one-card - component to visualize one data item.
* chart-line - component to visualize multi-item data as a line graph. Suitable for series of number values.
* chart-pie - component to visualize multi-item data of any size as a pie chart. Suitable for items percentage or portion values. First field contains the name, second percentage value.
* video-player - component to play video from one item data. First field contains title, second url to the video e.g. https://www.youtube.com/watch?v=v-PjgYDrg70
* image - component to show one image from one item data. First field contains title, second url to the image.
"""


async def component_selection(
    inference: InferenceBase, input: AgentInput
) -> list[UIComponentMetadata]:
    print("\n\n---CALL component_selection---")
    components = await asyncio.gather(
        *[
            component_selection_run(input["user_prompt"], inference, data)
            for data in input["input_data"]
        ]
    )
    print(components)

    return components


async def component_selection_run(
    user_prompt: str,
    inference: InferenceBase,
    input_data: InputData,
) -> UIComponentMetadata:
    """Run Component Selection task."""

    print(f"\n\n---CALL component_selection_run--- id: {input_data['id']}")
    # print(user_prompt)
    # print(input_data)

    sys_msg_content = f"""
        You are helpful and advanced user interface design assistant. Based on the user query and JSON formatted data, select the best one component to visualize the data to the user.
        Generate response in the JSON format only. Select one component only.
        Provide the title for the component in "title".
        Provide reason for the component selection in the "reasonForTheComponentSelection".
        Provide your confidence for the component selection as a percentage in the "confidenceScore".
        Select only relevant data fields to be presented in the component. Do not bloat presentation. Show all the important info about the data item. Mainly include information the user asks for.
        Provide "name" for every field.
        For every field provide "data_path" containing path to get the value from the data. Do not use any formatting or calculations in the "data_path".

        Available components:
        {ui_components_description}
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

    prompt = f"""
        === User query ===
        {user_prompt}

        === Data ===
        {input_data['data']}
    """

    response = await inference.call_model(sys_msg_content, prompt)
    print("Component metadata:")
    print(response)

    try:
        result: UIComponentMetadata = json.loads(response)
        # TODO Validate response
        result["id"] = input_data["id"]
        return result
    except json.JSONDecodeError as e:
        print("Cannot decode the json", e)
        traceback.print_exc()
        raise e
