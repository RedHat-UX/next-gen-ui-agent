import asyncio
import json
import logging

from next_gen_ui_agent.array_field_reducer import reduce_arrays
from next_gen_ui_agent.component_selection import trim_to_json
from next_gen_ui_agent.model import InferenceBase
from next_gen_ui_agent.types import (
    AgentInput,
    ComponentSelectionStrategy,
    InputData,
    UIComponentMetadata,
)
from pydantic_core import from_json

logger = logging.getLogger(__name__)

ui_components_description_supported = """
* one-card - component to visualize multiple fields from one-item Data. One image can be shown if url is available in the Data. Array of objects can't be shown as a field.
* video-player - component to play a video from one-item Data. Video like trailer, promo video. Data must contain url pointing to the video to be shown, e.g. https://www.youtube.com/watch?v=v-PjgYDrg70
* image - component to show one image from one-item Data. Image like poster, cover, picture. Do not use for video! Select it if no other fields are necessary to be shown. Data must contain url pointing to the image to be shown, e.g. https://www.images.com/v-PjgYDrg70.jpeg
"""

ui_components_description_all = (
    ui_components_description_supported
    + """
* table - component to visualize multi-item Data. Use it for Data with more than 6 items, small number of fields to be shown, and fields with short values.
* set-of-cards - component to visualize multi-item Data. Use it for Data with less than 6 items, high number of fields to be shown, and fields with long values.
""".strip()
)

# print("ui_components_description_all: " + ui_components_description_all)


def get_ui_components_description(unsupported_components: bool) -> str:
    """Get UI components description for system prompt based on the unsupported_components flag."""
    if unsupported_components:
        return ui_components_description_all
    else:
        return ui_components_description_supported


