import logging
from typing import Any

from next_gen_ui_agent.component_selection_chart_instructions import (
    CHART_FIELD_SELECTION_EXAMPLES,
    CHART_FIELD_SELECTION_EXTENSION,
    CHART_INSTRUCTIONS,
)
from next_gen_ui_agent.component_selection_common import (
    TWOSTEP_STEP1_PROMPT_RULES,
    TWOSTEP_STEP1_RESPONSE_EXAMPLES,
    TWOSTEP_STEP2_PROMPT_RULES,
    get_ui_components_description,
)
from next_gen_ui_agent.component_selection_llm_strategy import (
    ComponentSelectionStrategy,
    InferenceResult,
    LLMInteraction,
    trim_to_json,
    validate_and_correct_chart_type,
)
from next_gen_ui_agent.model import InferenceBase
from next_gen_ui_agent.types import UIComponentMetadata
from pydantic_core import from_json

logger = logging.getLogger(__name__)


class TwostepLLMCallComponentSelectionStrategy(ComponentSelectionStrategy):
    """Component selection strategy using two LLM inference calls, one for component selection and one for its configuration."""

    def __init__(
        self,
        unsupported_components: bool,
        select_component_only: bool = False,
        input_data_json_wrapping: bool = True,
    ):
        """
        Component selection strategy using two LLM inference calls, one for component selection and one for its configuration.

        Args:
            unsupported_components: if True, generate all UI components, otherwise generate only supported UI components
            select_component_only: if True, only generate the component, it is not necesary to generate it's configuration
            input_data_json_wrapping: if True, wrap the JSON input data into data type field if necessary due to its structure
        """
        super().__init__(logger, input_data_json_wrapping)
        self.unsupported_components = unsupported_components
        self.select_component_only = select_component_only

    def parse_infernce_output(
        self, inference_result: InferenceResult, input_data_id: str
    ) -> UIComponentMetadata:
        """Parse inference output and return UIComponentMetadata or throw exception if inference output is invalid."""

        # allow values coercing by `strict=False`
        # allow partial json parsing by `allow_partial=True`, validation will fail on missing fields then. See https://docs.pydantic.dev/latest/concepts/json/#partial-json-parsing
        part = from_json(inference_result["outputs"][0], allow_partial=True)

        # parse fields if they are available
        if len(inference_result["outputs"]) > 1:
            part["fields"] = from_json(
                inference_result["outputs"][1], allow_partial=True
            )
        else:
            part["fields"] = []

        result: UIComponentMetadata = UIComponentMetadata.model_validate(
            part, strict=False
        )
        result.id = input_data_id

        # Attach LLM interactions from result
        result.llm_interactions = inference_result["llm_interactions"]

        # Post-processing: Validate chart type matches reasoning
        validate_and_correct_chart_type(result, logger)

        # Log component selection reasoning
        logger.info(
            "[NGUI] Component selection reasoning:\n"
            "  Component: %s\n"
            "  Reason: %s\n"
            "  Confidence: %s",
            result.component,
            result.reasonForTheComponentSelection,
            result.confidenceScore,
        )

        return result

    async def perform_inference(
        self,
        inference: InferenceBase,
        user_prompt: str,
        json_data: Any,
        input_data_id: str,
    ) -> InferenceResult:
        """Run Component Selection inference."""

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "---CALL component_selection_inference--- id: %s", {input_data_id}
            )

        data_for_llm = str(json_data)

        # Initialize LLM interactions list
        llm_interactions: list[LLMInteraction] = []

        raw_response_1 = await self.inference_step_1(
            inference, user_prompt, data_for_llm, llm_interactions
        )
        response_1 = trim_to_json(raw_response_1)

        if self.select_component_only:
            return InferenceResult(
                outputs=[response_1], llm_interactions=llm_interactions
            )

        raw_response_2 = await self.inference_step_2(
            inference, response_1, user_prompt, data_for_llm, llm_interactions
        )
        response_2 = trim_to_json(raw_response_2)

        return InferenceResult(
            outputs=[response_1, response_2], llm_interactions=llm_interactions
        )

    async def inference_step_1(
        self,
        inference,
        user_prompt,
        json_data_for_llm: str,
        llm_interactions: list[LLMInteraction],
    ):
        """Run Component Selection inference."""

        sys_msg_content = f"""You are a UI design assistant. Select the best component to show the Data based on User query.

{TWOSTEP_STEP1_PROMPT_RULES}

Available components: {get_ui_components_description(self.unsupported_components)}

{CHART_INSTRUCTIONS}
"""

        sys_msg_content += f"""
{TWOSTEP_STEP1_RESPONSE_EXAMPLES}
"""

        prompt = f"""=== User query ===
{user_prompt}
=== Data ===
{json_data_for_llm}
"""

        logger.debug("LLM component selection system message:\n%s", sys_msg_content)
        logger.debug("LLM component selection prompt:\n%s", prompt)

        response = await inference.call_model(sys_msg_content, prompt)
        logger.debug("Component selection LLM response: %s", response)

        # Store step 1 interaction
        llm_interactions.append(
            LLMInteraction(
                step="component_selection",
                system_prompt=sys_msg_content,
                user_prompt=prompt,
                raw_response=response,
            )
        )

        return response

    async def inference_step_2(
        self,
        inference,
        component_selection_response,
        user_prompt,
        json_data_for_llm: str,
        llm_interactions: list[LLMInteraction],
    ):
        component = from_json(component_selection_response, allow_partial=True)[
            "component"
        ]

        """Run Component Configuration inference."""

        sys_msg_content = f"""You are a UI design assistant. Select the best fields to display Data in the {component} component.

{TWOSTEP_STEP2_PROMPT_RULES}

{get_sys_prompt_component_extensions(component)}

{get_sys_prompt_component_examples(component)}
"""

        prompt = f"""=== User query ===
{user_prompt}

=== Data ===
{json_data_for_llm}
"""

        logger.debug("LLM component configuration system message:\n%s", sys_msg_content)
        logger.debug("LLM component configuration prompt:\n%s", prompt)

        response = await inference.call_model(sys_msg_content, prompt)
        logger.debug("Component configuration LLM response: %s", response)

        # Store step 2 interaction
        llm_interactions.append(
            LLMInteraction(
                step="field_selection",
                system_prompt=sys_msg_content,
                user_prompt=prompt,
                raw_response=response,
            )
        )

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
    "chart": CHART_FIELD_SELECTION_EXTENSION,
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
    "chart": CHART_FIELD_SELECTION_EXAMPLES,
}
