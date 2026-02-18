"""Data filtering utilities using LLM."""

import json
from typing import Any, Callable, Optional

from app.models import DataFilterResult
from app.prompts import get_data_filter_analysis_prompt


async def generic_data_filter_agent(
    prompt: str,
    data: Any,
    filter_llm_callable: Callable[[str], Any],
) -> Optional[Any]:
    """
    Generic intelligent data filtering agent that works with ANY data type.
    Analyzes user query and filters data accordingly.
    Uses filter_llm_callable(prompt_str) for LLM calls (works with local LLM or LlamaStack).

    Works for:
    - Movies data
    - Cost efficiency data
    - RBAC permissions
    - Any JSON data structure

    Returns filtered data or all data if query is general.
    """
    if not data:
        return None

    print(f"Data Filter Agent analyzing query: '{prompt}'")

    data_sample = json.dumps(
        data[0] if isinstance(data, list) and len(data) > 0 else data, indent=2
    )[:500]
    data_count = len(data) if isinstance(data, list) else 1

    analysis_prompt = get_data_filter_analysis_prompt(data_sample, data_count, prompt)

    try:
        # Call LLM to analyze the query (local or LlamaStack via callable)
        response_content = await filter_llm_callable(analysis_prompt)
        if hasattr(response_content, "completion_message"):
            response_content = response_content.completion_message.content
        elif not isinstance(response_content, str):
            response_content = str(response_content)
        print(f"Filter Agent LLM response: {response_content[:200]}...")

        # Parse JSON response
        if "```json" in response_content:
            json_start = response_content.find("```json") + 7
            json_end = response_content.find("```", json_start)
            json_str = response_content[json_start:json_end].strip()
        elif "```" in response_content:
            json_start = response_content.find("```") + 3
            json_end = response_content.find("```", json_start)
            json_str = response_content[json_start:json_end].strip()
        else:
            json_str = response_content.strip()

        result = json.loads(json_str)
        filter_result = DataFilterResult(**result)

        print(f"Query type: {filter_result.query_type}")
        print(f"Should filter: {filter_result.should_filter}")
        print(f"Explanation: {filter_result.explanation}")

        if not filter_result.should_filter or filter_result.query_type == "all":
            print("Returning all data (no filtering)")
            return data

        # Apply filtering
        print("Applying intelligent filtering...")
        filter_prompt = f"""Given this data and user query, return ONLY the items that match the query.

Data:
```json
{json.dumps(data, indent=2)}
```

User query: "{prompt}"
Filter instructions: {filter_result.filter_instructions}

Return ONLY the filtered data as valid JSON (array or object). Do not include any explanation, just the filtered data.
If no items match, return an empty array [].
"""

        filtered_content = await filter_llm_callable(filter_prompt)
        if hasattr(filtered_content, "completion_message"):
            filtered_content = filtered_content.completion_message.content
        elif not isinstance(filtered_content, str):
            filtered_content = str(filtered_content)

        # Parse filtered data
        if "```json" in filtered_content:
            json_start = filtered_content.find("```json") + 7
            json_end = filtered_content.find("```", json_start)
            filtered_json_str = filtered_content[json_start:json_end].strip()
        elif "```" in filtered_content:
            json_start = filtered_content.find("```") + 3
            json_end = filtered_content.find("```", json_start)
            filtered_json_str = filtered_content[json_start:json_end].strip()
        else:
            filtered_json_str = filtered_content.strip()

        filtered_data = json.loads(filtered_json_str)

        if isinstance(filtered_data, list):
            print(f"Filtered to {len(filtered_data)} item(s)")
        else:
            print("Filtered data returned")

        # If filtering returned empty, use all data
        if (
            isinstance(filtered_data, list) and len(filtered_data) == 0
        ) or not filtered_data:
            print("Filtering returned empty, using all data")
            return data

        return filtered_data

    except json.JSONDecodeError as e:
        print(f"Failed to parse filter agent response: {e}")
        print("Falling back to all data")
        return data
    except Exception as e:
        print(f"Filter agent error: {e}")
        print("Falling back to all data")
        return data
