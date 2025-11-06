"""Shared LLM prompt instructions for component selection.

This module provides consistent prompt templates and instructions across
different component selection strategies (one-step and two-step).
"""

# Component selection step 1 instructions (selecting which component to use)
COMPONENT_SELECTION_BASE_INSTRUCTIONS = """You are helpful and advanced user interface design assistant.
Based on the "User query" and JSON formatted "Data", select the best UI component to show the "Data" to the user.
Generate response in the JSON format only. Select one UI component only. Put it into "component".
Provide reason for the UI component selection in the "reasonForTheComponentSelection".
Provide your confidence for the UI component selection as a percentage in the "confidenceScore".
Provide title for the UI component in "title".
"""

# Field selection step 2 instructions (selecting which fields to display)
FIELD_SELECTION_BASE_INSTRUCTIONS = """You are helpful and advanced user interface design assistant.
Based on the "User query" and JSON formatted "Data", select the best fields to show the "Data" to the user in the UI component {component}.
Generate JSON array of objects only.
Provide list of "fields" to be visualized in the UI component.
Select only relevant "Data" fields to be presented in the UI component. Do not bloat presentation. Show all the important info about the data item. Mainly include information the user asks for in "User query".
Provide reason for the every field selection in the "reason".
Provide your confidence for the every field selection as a percentage in the "confidenceScore".
Provide "name" for every field.
For every field provide "data_path" containing path to get the value from the "Data". Do not use formatting or calculation in the "data_path".
"""

# One-step strategy instructions (combined component + field selection)
ONESTEP_BASE_INSTRUCTIONS = """You are helpful and advanced user interface design assistant. Based on the "User query" and JSON formatted "Data", select the best UI component to visualize the "Data" to the user.
Generate response in the JSON format only. Select one component only into "component".
Provide the title for the component in "title".
Provide reason for the component selection in the "reasonForTheComponentSelection".
Provide your confidence for the component selection as a percentage in the "confidenceScore".
Provide list of "fields" to be visualized in the UI component. Select only relevant data fields to be presented in the component. Do not bloat presentation. Show all the important info about the data item. Mainly include information the user asks for in User query.
If the selected UI component requires specific fields mentioned in its description, provide them. Provide "name" for every field.
For every field provide "data_path" containing JSONPath to get the value from the Data. Do not use any formatting or calculation in the "data_path".
"""

# Response examples for component selection (step 1)
COMPONENT_SELECTION_EXAMPLES = """
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

# Response examples for one-step strategy (combined)
ONESTEP_RESPONSE_EXAMPLES = """
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
"""

# Component-specific extensions for field selection
COMPONENT_EXTENSIONS = {
    "image": """Provide one field only in the list, containing url of the image to be shown, taken from the "Data".""",
    "video-player": """Provide one field only in the list, containing url of the video to be played, taken from the "Data".""",
    "one-card": """Value the "data_path" points to must be either simple value or array of simple values. Do not point to objects in the "data_path".
Do not use the same "data_path" for multiple fields.
One field can point to the large image shown as the main image in the card UI, if url is available in the "Data".
Show ID value only if it seems important for the user, like order ID. Do not show ID value if it is not important for the user.""",
}

# Component-specific examples for field selection
COMPONENT_EXAMPLES = {
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
    "video-player": """⚠️  CRITICAL: video-player REQUIRES a field with data_path pointing to the video URL!

Response example 1:
[
    {
        "reason": "video-player UI component is used, so we MUST provide video url",
        "confidenceScore": "98%",
        "name": "Trailer",
        "data_path": "movie.trailerUrl"
    }
]

Response example 2 (with tool response structure):
[
    {
        "reason": "video-player UI component is used, so we MUST provide video url from the data",
        "confidenceScore": "98%",
        "name": "Trailer URL",
        "data_path": "search_movie[size up to 6][*].movie.trailerUrl"
    }
]

CRITICAL: The video-player component will NOT work without a field pointing to a URL field like trailerUrl, videoUrl, video, or url.
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
    "table": """Response example 1 (simple structure):
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

Response example 2 (tool response with size annotation - USE EXACT STRUCTURE):
⚠️  When Data has "get_all_movies[size up to 6]" structure, use EXACT key:
[
    {
        "reason": "User wants to see movie titles",
        "confidenceScore": "98%",
        "name": "Title",
        "data_path": "get_all_movies[size up to 6][*].movie.title"
    },
    {
        "reason": "User wants to see release year",
        "confidenceScore": "95%",
        "name": "Year",
        "data_path": "get_all_movies[size up to 6][*].movie.year"
    },
    {
        "reason": "User wants to see rating",
        "confidenceScore": "92%",
        "name": "Rating",
        "data_path": "get_all_movies[size up to 6][*].movie.imdbRating"
    }
]
CRITICAL: Use "get_all_movies[size up to 6][*].movie.title" NOT "movies[*].title" or "get_all_movies[*].title"
""",
    "chart": """⚠️  CRITICAL: For PIE/DONUT charts (distributions), provide ONLY ONE field - the backend auto-counts!
⚠️  DO NOT calculate or aggregate - just pass the raw field path!

Response example 1 - PIE/DONUT (genre distribution):
⚠️  ONLY ONE field! Backend counts how many times each value appears.
[
    {
        "reason": "User wants to see genre distribution - backend will count occurrences automatically",
        "confidenceScore": "98%",
        "name": "Genre",
        "data_path": "get_all_movies[size up to 6][*].movie.genres[*]"
    }
]

CRITICAL for distributions:
- Use [*] to extract individual array elements (e.g., genres[*] extracts each genre string)
- Backend automatically counts and creates the pie chart
- DO NOT add a count field - this is automatic!
- DO NOT add a second field with item names - only the category field!

Response example 2 - Simple comparison (bar/pie/donut chart):
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

Response example 3 - SINGLE-ITEM NESTED ARRAY (one item with time-series):
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

Response example 4 - NESTED TIME-SERIES (periodic trends):
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

Response example 5 - MIRRORED-BAR (comparing TWO metrics side-by-side):
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


def get_component_extension(component: str) -> str:
    """Get component-specific extension instructions for field selection."""
    return COMPONENT_EXTENSIONS.get(component, "")


def get_component_examples(component: str) -> str:
    """Get component-specific examples for field selection."""
    return COMPONENT_EXAMPLES.get(component, "")