class TwostepLLMCallComponentSelectionStrategy(ComponentSelectionStrategy):
    """Component selection strategy using two LLM inference calls, one for component selection and one for its configuration."""

    def __init__(
        self, unsupported_components: bool, select_component_only: bool = False
    ):
        """
        Component selection strategy using two LLM inference calls, one for component selection and one for its configuration.

        Args:
            unsupported_components: if True, generate all UI components, otherwise generate only supported UI components
            select_component_only: if True, only generate the component, it is not necesary to generate it's configuration
        """
        self.unsupported_components = unsupported_components
        self.select_component_only = select_component_only

    async def select_components(
        self, inference: InferenceBase, input: AgentInput
    ) -> list[UIComponentMetadata]:
        logger.debug("---CALL component_selection---")
        components = await asyncio.gather(
            *[
                self.component_selection_run(input["user_prompt"], inference, data)
                for data in input["input_data"]
            ]
        )
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(components)

        return components

    async def component_selection_run(
        self,
        user_prompt: str,
        inference: InferenceBase,
        input_data: InputData,
    ) -> UIComponentMetadata:
        """Run Component Selection task."""

        logger.debug("---CALL component_selection_run--- id: %s", {input_data["id"]})

        inference_otput = await self.perform_inference(
            user_prompt, inference, input_data
        )

        try:
            return self.parse_infernce_output(inference_otput, input_data)
        except Exception as e:
            logger.exception("Cannot decode the json from LLM response")
            raise e

    def parse_infernce_output(
        self, inference_output: list[str], input_data: InputData
    ) -> UIComponentMetadata:
        """Parse inference output and return UIComponentMetadata or throw exception if inference output is invalid."""

        # allow values coercing by `strict=False`
        # allow partial json parsing by `allow_partial=True`, validation will fail on missing fields then. See https://docs.pydantic.dev/latest/concepts/json/#partial-json-parsing
        part = from_json(inference_output[0], allow_partial=True)

        # parse fields if they are available
        if len(inference_output) > 1:
            part["fields"] = from_json(inference_output[1], allow_partial=True)
        else:
            part["fields"] = []

        result: UIComponentMetadata = UIComponentMetadata.model_validate(
            part, strict=False
        )
        result.id = input_data["id"]
        return result

    async def perform_inference(
        self,
        user_prompt: str,
        inference: InferenceBase,
        input_data: InputData,
    ) -> list[str]:
        """Run Component Selection inference."""

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "---CALL component_selection_inference--- id: %s", {input_data["id"]}
            )

        # we have to parse JSON data to reduce arrays
        json_data = json.loads(input_data["data"])
        data = reduce_arrays(json_data, 6)
        json_data = str(data)

        response_1 = trim_to_json(
            await self.inference_step_1(inference, user_prompt, json_data)
        )

        if self.select_component_only:
            return [response_1]

        response_2 = trim_to_json(
            await self.inference_step_2(inference, response_1, user_prompt, json_data)
        )

        return [response_1, response_2]

    async def inference_step_1(self, inference, user_prompt, json_data):
        """Run Component Selection inference."""

        sys_msg_content = f"""You are helpful and advanced user interface design assistant.
Based on the "User query" and JSON formatted "Data", select the best UI component to show the "Data" to the user.
Generate response in the JSON format only. Select one UI component only. Put it into "component".
Provide reason for the UI component selection in the "reasonForTheComponentSelection".
Provide your confidence for the UI component selection as a percentage in the "confidenceScore".
Provide title for the UI component in "title".

Select from these UI components: {get_ui_components_description(self.unsupported_components)}

"""

        sys_msg_content += """
Response example for multi-item data:
{
    "reasonForTheComponentSelection": "More than 6 items in the data array. Short values to visualize based on the user query",
    "confidenceScore": "82%",
    "title": "Orders",
    "component": "table"
}

Response example for one-item data:
{
    "reasonForTheComponentSelection": "One item available in the data. Multiple fields to show based on the User query",
    "confidenceScore": "95%",
    "title": "Order CA565",
    "component": "one-card"
}

Response example for one-item data and image:
{
    "reasonForTheComponentSelection": "User asked to see the magazine cover",
    "confidenceScore": "75%",
    "title": "Magazine cover",
    "component": "image"
}
"""

        prompt = f"""=== User query ===
{user_prompt}
=== Data ===
{json_data}
"""

        logger.debug("LLM component selection system message:\n%s", sys_msg_content)
        logger.debug("LLM component selection prompt:\n%s", prompt)

        response = await inference.call_model(sys_msg_content, prompt)
        logger.debug("Component selection LLM response: %s", response)
        return response

    async def inference_step_2(
        self, inference, component_selection_response, user_prompt, json_data
    ):
        component = from_json(component_selection_response, allow_partial=True)[
            "component"
        ]

        """Run Component Configuration inference."""

        sys_msg_content = f"""You are helpful and advanced user interface design assistant.
Based on the "User query" and JSON formatted "Data", select the best fields to show the "Data" to the user in the UI component {component}.
Generate JSON array of objects only.
Provide list of "fields" to be visualized in the UI component.
Select only relevant "Data" fields to be presented in the UI component. Do not bloat presentation. Show all the important info about the data item. Mainly include information the user asks for in "User query".
Provide reason for the every field selection in the "reason".
Provide your confidence for the every field selection as a percentage in the "confidenceScore".
Provide "name" for every field.
For every field provide "data_path" containing path to get the value from the "Data". Do not use formatting or calculation in the "data_path".
{get_sys_prompt_component_extensions(component)}

{get_sys_prompt_component_examples(component)}
"""

        prompt = f"""=== User query ===
{user_prompt}

=== Data ===
{json_data}
"""

        logger.debug("LLM component configuration system message:\n%s", sys_msg_content)
        logger.debug("LLM component configuration prompt:\n%s", prompt)

        response = await inference.call_model(sys_msg_content, prompt)
        logger.debug("Component configuration LLM response: %s", response)
        return response


def get_sys_prompt_component_extensions(component: str) -> str:
    """Get system prompt component extensions for the selected UI component."""
    if component in SYS_PROMPT_COMPONENT_EXTENSIONS.keys():
        return SYS_PROMPT_COMPONENT_EXTENSIONS[component]
    else:
        return ""


