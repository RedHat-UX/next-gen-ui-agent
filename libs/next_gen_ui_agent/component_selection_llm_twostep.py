import logging
from typing import Any

from next_gen_ui_agent.component_selection_llm_strategy import (
    ComponentSelectionStrategy,
    trim_to_json,
)
from next_gen_ui_agent.model import InferenceBase
from next_gen_ui_agent.types import UIComponentMetadata
from pydantic_core import from_json

logger = logging.getLogger(__name__)

# Chart component instructions - refactored for clarity
chart_instructions = """
CHART COMPONENT RULES:

⚠️⚠️⚠️ RULE #1 - ALWAYS CHECK USER'S EXACT WORDS FIRST ⚠️⚠️⚠️
IF the user explicitly says "donut chart" in their query → YOU MUST USE "chartType": "donut"
IF the user explicitly says "pie chart" in their query → YOU MUST USE "chartType": "pie"
IF the user explicitly says "bar chart" in their query → YOU MUST USE "chartType": "bar"
IF the user explicitly says "line chart" in their query → YOU MUST USE "chartType": "line"

DO NOT substitute a different chart type than what the user explicitly requested!

1. CHART TYPE SELECTION:
   - "bar" → compare ONE metric across multiple items (e.g., "compare values", "metric comparison")
   - "line" → trends over time, multi-series comparisons over time
   - "mirrored-bar" → compare TWO DIFFERENT metrics side-by-side (e.g., "metric1 vs metric2")
   - "pie" → proportions (use when user says "pie chart" or doesn't specify)
   - "donut" → proportions (ONLY when user explicitly says "donut chart")

2. CRITICAL: Count the ACTUAL metrics the user explicitly asks for (DO NOT invent metrics!):
   
   ⚠️  SINGLE METRIC → bar chart:
   - "compare metric A" → bar (user asked for: metricA)
   - "compare values" → bar (user asked for: value)
   - "show all scores" → bar (user asked for: score)
   - "rating comparison" → bar (user asked for: rating ONLY - don't add other metrics!)
   - "compare prices" → bar (user asked for: price)
   
   ⚠️  TRENDS OVER TIME → line chart:
   - "compare trends", "weekly/daily/monthly", "over time" → line
   
   ⚠️  TWO DIFFERENT METRICS → mirrored-bar (user MUST explicitly mention BOTH):
   - "metric1 vs metric2" → mirrored-bar (user asked for: metric1 AND metric2)
   - "score and rating" → mirrored-bar (user asked for: score AND rating)
   - "cost vs value" → mirrored-bar (user asked for: cost AND value)
   - "compare actual and target" → mirrored-bar (user asked for: actual AND target)
   
   ❌ DO NOT ADD METRICS THE USER DIDN'T ASK FOR!
   If user says "score comparison", they want score only → bar chart with 2 fields total

3. FOR LINE CHARTS WITH NESTED TIME-SERIES DATA:
   ⚠️  CRITICAL FIELD ORDER - DO NOT DEVIATE:
   Field 1: Item identifier (creates series names/lines)
           Example: items[*].name → "Item A", "Item B"
   Field 2: Nested x-axis (time dimension)
           Example: items[*].timeSeries[*].period → 1, 2, 3, 4
   Field 3: Nested y-axis (metric values)  
           Example: items[*].timeSeries[*].value → 158411483, 75165786, ...
   
   ⚠️  USE SIMPLE, STANDARD JSONPATH SYNTAX ONLY:
   ✅ CORRECT: "items[*].timeSeries[*].period"
   ✅ CORRECT: "items[*].nested[*].value"
   ✅ CORRECT: "results[*].item.name" (NOT results[size up to 6][*])
   ❌ WRONG: "'$$'[0]'.timeSeries[*].period" - INVALID SYNTAX
   ❌ WRONG: "['key[size up to 6]'][0]['nested']..." - TOO COMPLEX
   ❌ WRONG: "results[size up to 6][*].item.name" - DO NOT include [size...] type hints!
   
   ❌ DO NOT use items[*].totalValue (aggregate) - use items[*].timeSeries[*].value (nested period values)
   ❌ DO NOT put time/period field first - put item identifier first
   ❌ DO NOT create "Period" and "Value" as series names - use item names ("Item A", "Item B")
   
   Result: Multiple lines (one per item), x-axis=time, y-axis=metric

4. FOR SIMPLE BAR CHARTS (flat data):
   Field 1: Categories (e.g., items[*].name)
   Field 2: ONE metric only (e.g., items[*].value OR items[*].metric)
   
   For mirrored-bar ONLY:
   Field 1: Categories (e.g., items[*].name)
   Field 2: First metric (e.g., items[*].metric1)
   Field 3: Second metric (e.g., items[*].metric2)
   
   For PIE/DONUT charts (distribution/frequency):
   ⚠️  ONLY ONE field needed! Backend auto-counts occurrences.
   Field 1: Categories to count
   
   ⚠️  UNDERSTAND WHAT USER WANTS TO DISTRIBUTE:
   - "category distribution" → items[*].categories[*] (count category values)
   - "rating distribution" → items[*].rating (count rating values like 8.3, 9.0, 8.7)
   - "type distribution" → items[*].type (count types)
   - "status distribution" → items[*].status (count status values)
   
   ⚠️  CRITICAL FOR ARRAYS - ALWAYS USE [*] NOT [size:N]:
   ✅ CORRECT: "items[*].categories[*]" (extracts individual category strings)
   ❌ WRONG: "items[*].categories[size: 1]" (extracts entire array!)
   ❌ WRONG: "items[*].categories" (extracts entire array!)
   
   ❌ DO NOT confuse different field types - they may have different structures!
   ❌ DO NOT add a second field with counts - backend handles this automatically!

5. HORIZONTAL BAR CHARTS:
   If x-axis labels > 15 chars or contain long names/titles → set horizontal=true

6. CRITICAL: Count ONLY the metrics the user explicitly mentions!
   - "compare metric A" = user said: metricA → 1 metric → bar
   - "compare values" = user said: value → 1 metric → bar
   - "score comparison" = user said: score → 1 metric → bar (DO NOT add other metrics!)
   - "metric1 vs metric2" = user said: metric1, metric2 → 2 metrics → mirrored-bar
   - "score and rating" = user said: score, rating → 2 metrics → mirrored-bar
   
   ❌ NEVER invent or add metrics the user didn't explicitly request!
"""

