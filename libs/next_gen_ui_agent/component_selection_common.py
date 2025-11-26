"""Common instructions and constants shared between component selection strategies.

This module provides reusable prompt components and examples for LLM-based
component selection strategies. The public API is organized by strategy type.
"""

# ============================================================================
# SECTION 1: Shared Utilities (Public API)
# ============================================================================
UI_COMPONENTS_DESCRIPTION_SUPPORTED = """
* one-card - component to visualize multiple fields from one-item data. One image can be shown if url is available together with other fields. Array of simple values from one-item data can be shown as a field. Array of objects can't be shown as a field.
* video-player - component to play video from one-item data. Videos like trailers, promo videos. Data must contain url pointing to the video to be shown, e.g. https://www.youtube.com/watch?v=v-PjgYDrg70
* image - component to show one image from one-item data. Images like posters, covers, pictures. Do not use for video! Select it if no other fields are necessary to be shown. Data must contain url pointing to the image to be shown, e.g. https://www.images.com/v-PjgYDrg70.jpeg
* chart-bar - component to visualize numeric data as a bar chart. Use for comparing one metric across categories.
* chart-line - component to visualize numeric data as a line chart. Use for trends over time or continuous data.
* chart-pie - component to visualize data distribution as a pie chart. Use for showing proportions or percentages.
* chart-donut - component to visualize data distribution as a donut chart. Use for showing proportions with a central metric.
* chart-mirrored-bar - component to visualize two metrics side-by-side as mirrored bars. Use for comparing two metrics across categories.
""".strip()

UI_COMPONENTS_DESCRIPTION_ALL = (
    UI_COMPONENTS_DESCRIPTION_SUPPORTED
    + """
* table - component to visualize array of objects with multiple items (typically 3 or more) in a tabular format. Use when user explicitly requests a table, or for data with many items (especially >6), small number of fields, and short values.
* set-of-cards - component to visualize array of objects with multiple items. Use for data with fewer items (<6), high number of fields, or fields with long values. Also good when visual separation between items is important.
""".strip()
)


def get_ui_components_description(unsupported_components: bool) -> str:
    """Get UI components description for system prompt based on the unsupported_components flag."""
    if unsupported_components:
        return UI_COMPONENTS_DESCRIPTION_ALL
    else:
        return UI_COMPONENTS_DESCRIPTION_SUPPORTED


# ============================================================================
# SECTION 2: Internal Building Blocks (Private - not imported by strategies)
# ============================================================================
_COMMON_RULES = """RULES:
- If user explicitly requests a component type ("table", "chart", "cards"), USE IT unless data structure prevents it
- Select one component in "component" field
- Provide "title", "reasonForTheComponentSelection", "confidenceScore" (percentage)"""

_COMMON_FIELD_SELECTION_RULES = """- Select relevant Data fields based on User query
- Each field must have "name" and "data_path"
- Do not use formatting or calculations in "data_path"
"""

_JSONPATH_REQUIREMENTS = """JSONPATH REQUIREMENTS:
- Analyze actual Data structure carefully
- If fields are nested (e.g., items[*].movie.title), include full path
- Do NOT skip intermediate objects
- Use [*] for array access"""

# ============================================================================
# SECTION 3: One-Step Strategy (Public API)
# ============================================================================
ONESTEP_PROMPT_RULES = f"""{_COMMON_RULES}
- Generate JSON only
{_COMMON_FIELD_SELECTION_RULES}

{_JSONPATH_REQUIREMENTS}"""

ONESTEP_RESPONSE_EXAMPLES = """Response example for multi-item data:
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
    "component": "chart-bar",
    "fields" : [
        {{"name":"Movie","data_path":"movies[*].title"}},
        {{"name":"Revenue","data_path":"movies[*].revenue"}}
    ]
}

Response example for mirrored-bar chart (comparing 2 metrics, note nested structure):
{
    "title": "Movie ROI and Budget Comparison",
    "reasonForTheComponentSelection": "User wants to compare two metrics (ROI and budget) across movies, which requires a mirrored-bar chart to handle different scales",
    "confidenceScore": "90%",
    "component": "chart-mirrored-bar",
    "fields" : [
        {{"name":"Movie","data_path":"get_all_movies[*].movie.title"}},
        {{"name":"ROI","data_path":"get_all_movies[*].movie.roi"}},
        {{"name":"Budget","data_path":"get_all_movies[*].movie.budget"}}
    ]
}"""

# ============================================================================
# SECTION 4: Two-Step Strategy (Public API)
# ============================================================================
TWOSTEP_STEP1_PROMPT_RULES = f"""{_COMMON_RULES}

{_JSONPATH_REQUIREMENTS}"""

TWOSTEP_STEP1_RESPONSE_EXAMPLES = """Response example for multi-item data:
{
    "reasonForTheComponentSelection": "User explicitly requested a table, and data has multiple items with short field values",
    "confidenceScore": "95%",
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

Response example for bar chart:
{
    "title": "Movie Revenue Comparison",
    "reasonForTheComponentSelection": "User wants to compare numeric values as a chart",
    "confidenceScore": "90%",
    "component": "chart-bar"
}

Response example for mirrored-bar chart (comparing 2 metrics):
{
    "title": "Movie ROI and Budget Comparison",
    "reasonForTheComponentSelection": "User wants to compare two metrics (ROI and budget) across movies, which requires a mirrored-bar chart to handle different scales",
    "confidenceScore": "90%",
    "component": "chart-mirrored-bar"
}"""

TWOSTEP_STEP2_PROMPT_RULES = f"""RULES:
- Generate JSON array of objects only
{_COMMON_FIELD_SELECTION_RULES}
- Each field must also have "reason" and "confidenceScore" (percentage)

{_JSONPATH_REQUIREMENTS}"""
