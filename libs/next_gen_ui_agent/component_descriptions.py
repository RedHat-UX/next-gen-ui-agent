"""Shared UI component descriptions for LLM prompts.

This module provides consistent component descriptions across different
component selection strategies (one-step and two-step).
"""

# Core components that are always supported
UI_COMPONENTS_DESCRIPTION_SUPPORTED = """
* one-card - component to visualize multiple fields from one-item Data. One image can be shown if url is available together with other fields. Array of simple values from one-item data can be shown as a field. Array of objects can't be shown as a field.
* video-player - component to play video from one-item Data. Videos like trailers, promo videos. Data must contain url pointing to the video to be shown, e.g. https://www.youtube.com/watch?v=v-PjgYDrg70. REQUIRED: You MUST include a field with data_path pointing to the video URL (e.g., trailerUrl, videoUrl, video, url)
* image - component to show one image from one-item Data. Images like posters, covers, pictures. Do not use for video! Select it if no other fields are necessary to be shown. Data must contain url pointing to the image to be shown, e.g. https://www.images.com/v-PjgYDrg70.jpeg
* chart - component to visualize numeric Data. IMPORTANT: component name is always "chart", then specify chart type separately using "chartType" field (values: "bar", "line", "pie", "donut", "mirrored-bar"). See detailed CHART COMPONENT RULES below.
""".strip()

# Additional components for advanced use cases
UI_COMPONENTS_DESCRIPTION_ADDITIONAL = """
* table - component to visualize multi-item Data. Use it for Data with more than 6 items, small number of fields to be shown, and fields with short values.
* set-of-cards - component to visualize multi-item Data. Use it for Data with less than 6 items, high number of fields to be shown, and fields with long values.
""".strip()

# All components including experimental/advanced ones
UI_COMPONENTS_DESCRIPTION_ALL = (
    UI_COMPONENTS_DESCRIPTION_SUPPORTED + "\n" + UI_COMPONENTS_DESCRIPTION_ADDITIONAL
)


def get_ui_components_description(unsupported_components: bool) -> str:
    """Get UI components description for system prompt.

    Args:
        unsupported_components: If True, include all components (table, set-of-cards).
                                If False, only include core supported components.

    Returns:
        String containing component descriptions for LLM prompt.
    """
    if unsupported_components:
        return UI_COMPONENTS_DESCRIPTION_ALL
    else:
        return UI_COMPONENTS_DESCRIPTION_SUPPORTED