ui_components_description_supported = """
* one-card - component to visualize multiple fields from one-item Data. One image can be shown if url is available in the Data. Array of objects can't be shown as a field.
* video-player - component to play a video from one-item Data. Video like trailer, promo video. Data must contain url pointing to the video to be shown, e.g. https://www.youtube.com/watch?v=v-PjgYDrg70
* image - component to show one image from one-item Data. Image like poster, cover, picture. Do not use for video! Select it if no other fields are necessary to be shown. Data must contain url pointing to the image to be shown, e.g. https://www.images.com/v-PjgYDrg70.jpeg
* chart - component to visualize numeric Data as charts (bar, line, pie, donut, mirrored-bar). See detailed CHART COMPONENT RULES below.
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
        self, inference_output: list[str], input_data_id: str
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
        result.id = input_data_id
        return result

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

        data_for_llm = str(json_data)

        response_1 = trim_to_json(
            await self.inference_step_1(inference, user_prompt, data_for_llm)
        )

        if self.select_component_only:
            return [response_1]

        response_2 = trim_to_json(
            await self.inference_step_2(
                inference, response_1, user_prompt, data_for_llm
            )
        )

        return [response_1, response_2]

    async def inference_step_1(self, inference, user_prompt, json_data_for_llm: str):
        """Run Component Selection inference."""

        sys_msg_content = f"""You are helpful and advanced user interface design assistant.
Based on the "User query" and JSON formatted "Data", select the best UI component to show the "Data" to the user.
Generate response in the JSON format only. Select one UI component only. Put it into "component".
Provide reason for the UI component selection in the "reasonForTheComponentSelection".
Provide your confidence for the UI component selection as a percentage in the "confidenceScore".
Provide title for the UI component in "title".

