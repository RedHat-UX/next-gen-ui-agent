"""Utilities for validating and extracting data from NGUI responses."""

import json
import re
from typing import Any, Optional

from utils.logging import log_error, log_info
from utils.response import create_error_response


def validate_ngui_response(
    ngui_response: Any, agent_messages: Optional[list] = None
) -> tuple[Optional[str], Optional[dict]]:
    """
    Validate NGUI response and extract component JSON.

    Returns:
        (component_json_str, error_response) - If validation succeeds, returns (json_str, None).
        If validation fails, returns (None, error_dict).
    """
    # Step 1: Check if response exists
    if not ngui_response:
        log_error("ERROR: NGUI response is None")
        return None, create_error_response(
            "No UI response",
            "NGUI agent returned None",
            ngui_response,
            agent_messages=agent_messages,
        )

    # Step 2: Check response type
    if not isinstance(ngui_response, dict):
        log_error("ERROR: NGUI response is not a dictionary")
        return None, create_error_response(
            "Invalid UI response format",
            f"Expected dictionary, got {type(ngui_response).__name__}",
            ngui_response,
            agent_messages=agent_messages,
        )

    # Step 3: Check for renditions key
    if "renditions" not in ngui_response:
        log_error("ERROR: No renditions key in NGUI response")
        return None, create_error_response(
            "Missing renditions",
            "NGUI response missing 'renditions' key",
            ngui_response,
            agent_messages=agent_messages,
        )

    # Step 4: Check renditions is not empty
    renditions = ngui_response["renditions"]
    if not renditions:
        log_error("ERROR: Empty renditions list")
        return None, create_error_response(
            "No UI components generated",
            "NGUI agent returned empty renditions array",
            agent_messages=agent_messages,
        )

    # Step 5: Check renditions is a list
    if not isinstance(renditions, list):
        log_error("ERROR: Renditions is not a list")
        return None, create_error_response(
            "Invalid renditions format",
            f"Expected list, got {type(renditions).__name__}",
            ngui_response,
            agent_messages=agent_messages,
        )

    # Step 6: Extract and validate rendition content
    first_rendition = renditions[0]
    log_info(f"First rendition type: {type(first_rendition)}")
    log_info(f"First rendition: {first_rendition}")

    # Handle both dict and Rendition object
    if isinstance(first_rendition, dict):
        rendition_content = first_rendition.get("content")
        log_info(f"Extracted content from dict: {rendition_content}")
    else:
        # Handle LangGraph Rendition object
        try:
            rendition_content = getattr(first_rendition, "content", None)
            log_info(f"Extracted content from object attribute: {rendition_content}")

            if rendition_content is None:
                # Try to access as string representation
                rendition_str = str(first_rendition)
                log_info(f"Rendition as string: {rendition_str}")

                # Extract content from string representation
                content_match = re.search(r"content='([^']*)'", rendition_str)
                if content_match:
                    rendition_content = content_match.group(1)
                    log_info(f"Extracted content from regex: {rendition_content}")
                else:
                    log_error("ERROR: Could not extract content from rendition string")
                    return None, create_error_response(
                        "Invalid rendition content",
                        "Could not extract content from rendition object",
                        first_rendition,
                        agent_messages=agent_messages,
                    )
        except Exception as e:
            log_error(f"ERROR: Failed to extract content from rendition: {e}")
            return None, create_error_response(
                "Invalid rendition format",
                f"Failed to extract content from rendition object: {str(e)}",
                first_rendition,
                agent_messages=agent_messages,
            )

    # Step 7: Validate content exists
    if not rendition_content:
        log_error("ERROR: No content in rendition")
        return None, create_error_response(
            "Empty component content",
            "Rendition missing 'content' field",
            first_rendition,
            agent_messages=agent_messages,
        )

    # Step 8: Validate content is string
    if not isinstance(rendition_content, str):
        log_error("ERROR: Rendition content is not a string")
        return None, create_error_response(
            "Invalid content format",
            f"Expected string, got {type(rendition_content).__name__}",
            rendition_content,
            agent_messages=agent_messages,
        )

    # Step 9: Validate content is not empty
    if not rendition_content.strip():
        log_error("ERROR: Rendition content is empty or whitespace")
        return None, create_error_response(
            "Empty component configuration",
            "Rendition content is empty or contains only whitespace",
            rendition_content,
            agent_messages=agent_messages,
        )

    log_info(f"Rendition content: {rendition_content}")

    # Step 10: Parse and validate JSON
    try:
        parsed_response = json.loads(rendition_content)
        log_info(f"Successfully parsed response: {parsed_response}")

        # Additional validation of parsed response
        if not isinstance(parsed_response, dict):
            return None, create_error_response(
                "Invalid component configuration",
                f"Component config must be an object, got {type(parsed_response).__name__}",
                rendition_content,
                agent_messages=agent_messages,
            )

        if not parsed_response:
            return None, create_error_response(
                "Empty component configuration",
                "Component configuration object is empty",
                rendition_content,
                agent_messages=agent_messages,
            )

        return rendition_content, None

    except json.JSONDecodeError as e:
        log_error(f"ERROR: Failed to parse JSON response: {e}")
        return None, create_error_response(
            "Invalid JSON configuration",
            f"JSON parse error: {str(e)}",
            rendition_content,
            "The component configuration is not valid JSON",
            agent_messages=agent_messages,
        )


