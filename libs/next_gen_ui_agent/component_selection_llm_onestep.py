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

1. CHART TYPE SELECTION:
   - "bar" → compare ONE metric across multiple items (e.g., "compare revenue", "opening weekends")
   - "line" → trends over time, multi-series comparisons over time
   - "mirrored-bar" → compare TWO DIFFERENT metrics side-by-side (e.g., "revenue vs profit")
   - "pie" → proportions (use when user says "pie chart" or doesn't specify)
   - "donut" → proportions (use when user explicitly says "donut chart")
   
   ⚠️  RESPECT USER'S EXPLICIT CHART TYPE REQUEST:
   If user says "pie chart" → use "pie"
   If user says "donut chart" → use "donut"
   If user says "bar chart" → use "bar"
   If user says "line chart" → use "line"

2. CRITICAL: Count the ACTUAL metrics the user explicitly asks for (DO NOT invent metrics!):
   
   ⚠️  SINGLE METRIC → bar chart:
   - "compare opening weekend revenue" → bar (user asked for: openingWeekend)
   - "compare box office revenue" → bar (user asked for: revenue)
   - "show all movie budgets" → bar (user asked for: budget)
   - "ROI comparison" → bar (user asked for: roi ONLY - don't add budget!)
   - "compare ratings" → bar (user asked for: rating)
   
   ⚠️  TRENDS OVER TIME → line chart:
   - "compare trends", "weekly/daily/monthly", "over time" → line
   
   ⚠️  TWO DIFFERENT METRICS → mirrored-bar (user MUST explicitly mention BOTH):
   - "revenue vs profit" → mirrored-bar (user asked for: revenue AND profit)
   - "ROI and budget" → mirrored-bar (user asked for: roi AND budget)
   - "opening weekend vs total revenue" → mirrored-bar (user asked for: openingWeekend AND revenue)
   - "compare domestic and international revenue" → mirrored-bar (user asked for: domesticRevenue AND internationalRevenue)
   
   ❌ DO NOT ADD METRICS THE USER DIDN'T ASK FOR!
   If user says "ROI comparison", they want ROI only → bar chart with 2 fields total

3. FOR LINE CHARTS WITH NESTED TIME-SERIES DATA (like weeklyBoxOffice):
   ⚠️  CRITICAL FIELD ORDER - DO NOT DEVIATE:
   Field 1: Item identifier (creates series names/lines)
           Example: movies[*].title → "The Dark Knight", "Inception"
   Field 2: Nested x-axis (time dimension)
           Example: movies[*].weeklyBoxOffice[*].week → 1, 2, 3, 4
   Field 3: Nested y-axis (metric values)  
           Example: movies[*].weeklyBoxOffice[*].revenue → 158411483, 75165786, ...
   
   ⚠️  USE SIMPLE, STANDARD JSONPATH SYNTAX ONLY:
   ✅ CORRECT: "movies[*].weeklyBoxOffice[*].week"
   ✅ CORRECT: "items[*].nested[*].value"
   ✅ CORRECT: "compare_movies[*].movie.title" (NOT compare_movies[size up to 6][*])
   ❌ WRONG: "'$$'[0]'.weeklyBoxOffice[*].week" - INVALID SYNTAX
   ❌ WRONG: "['key[size up to 6]'][0]['nested']..." - TOO COMPLEX
   ❌ WRONG: "compare_movies[size up to 6][*].movie.title" - DO NOT include [size...] type hints!
   
   ❌ DO NOT use movies[*].revenue (total) - use movies[*].weeklyBoxOffice[*].revenue (nested weekly values)
   ❌ DO NOT put week/time field first - put item identifier first
   ❌ DO NOT create "Week" and "Revenue" as series names - use item names ("The Dark Knight", "Inception")
   
   Result: Multiple lines (one per item), x-axis=time, y-axis=metric

4. FOR SIMPLE BAR CHARTS (flat data):
   Field 1: Categories (e.g., movies[*].title)
   Field 2: ONE metric only (e.g., movies[*].revenue OR movies[*].openingWeekend)
   
   For mirrored-bar ONLY:
   Field 1: Categories (e.g., movies[*].title)
   Field 2: First metric (e.g., movies[*].revenue)
   Field 3: Second metric (e.g., movies[*].profit)
   
   For PIE/DONUT charts (distribution/frequency):
   ⚠️  ONLY ONE field needed! Backend auto-counts occurrences.
   Field 1: Categories to count
   
   ⚠️  UNDERSTAND WHAT USER WANTS TO DISTRIBUTE:
   - "genre distribution" → movies[*].genres[*] (count genres)
   - "rating distribution" → movies[*].imdbRating (count rating values like 8.3, 9.0, 8.7)
   - "director distribution" → movies[*].director (count directors)
   - "year distribution" → movies[*].year (count years)
   
   ⚠️  CRITICAL FOR ARRAYS - ALWAYS USE [*] NOT [size:N]:
   ✅ CORRECT: "movies[*].genres[*]" (extracts individual genre strings)
   ❌ WRONG: "movies[*].genres[size: 1]" (extracts entire array!)
   ❌ WRONG: "movies[*].genres" (extracts entire array!)
   
   ❌ DO NOT confuse "rating" with "genre" - they are different fields!
   ❌ DO NOT add a second field with counts - backend handles this automatically!

5. HORIZONTAL BAR CHARTS:
   If x-axis labels > 15 chars or contain movie titles/person names → set horizontal=true

6. CRITICAL: Count ONLY the metrics the user explicitly mentions!
   - "compare opening weekend revenue" = user said: openingWeekend → 1 metric → bar
   - "compare revenue" = user said: revenue → 1 metric → bar
   - "ROI comparison" = user said: roi → 1 metric → bar (DO NOT add budget!)
   - "revenue vs profit" = user said: revenue, profit → 2 metrics → mirrored-bar
   - "ROI and budget" = user said: roi, budget → 2 metrics → mirrored-bar
   
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
When user asks "compare ROI", "compare revenue", "opening weekend comparison" → USE chartType="bar"

CORRECT EXAMPLE:
{
    "title": "ROI Comparison",
    "reasonForTheComponentSelection": "User wants to compare one metric (ROI) across multiple movies",
    "confidenceScore": "95%",
    "component": "chart",
    "chartType": "bar",
    "fields" : [
        {"name":"Movie","data_path":"movies[*].title"},
        {"name":"ROI","data_path":"movies[*].roi"}
    ]
}

⚠️  CRITICAL - Response example for SINGLE-ITEM NESTED ARRAY (one item with time-series):
When user asks "weekly box office for Toy Story", "daily revenue for The Matrix" → USE chartType="line"

CORRECT EXAMPLE (one movie with nested weeklyBoxOffice array):
{
    "title": "Weekly Box Office for Toy Story",
    "reasonForTheComponentSelection": "User wants to view weekly box office data for a specific movie",
    "confidenceScore": "95%",
    "component": "chart",
    "chartType": "line",
    "fields" : [
        {"name":"Week","data_path":"movie.weeklyBoxOffice[*].week"},
        {"name":"Revenue","data_path":"movie.weeklyBoxOffice[*].revenue"}
    ]
}

CRITICAL: For SINGLE item with nested array, use simple paths like "movie.weeklyBoxOffice[*].week"
DO NOT use complex paths like "['search_movie[size up to 6]'][0]['movie']..." - that is INVALID!

⚠️  CRITICAL - Response example for NESTED TIME-SERIES (weekly/daily trends):
When user asks "weekly revenue trends", "compare trends", "compare weekly/daily" → USE chartType="line"

CORRECT EXAMPLE (multiple movies comparing weekly trends):
{
    "title": "Weekly Revenue Trends",
    "component": "chart",
    "chartType": "line",
    "fields" : [
        {"name":"Movie","data_path":"movies[*].title"},
        {"name":"Week","data_path":"movies[*].weeklyBoxOffice[*].week"},
        {"name":"Revenue","data_path":"movies[*].weeklyBoxOffice[*].revenue"}
    ]
}

❌ WRONG - DO NOT DO THIS:
{
    "fields" : [
        {"name":"Week","data_path":"movies[*].weeklyBoxOffice[*].week"},  ← NO! Week should NOT be first
        {"name":"Revenue","data_path":"movies[*].revenue"}  ← NO! Use weeklyBoxOffice[*].revenue, not revenue
    ]
}

✅ CORRECT FIELD ORDER (memorize this):
1. movies[*].title → Series names: "The Dark Knight", "Inception" (one line per movie)
2. movies[*].weeklyBoxOffice[*].week → X-axis: 1, 2, 3, 4
3. movies[*].weeklyBoxOffice[*].revenue → Y-axis: 158411483, 75165786, ...

CRITICAL - Contrasting example for MIRRORED-BAR (comparing TWO metrics side-by-side):
When user asks to "compare revenue and profit", "ROI vs budget", "compare metric A and metric B" - USE MIRRORED-BAR (not line chart):
{
    "title": "ROI vs Budget Comparison",
    "reasonForTheComponentSelection": "User wants to compare two different metrics side-by-side",
    "confidenceScore": "90%",
    "component": "chart",
    "chartType": "mirrored-bar",
    "fields" : [
        {"name":"Movie","data_path":"movies[*].title"},
        {"name":"ROI","data_path":"movies[*].roi"},
        {"name":"Budget","data_path":"movies[*].budget"}
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