Select from these UI components: {get_ui_components_description(self.unsupported_components)}

{chart_instructions}
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

Response example for chart data (single metric comparison):
{
    "reasonForTheComponentSelection": "User wants to compare one metric (score) across multiple items",
    "confidenceScore": "95%",
    "title": "Score Comparison",
    "component": "chart",
    "chartType": "bar"
}
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
        return response

    async def inference_step_2(
        self,
        inference,
        component_selection_response,
        user_prompt,
        json_data_for_llm: str,
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
{json_data_for_llm}
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
    "chart": """Response example 1 - Simple comparison (bar/pie/donut chart):
[
    {
        "reason": "User wants to compare items by name",
        "confidenceScore": "98%",
        "name": "Item",
        "data_path": "items[*].name"
    },
    {
        "reason": "User asked to compare values",
        "confidenceScore": "98%",
        "name": "Value",
        "data_path": "items[*].value"
    }
]

Response example 1.5 - SINGLE-ITEM NESTED ARRAY (one item with time-series):
⚠️  CRITICAL: When user asks "time series for Item X", "daily values for Item Y" → USE chartType="line"

✅ CORRECT (one item with nested timeSeries array):
[
    {
        "reason": "Period is x-axis from nested timeSeries array",
        "confidenceScore": "98%",
        "name": "Period",
        "data_path": "item.timeSeries[*].period"
    },
    {
        "reason": "Value from nested array",
        "confidenceScore": "98%",
        "name": "Value",
        "data_path": "item.timeSeries[*].value"
    }
]

CRITICAL: For SINGLE item with nested array, use simple paths like "item.timeSeries[*].period"
DO NOT use complex paths like "['search_item[size up to 6]'][0]['item']..." - that is INVALID!

Response example 2 - NESTED TIME-SERIES (periodic trends):
⚠️  CRITICAL: When user asks "compare time series", "compare trends" → USE chartType="line"

✅ CORRECT FIELD ORDER:
[
    {
        "reason": "Item name creates separate series/lines (NOT x-axis)",
        "confidenceScore": "98%",
        "name": "Item",
        "data_path": "items[*].name"
    },
    {
        "reason": "Period is x-axis from nested timeSeries array",
        "confidenceScore": "98%",
        "name": "Period",
        "data_path": "items[*].timeSeries[*].period"
    },
    {
        "reason": "Value is y-axis from nested array (NOT items[*].totalValue)",
        "confidenceScore": "98%",
        "name": "Value",
        "data_path": "items[*].timeSeries[*].value"
    }
]

❌ WRONG - DO NOT DO THIS:
[
    {"name":"Period","data_path":"items[*].timeSeries[*].period"},  ← NO! Period should NOT be first
    {"name":"Value","data_path":"items[*].totalValue"}  ← NO! Use timeSeries[*].value
]

Result: items[*].name → "Item A", "Item B" (one line per item)
        items[*].timeSeries[*].period → 1, 2, 3, 4 (x-axis)
        items[*].timeSeries[*].value → periodic values (y-axis)

Response example 3 - MIRRORED-BAR (comparing TWO metrics side-by-side):
CRITICAL: When user asks to "compare metric1 and metric2", "score vs rating", "compare metric A and metric B" - USE MIRRORED-BAR (not line chart):
[
    {
        "reason": "Item name is the identifier for each bar",
        "confidenceScore": "98%",
        "name": "Item",
        "data_path": "items[*].name"
    },
    {
        "reason": "First metric to compare (score) - small values",
        "confidenceScore": "98%",
        "name": "Score",
        "data_path": "items[*].score"
    },
    {
        "reason": "Second metric to compare (rating) - different scale",
        "confidenceScore": "98%",
        "name": "Rating",
        "data_path": "items[*].rating"
    }
]
IMPORTANT: Use mirrored-bar ONLY when comparing TWO different metrics side-by-side (not trends over time). First field = identifier, second field = first metric, third field = second metric.
""",
}