def extract_component_metadata(
    ngui_response: dict,
    strategy: str,
    model_name: str,
    base_url: str,
    inline_data_context: Optional[dict] = None,
    agent_messages: Optional[list] = None,
) -> dict:
    """
    Extract metadata from NGUI response components.

    Args:
        ngui_response: The full NGUI agent response
        strategy: The component selection strategy used
        model_name: The LLM model name
        base_url: The LLM base URL
        inline_data_context: Optional context about inline data
        agent_messages: Optional agent messages for debugging

    Returns:
        Dictionary containing extracted metadata
    """
    metadata = {}
    components = ngui_response.get("components", [])

    if components and len(components) > 0:
        first_component = components[0]

        # Add reasoning and confidence if available
        if hasattr(first_component, "reasonForTheComponentSelection"):
            metadata["reason"] = first_component.reasonForTheComponentSelection
        if hasattr(first_component, "confidenceScore"):
            metadata["confidence"] = first_component.confidenceScore
        if hasattr(first_component, "component"):
            metadata["componentType"] = first_component.component

        # Add model information
        metadata["model"] = {"name": model_name, "baseUrl": base_url}

        # Add component selection strategy information
        metadata["strategy"] = strategy

        # Add data transformation information
        data_transform = {}
        if (
            hasattr(first_component, "input_data_transformer_name")
            and first_component.input_data_transformer_name
        ):
            data_transform["transformerName"] = (
                first_component.input_data_transformer_name
            )
        if (
            hasattr(first_component, "json_wrapping_field_name")
            and first_component.json_wrapping_field_name
        ):
            data_transform["jsonWrappingField"] = (
                first_component.json_wrapping_field_name
            )
        if hasattr(first_component, "fields") and first_component.fields:
            data_transform["fieldCount"] = len(first_component.fields)
            data_transform["fields"] = [
                {"name": field.name, "dataPath": field.data_path}
                for field in first_component.fields
            ]

        # Add inline data context if provided
        if inline_data_context:
            data_transform["inlineSource"] = inline_data_context["source"]
            if inline_data_context.get("recordCount") is not None:
                data_transform["inlineRecordCount"] = inline_data_context["recordCount"]
            if inline_data_context.get("payload") is not None:
                metadata["dataset"] = inline_data_context["payload"]

        if data_transform:
            metadata["dataTransform"] = data_transform

        # Add LLM interaction history for debugging
        if (
            hasattr(first_component, "llm_interactions")
            and first_component.llm_interactions
        ):
            metadata["llmInteractions"] = first_component.llm_interactions

        # Add agent messages for debugging
        if agent_messages:
            metadata["agentMessages"] = agent_messages

    return metadata