SYS_PROMPT_COMPONENT_EXTENSIONS = {
    "image": """Provide one field only in the list, containing url of the image to be shown, taken from the "Data".""",
    "video-player": """Provide one field only in the list, containing url of the video to be played, taken from the "Data".""",
    "one-card": """Value the "data_path" points to must be either simple value or array of simple values. Do not point to objects in the "data_path".
Do not use the same "data_path" for multiple fields.
One field can point to the large image shown as the main image in the card UI, if url is available in the "Data".
Show ID value only if it seems important for the user, like order ID. Do not show ID value if it is not important for the user.""",
}


def get_sys_prompt_component_examples(component: str) -> str:
    """Get system prompt component examples for the selected UI component."""
    if component in SYS_PROMPT_COMPONENT_EXAMPLES.keys():
        return SYS_PROMPT_COMPONENT_EXAMPLES[component]
    else:
        return ""


SYS_PROMPT_COMPONENT_EXAMPLES = {
    "image": """Response example 1:
[
    {
        "reason": "image UI component is used, so we have to provide image url",
        "confidenceScore": "98%",
        "name": "Image Url",
        "data_path": "order.pictureUrl"
    }
]

Response example 2:
[
    {
        "reason": "image UI component is used, so we have to provide image url",
        "confidenceScore": "98%",
        "name": "Cover Image Url",
        "data_path": "magazine.cover_image_url"
    }
]
""",
    "video-player": """Response example 1:
[
    {
        "reason": "video-player UI component is used, so we have to provide video url",
        "confidenceScore": "98%",
        "name": "Video Url",
        "data_path": "order.trailerUrl"
    }
]

Response example 2:
[
    {
        "reason": "video-player UI component is used, so we have to provide video url",
        "confidenceScore": "98%",
        "name": "Promootion video url",
        "data_path": "product.promotion_video_href"
    }
]
""",
    "one-card": """Response example 1:
[
    {
        "reason": "It is always good to show order name",
        "confidenceScore": "98%",
        "name": "Name",
        "data_path": "order.name"
    },
    {
        "reason": "It is generally good to show order date",
        "confidenceScore": "94%",
        "name": "Order date",
        "data_path": "order.createdDate"
    },
    {
        "reason": "User asked to see the order status",
        "confidenceScore": "98%",
        "name": "Order status",
        "data_path": "order.status.name"
    }
]

Response example 2:
[
    {
        "reason": "It is always good to show product name",
        "confidenceScore": "98%",
        "name": "Name",
        "data_path": "info.name"
    },
    {
        "reason": "It is generally good to show product price",
        "confidenceScore": "92%",
        "name": "Price",
        "data_path": "price"
    },
    {
        "reason": "User asked to see the product description",
        "confidenceScore": "85%",
        "name": "Description",
        "data_path": "product_description"
    }
]
""",
    "table": """Response example 1:
[
    {
        "reason": "It is always good to show order name",
        "confidenceScore": "98%",
        "name": "Name",
        "data_path": "order[].name"
    },
    {
        "reason": "It is generally good to show order date",
        "confidenceScore": "94%",
        "name": "Order date",
        "data_path": "order[].createdDate"
    },
    {
        "reason": "User asked to see the order status",
        "confidenceScore": "98%",
        "name": "Order status",
        "data_path": "order[].status.name"
    }
]

Response example 2:
[
    {
        "reason": "It is always good to show product name",
        "confidenceScore": "98%",
        "name": "Name",
        "data_path": "product[].info.name"
    },
    {
        "reason": "It is generally good to show product price",
        "confidenceScore": "92%",
        "name": "Price",
        "data_path": "product[].price"
    },
    {
        "reason": "User asked to see the product description",
        "confidenceScore": "85%",
        "name": "Description",
        "data_path": "product[].product_description"
    }
]
""",
}
