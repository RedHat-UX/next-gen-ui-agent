"""LLM prompts for intelligent data filtering."""


def get_data_filter_analysis_prompt(
    data_sample: str, data_count: int, user_query: str
) -> str:
    """
    Generate prompt for LLM to analyze user query and determine filtering needs.

    Args:
        data_sample: JSON sample of the data structure
        data_count: Total number of data items
        user_query: The user's natural language query

    Returns:
        Formatted prompt string for LLM
    """
    return f"""You are a universal data filtering expert. Analyze the user's query against the provided data structure.

**Your Task:** Determine if the user wants ALL data items or SPECIFIC filtered items.

**Data Context:**
- Total items: {data_count}
- Sample structure:
```json
{data_sample}
```

**User Query:** "{user_query}"

**Decision Rules:**

1️⃣ **SHOW ALL (should_filter: false)** - Choose when query indicates wanting to see EVERYTHING:
   - Uses plural/collective language: "show items", "list all", "display data"
   - Asks about a category without specifying particular items
   - Requests visualization: "in a table", "as cards", "chart of"
   - No specific identifiers mentioned (names, IDs, unique values)

2️⃣ **FILTER SPECIFIC (should_filter: true)** - Choose when query asks for SUBSET:
   - Mentions specific identifier: name, ID, email, title, exact value
   - Includes filter criteria: "from year X", "with role Y", "where Z"
   - Comparisons: "compare A and B", "difference between X and Y"
   - Singular reference to known item: "tell me about [specific_item]"

**IMPORTANT:** When ambiguous or uncertain, default to "all" (show all data).

**Response Format (JSON only):**
{{
    "query_type": "specific" or "all",
    "filter_instructions": "Describe filtering criteria or 'show all items'",
    "should_filter": true or false,
    "explanation": "Brief reason for decision"
}}

**Universal Examples:**
- "Show employee John Doe" → specific (named individual)
- "List all employees" → all (requesting full dataset)
- "Items from 2024" → specific (year filter)
- "Display the data" → all (generic display request)
- "Compare X and Y" → specific (two items to compare)
"""


def get_data_filter_execution_prompt(
    data_json: str, user_query: str, filter_instructions: str
) -> str:
    """
    Generate prompt for LLM to perform actual data filtering.

    Args:
        data_json: Full JSON data to filter
        user_query: The user's natural language query
        filter_instructions: Instructions from analysis phase

    Returns:
        Formatted prompt string for LLM
    """
    return f"""Given this data and user query, return ONLY the items that match the query.

Data:
```json
{data_json}
```

User query: "{user_query}"
Filter instructions: {filter_instructions}

Return ONLY the filtered data as valid JSON (array or object). Do not include any explanation, just the filtered data.
If no items match, return an empty array [].
"""
