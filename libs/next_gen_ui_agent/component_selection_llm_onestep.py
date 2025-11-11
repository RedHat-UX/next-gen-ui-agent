import logging
from typing import Any

from next_gen_ui_agent.component_selection_chart_instructions import CHART_INSTRUCTIONS
from next_gen_ui_agent.component_selection_llm_strategy import (
    ComponentSelectionStrategy,
    trim_to_json,
    validate_and_correct_chart_type,
)
from next_gen_ui_agent.model import InferenceBase
from next_gen_ui_agent.types import UIComponentMetadata
from pydantic_core import from_json

ui_components_description_supported = """
* one-card - component to visualize multiple fields from one-item data. One image can be shown if url is available together with other fields. Array of simple values from one-item data can be shown as a field. Array of objects can't be shown as a field.
* video-player - component to play video from one-item data. Videos like trailers, promo videos. Data must contain url pointing to the video to be shown, e.g. https://www.youtube.com/watch?v=v-PjgYDrg70
* image - component to show one image from one-item data. Images like posters, covers, pictures. Do not use for video! Select it if no other fields are necessary to be shown. Data must contain url pointing to the image to be shown, e.g. https://www.images.com/v-PjgYDrg70.jpeg
* chart - component to visualize numeric data as charts. Specify the chart type in "chartType" field: "bar", "line", "pie", "donut", or "mirrored-bar". Use for data comparisons, trends, distributions, and metrics.
"""

ui_components_description_all = (
    ui_components_description_supported
    + """
* table - component to visualize array of objects with multiple items (typically 3 or more) in a tabular format. Use when user explicitly requests a table, or for data with many items (especially >6), small number of fields, and short values.
* set-of-cards - component to visualize array of objects with multiple items. Use for data with fewer items (<6), high number of fields, or fields with long values. Also good when visual separation between items is important.
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
    ) -> list[str]:
        """Run Component Selection inference."""

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "---CALL component_selection_inference--- id: %s", {input_data_id}
            )
            # logger.debug(user_prompt)
            # logger.debug(input_data)

        sys_msg_content = f"""You are helpful and advanced user interface design assistant. Based on the "User query" and JSON formatted "Data", select the best UI component to visualize the "Data" to the user.

CRITICAL: If user explicitly requests a component type ("table", "chart", "cards"), USE IT unless data structure prevents it.

Generate response in the JSON format only. Select one component only into "component".
Provide the title for the component in "title".
Provide reason for the component selection in the "reasonForTheComponentSelection".
Provide your confidence for the component selection as a percentage in the "confidenceScore".
Provide list of "fields" to be visualized in the UI component. Select only relevant data fields to be presented in the component. Do not bloat presentation. Show all the important info about the data item. Mainly include information the user asks for in User query.
If the selected UI component requires specific fields mentioned in its description, provide them. Provide "name" for every field.
For every field provide "data_path" containing JSONPath to get the value from the Data. Do not use any formatting or calculation in the "data_path".

🔴 CRITICAL - JSONPATH: Carefully analyze the actual Data structure. If fields are nested (e.g., items[*].movie.title), you MUST include the full path. Do NOT skip intermediate objects.

Select one from there UI components: {get_ui_components_description(self.unsupported_components)}

{CHART_INSTRUCTIONS}
"""

        sys_msg_content += """
Response example for multi-item data:
{
    "title": "Orders",
    "reasonForTheComponentSelection": "User explicitly requested a table, and data has multiple items with short field values",
    "confidenceScore": "95%",
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
}

Response example for bar chart:
{
    "title": "Movie Revenue Comparison",
    "reasonForTheComponentSelection": "User wants to compare numeric values as a chart",
    "confidenceScore": "90%",
    "component": "chart",
    "chartType": "bar",
    "fields" : [
        {"name":"Movie","data_path":"movies[*].title"},
        {"name":"Revenue","data_path":"movies[*].revenue"}
    ]
}

Response example for mirrored-bar chart (comparing 2 metrics, note nested structure):
{
    "title": "Movie ROI and Budget Comparison",
    "reasonForTheComponentSelection": "User wants to compare two metrics (ROI and budget) across movies, which requires a mirrored-bar chart to handle different scales",
    "confidenceScore": "90%",
    "component": "chart",
    "chartType": "mirrored-bar",
    "fields" : [
        {"name":"Movie","data_path":"get_all_movies[*].movie.title"},
        {"name":"ROI","data_path":"get_all_movies[*].movie.roi"},
        {"name":"Budget","data_path":"get_all_movies[*].movie.budget"}
    ]
}

Response example for donut chart (user explicitly requested "donut"):
{
    "title": "Genre Distribution",
    "reasonForTheComponentSelection": "User explicitly requested a donut chart for genre distribution",
    "confidenceScore": "95%",
    "component": "chart",
    "chartType": "donut",
    "fields" : [
        {"name":"Genre","data_path":"movies[*].genre"}
    ]
}"""

        prompt = f"""=== User query ===
    {user_prompt}

    === Data ===
    {str(json_data)}
        """

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
