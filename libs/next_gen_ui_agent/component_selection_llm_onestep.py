import logging
from typing import Any

from next_gen_ui_agent.component_selection_llm_strategy import (
    ComponentSelectionStrategy,
    trim_to_json,
)
from next_gen_ui_agent.model import InferenceBase
from next_gen_ui_agent.types import UIComponentMetadata
from pydantic_core import from_json

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
* one-card - component to visualize multiple fields from one-item data. One image can be shown if url is available together with other fields. Array of simple values from one-item data can be shown as a field. Array of objects can't be shown as a field.
* video-player - component to play video from one-item data. Videos like trailers, promo videos. Data must contain url pointing to the video to be shown, e.g. https://www.youtube.com/watch?v=v-PjgYDrg70
* image - component to show one image from one-item data. Images like posters, covers, pictures. Do not use for video! Select it if no other fields are necessary to be shown. Data must contain url pointing to the image to be shown, e.g. https://www.images.com/v-PjgYDrg70.jpeg
* chart - component to visualize numeric data as charts (bar, line, pie, donut, mirrored-bar). See detailed CHART COMPONENT RULES below.
"""

ui_components_description_all = (
    ui_components_description_supported
    + """
* table - component to visualize array of objects with more than 6 items and small number of shown fields with short values.
* set-of-cards - component to visualize array of objects with less than 6 items, or high number of shown fields and fields with long values.
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
Generate response in the JSON format only. Select one component only into "component".
Provide the title for the component in "title".
Provide reason for the component selection in the "reasonForTheComponentSelection".
Provide your confidence for the component selection as a percentage in the "confidenceScore".
Provide list of "fields" to be visualized in the UI component. Select only relevant data fields to be presented in the component. Do not bloat presentation. Show all the important info about the data item. Mainly include information the user asks for in User query.
If the selected UI component requires specific fields mentioned in its description, provide them. Provide "name" for every field.
For every field provide "data_path" containing JSONPath to get the value from the Data. Do not use any formatting or calculation in the "data_path".

Select one from there UI components: {get_ui_components_description(self.unsupported_components)}

{chart_instructions}
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
}

⚠️  CRITICAL - Response example for SIMPLE BAR CHART (single metric comparison):
When user asks "compare scores", "compare values", "metric comparison" → USE chartType="bar"

CORRECT EXAMPLE:
{
    "title": "Score Comparison",
    "reasonForTheComponentSelection": "User wants to compare one metric (score) across multiple items",
    "confidenceScore": "95%",
    "component": "chart",
    "chartType": "bar",
    "fields" : [
        {"name":"Item","data_path":"items[*].name"},
        {"name":"Score","data_path":"items[*].score"}
    ]
}

⚠️  CRITICAL - Response example for SINGLE-ITEM NESTED ARRAY (one item with time-series):
When user asks "daily values for Item X", "time series for Item Y" → USE chartType="line"

CORRECT EXAMPLE (one item with nested timeSeries array):
{
    "title": "Time Series for Item X",
    "reasonForTheComponentSelection": "User wants to view time series data for a specific item",
    "confidenceScore": "95%",
    "component": "chart",
    "chartType": "line",
    "fields" : [
        {"name":"Period","data_path":"item.timeSeries[*].period"},
        {"name":"Value","data_path":"item.timeSeries[*].value"}
    ]
}

CRITICAL: For SINGLE item with nested array, use simple paths like "item.timeSeries[*].period"
DO NOT use complex paths like "['search_item[size up to 6]'][0]['item']..." - that is INVALID!

⚠️  CRITICAL - Response example for NESTED TIME-SERIES (periodic trends):
When user asks "compare time series", "compare trends", "periodic comparisons" → USE chartType="line"

CORRECT EXAMPLE (multiple items comparing periodic trends):
{
    "title": "Periodic Value Trends",
    "component": "chart",
    "chartType": "line",
    "fields" : [
        {"name":"Item","data_path":"items[*].name"},
        {"name":"Period","data_path":"items[*].timeSeries[*].period"},
        {"name":"Value","data_path":"items[*].timeSeries[*].value"}
    ]
}

❌ WRONG - DO NOT DO THIS:
{
    "fields" : [
        {"name":"Period","data_path":"items[*].timeSeries[*].period"},  ← NO! Period should NOT be first
        {"name":"Value","data_path":"items[*].totalValue"}  ← NO! Use timeSeries[*].value, not totalValue
    ]
}

✅ CORRECT FIELD ORDER (memorize this):
1. items[*].name → Series names: "Item A", "Item B" (one line per item)
2. items[*].timeSeries[*].period → X-axis: 1, 2, 3, 4
3. items[*].timeSeries[*].value → Y-axis: 158411483, 75165786, ...

CRITICAL - Contrasting example for MIRRORED-BAR (comparing TWO metrics side-by-side):
When user asks to "compare metric1 and metric2", "score vs rating", "compare metric A and metric B" - USE MIRRORED-BAR (not line chart):
{
    "title": "Score vs Rating Comparison",
    "reasonForTheComponentSelection": "User wants to compare two different metrics side-by-side",
    "confidenceScore": "90%",
    "component": "chart",
    "chartType": "mirrored-bar",
    "fields" : [
        {"name":"Item","data_path":"items[*].name"},
        {"name":"Score","data_path":"items[*].score"},
        {"name":"Rating","data_path":"items[*].rating"}
    ]
}
IMPORTANT: Use mirrored-bar ONLY when comparing TWO different metrics (not trends over time). First field = identifier, second field = first metric, third field = second metric."""

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

        # Log the raw LLM output for debugging
        print(f"[ComponentSelection] Raw LLM output (first 1000 chars):")
        print(inference_output[0][:1000] if len(inference_output[0]) > 1000 else inference_output[0])
        
        # allow values coercing by `strict=False`
        # allow partial json parsing by `allow_partial=True`, validation will fail on missing fields then. See https://docs.pydantic.dev/latest/concepts/json/#partial-json-parsing
        try:
            result: UIComponentMetadata = UIComponentMetadata.model_validate(
                from_json(inference_output[0], allow_partial=True), strict=False
            )
            result.id = input_data_id
            return result
        except Exception as e:
            print(f"[ComponentSelection] ERROR parsing LLM output: {e}")
            print(f"[ComponentSelection] Full output:")
            print(inference_output[0])
            raise
