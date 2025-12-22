"""Common instructions and constants shared between component selection strategies.

This module provides reusable prompt components and examples for LLM-based
component selection strategies. The public API is organized by strategy type.
"""

from next_gen_ui_agent.data_transform.chart import (
    BarChartDataTransformer,
    DonutChartDataTransformer,
    LineChartDataTransformer,
    MirroredBarChartDataTransformer,
    PieChartDataTransformer,
)
from next_gen_ui_agent.data_transform.image import ImageDataTransformer
from next_gen_ui_agent.data_transform.one_card import OneCardDataTransformer
from next_gen_ui_agent.data_transform.set_of_cards import SetOfCardsDataTransformer
from next_gen_ui_agent.data_transform.table import TableDataTransformer
from next_gen_ui_agent.data_transform.video import VideoPlayerDataTransformer
from next_gen_ui_agent.types import CONFIG_OPTIONS_ALL_COMPONETS

# ============================================================================
# SECTION 1: Shared Utilities (Public API)
# ============================================================================


def get_all_components_description() -> str:
    """
    Get complete description of all UI components.

    This function builds the component descriptions from COMPONENT_METADATA.
    Used primarily for AI evaluation and documentation purposes.

    Returns:
        Formatted string with all component descriptions
    """
    return build_components_description(set(COMPONENT_METADATA.keys()))


def get_all_chart_instructions() -> str:
    """
    Get complete chart instructions for all chart types.

    This function builds the chart instructions from COMPONENT_METADATA.
    Used primarily for AI evaluation and documentation purposes.

    Returns:
        Formatted string with chart instructions for all chart types
    """
    return build_chart_instructions(CHART_COMPONENTS)


# ============================================================================
# SECTION 2: Internal Building Blocks (Private - not imported by strategies)
# ============================================================================
_COMMON_RULES = """RULES:
- Generate JSON only
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
{_COMMON_FIELD_SELECTION_RULES}

{_JSONPATH_REQUIREMENTS}"""

# ============================================================================
# SECTION 4: Two-Step Strategy (Public API)
# ============================================================================
TWOSTEP_STEP1_PROMPT_RULES = f"""{_COMMON_RULES}

{_JSONPATH_REQUIREMENTS}"""

TWOSTEP_STEP2_PROMPT_RULES = f"""RULES:
- Generate JSON array of objects only
{_COMMON_FIELD_SELECTION_RULES}
- Each field must also have "reason" and "confidenceScore" (percentage)

{_JSONPATH_REQUIREMENTS}"""

# ============================================================================
# SECTION 5: Unified Component Metadata (Public API)
# ============================================================================

# Ordered list of all component names (for consistent display order)
# Using COMPONENT_NAME constants from transformer classes ensures single source of truth
ALL_COMPONENTS = [
    OneCardDataTransformer.COMPONENT_NAME,
    ImageDataTransformer.COMPONENT_NAME,
    VideoPlayerDataTransformer.COMPONENT_NAME,
    TableDataTransformer.COMPONENT_NAME,
    SetOfCardsDataTransformer.COMPONENT_NAME,
    BarChartDataTransformer.COMPONENT_NAME,
    LineChartDataTransformer.COMPONENT_NAME,
    PieChartDataTransformer.COMPONENT_NAME,
    DonutChartDataTransformer.COMPONENT_NAME,
    MirroredBarChartDataTransformer.COMPONENT_NAME,
]

# Set of chart component names for easy detection
# Using COMPONENT_NAME constants from transformer classes ensures single source of truth
CHART_COMPONENTS = {
    BarChartDataTransformer.COMPONENT_NAME,
    LineChartDataTransformer.COMPONENT_NAME,
    PieChartDataTransformer.COMPONENT_NAME,
    DonutChartDataTransformer.COMPONENT_NAME,
    MirroredBarChartDataTransformer.COMPONENT_NAME,
}

# Common rules applying to all chart types
CHART_COMMON_RULES = """- Don't add unrequested metrics
- Line charts: Use standard pattern when showing multiple different metrics. Use multi-series pattern when showing same metric for different entities."""

# Unified component metadata containing all information for both strategies
COMPONENT_METADATA = {
    "one-card": {
        "description": "component to visualize multiple fields from one-item data. One image can be shown if url is available together with other fields. Array of simple values from one-item data can be shown as a field. Array of objects can't be shown as a field.",
        "twostep_step2_example": '[{"reason":"It is always good to show order name","confidenceScore":"98%","name":"Name","data_path":"order.name"},{"reason":"It is generally good to show order date","confidenceScore":"94%","name":"Order date","data_path":"order.createdDate"},{"reason":"User asked to see the order status","confidenceScore":"98%","name":"Order status","data_path":"order.status.name"}]',
        "twostep_step2_extension": 'Value the "data_path" points to must be either simple value or array of simple values. Do not point to objects in the "data_path".\nDo not use the same "data_path" for multiple fields.\nOne field can point to the large image shown as the main image in the card UI, if url is available in the "Data".\nShow ID value only if it seems important for the user, like order ID. Do not show ID value if it is not important for the user.',
    },
    "image": {
        "description": "component to show one image from one-item data. Images like posters, covers, pictures. Do not use for video! Select it if no other fields are necessary to be shown. Data must contain url pointing to the image to be shown, e.g. https://www.images.com/v-PjgYDrg70.jpeg",
        "twostep_step2_example": '[{"reason":"image UI component is used, so we have to provide image url","confidenceScore":"98%","name":"Image Url","data_path":"order.pictureUrl"}]',
        "twostep_step2_extension": 'Provide one field only in the list, containing url of the image to be shown, taken from the "Data".',
    },
    "video-player": {
        "description": "component to play video from one-item data. Videos like trailers, promo videos. Data must contain url pointing to the video to be shown, e.g. https://www.youtube.com/watch?v=v-PjgYDrg70",
        "twostep_step2_example": '[{"reason":"video-player UI component is used, so we have to provide video url","confidenceScore":"98%","name":"Video Url","data_path":"order.trailerUrl"}]',
        "twostep_step2_extension": 'Provide one field only in the list, containing url of the video to be played, taken from the "Data".',
    },
    "table": {
        "description": "component to visualize array of objects with multiple items (typically 3 or more) in a tabular format. Use when user explicitly requests a table, or for data with many items (especially >6), small number of fields, and short values.",
        "twostep_step2_example": '[{"reason":"It is always good to show order name","confidenceScore":"98%","name":"Name","data_path":"order[].name"},{"reason":"It is generally good to show order date","confidenceScore":"94%","name":"Order date","data_path":"order[].createdDate"},{"reason":"User asked to see the order status","confidenceScore":"98%","name":"Order status","data_path":"order[].status.name"}]',
    },
    "set-of-cards": {
        "description": "component to visualize array of objects with multiple items. Use for data with fewer items (<6), high number of fields, or fields with long values. Also good when visual separation between items is important.",
        "twostep_step2_example": '[{"reason":"It is always good to show product name","confidenceScore":"98%","name":"Name","data_path":"products[].name"},{"reason":"Product description provides important context","confidenceScore":"92%","name":"Description","data_path":"products[].description"},{"reason":"Price is essential information for products","confidenceScore":"95%","name":"Price","data_path":"products[].price"}]',
    },
    "chart-bar": {
        "description": "component to visualize numeric data as a bar chart. Use for comparing one metric across categories.",
        "twostep_step2_example": '[{"name":"Movie","data_path":"movies[*].title"},{"name":"Revenue","data_path":"movies[*].revenue"}]',
        "twostep_step2_extension": "FIELDS: chart-bar=2 [category,metric]",
        "chart_description": "Compare 1 metric across items",
        "chart_fields_spec": "[category, metric]",
        "chart_rules": "",
        "chart_inline_examples": 'Bar (vertical): {"component":"chart-bar","fields":[{"name":"Item","data_path":"items[*].name"},{"name":"Score","data_path":"items[*].score"}]}\nBar (nested): {"component":"chart-bar","fields":[{"name":"Item","data_path":"items[*].product.name"},{"name":"Sales","data_path":"items[*].product.sales"}]}',
    },
    "chart-line": {
        "description": "component to visualize numeric data as a line chart. Use for trends over time or continuous data.",
        "twostep_step2_example": '[{"name":"Month","data_path":"data[*].month"},{"name":"Revenue","data_path":"data[*].revenue"}]',
        "twostep_step2_extension": "FIELDS: chart-line=2+ [time/x-axis,metric1,metric2,...] OR 3 [entity_id,time/x-axis,metric] for multi-series\nLine: Use standard pattern [time,metric1,metric2] for multiple metrics, or [entity_id,time,metric] for same metric across entities.",
        "chart_description": "Time-series, trends over time",
        "chart_fields_spec": "Two patterns:\n  - Standard: [time/x-axis, metric1, metric2, ...] - Multiple metrics over same x-axis\n  - Multi-series: [entity_id, time/x-axis, metric] - Same metric across different entities",
        "chart_rules": "Use standard pattern when showing multiple different metrics. Use multi-series pattern when showing same metric for different entities.",
        "chart_inline_examples": 'Line (standard, 2 metrics): {"component":"chart-line","fields":[{"name":"Month","data_path":"data[*].month"},{"name":"Sales","data_path":"data[*].sales"},{"name":"Profit","data_path":"data[*].profit"}]}\nLine (standard, 1 metric): {"component":"chart-line","fields":[{"name":"Month","data_path":"data[*].month"},{"name":"Revenue","data_path":"data[*].revenue"}]}\nLine (multi-series): {"component":"chart-line","fields":[{"name":"Movie","data_path":"items[*].movieTitle"},{"name":"Week","data_path":"items[*].week"},{"name":"Revenue","data_path":"items[*].revenue"}]}',
    },
    "chart-pie": {
        "description": "component to visualize data distribution as a pie chart. Use for showing proportions or percentages.",
        "twostep_step2_example": '[{"name":"Genre","data_path":"movies[*].genres"}]',
        "twostep_step2_extension": "FIELDS: chart-pie=1 [category]\nPie: backend counts, use [*] for arrays.",
        "chart_description": "Distribution of 1 categorical field",
        "chart_fields_spec": "[category] - backend auto-counts, don't add count field",
        "chart_rules": "",
        "chart_inline_examples": 'Pie: {"component":"chart-pie","fields":[{"name":"Genre","data_path":"items[*].genres"}]}',
    },
    "chart-donut": {
        "description": "component to visualize data distribution as a donut chart. Use for showing proportions with a central metric.",
        "twostep_step2_example": '[{"name":"Category","data_path":"movies[*].category"}]',
        "twostep_step2_extension": "FIELDS: chart-donut=1 [category]\nDonut: backend counts, use [*] for arrays.",
        "chart_description": "Distribution of 1 categorical field",
        "chart_fields_spec": "[category] - backend auto-counts, don't add count field",
        "chart_rules": "",
        "chart_inline_examples": 'Donut: {"component":"chart-donut","fields":[{"name":"Category","data_path":"items[*].category"}]}',
    },
    "chart-mirrored-bar": {
        "description": "component to visualize two metrics side-by-side as mirrored bars. Use for comparing two metrics across categories.",
        "twostep_step2_example": '[{"name":"Movie","data_path":"get_all_movies[*].movie.title"},{"name":"ROI","data_path":"get_all_movies[*].movie.roi"},{"name":"Budget","data_path":"get_all_movies[*].movie.budget"}]',
        "twostep_step2_extension": "FIELDS: chart-mirrored-bar=3 [category,metric1,metric2]",
        "chart_description": 'Compare 2 metrics side-by-side (e.g., "A and B", "A vs B", different scales)',
        "chart_fields_spec": "[category, metric1, metric2]",
        "chart_rules": "",
        "chart_inline_examples": 'Mirrored: {"component":"chart-mirrored-bar","fields":[{"name":"Item","data_path":"items[*].name"},{"name":"A","data_path":"items[*].a"},{"name":"B","data_path":"items[*].b"}]}',
    },
}


def normalize_allowed_components(
    allowed_components: CONFIG_OPTIONS_ALL_COMPONETS,
) -> set[str]:
    """
    Normalize allowed_components to a set of strings.

    Args:
        allowed_components: Set of allowed component names, or None for all components

    Returns:
        Set of allowed component names
    """
    if allowed_components is None:
        return set(COMPONENT_METADATA.keys())
    return allowed_components  # type: ignore


def has_chart_components(allowed_components: set[str]) -> bool:
    """
    Check if any chart component is in the allowed components.

    Args:
        allowed_components: Set of allowed component names

    Returns:
        True if any chart component is present, False otherwise
    """
    return bool(allowed_components & CHART_COMPONENTS)


def has_non_chart_components(allowed_components: set[str]) -> bool:
    """
    Check if any non-chart component is in the allowed components.

    Args:
        allowed_components: Set of allowed component names

    Returns:
        True if any non-chart component is present, False otherwise
    """
    return bool(allowed_components - CHART_COMPONENTS)


def build_components_description(
    allowed_components: set[str],
) -> str:
    """
    Build filtered component descriptions based on allowed components.

    Args:
        allowed_components: Set of allowed component names, or None for all components

    Returns:
        Formatted string with component descriptions
    """

    descriptions = []
    for component in ALL_COMPONENTS:
        if component in allowed_components:
            descriptions.append(
                f"* {component} - {COMPONENT_METADATA[component]['description']}"
            )

    return "\n".join(descriptions)


def build_onestep_examples(
    allowed_components: set[str],
) -> str:
    """
    Build filtered one-step strategy examples based on allowed components.

    Args:
        allowed_components: Set of allowed component names, preprocessed by `normalize_allowed_components` function

    Returns:
        Formatted string with response examples
    """

    examples = []

    if has_non_chart_components(allowed_components):

        examples.append(
            """Response example for multi-item data:
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
}"""
        )

    if has_chart_components(allowed_components):

        examples.append(
            """Response example for bar chart:
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
        )

    return "\n\n".join(examples)


def build_twostep_step1_examples(
    allowed_components: set[str],
) -> str:
    """
    Build filtered two-step step-1 strategy examples based on allowed components.

    Args:
        allowed_components: Set of allowed component names, preprocessed by `normalize_allowed_components` function

    Returns:
        Formatted string with response examples
    """

    examples = []

    if has_non_chart_components(allowed_components):

        examples.append(
            """Response example for multi-item data:
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
}"""
        )

    if has_chart_components(allowed_components):

        examples.append(
            """Response example for bar chart:
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
        )

    return "\n\n".join(examples)


def build_twostep_step2_example(component: str) -> str:
    """
    Get step-2 field example for the selected component.

    Args:
        component: Component name

    Returns:
        Field selection example string or empty string if not found
    """
    if component in COMPONENT_METADATA:
        return COMPONENT_METADATA[component].get("twostep_step2_example", "")
    return ""


def build_twostep_step2_extension(component: str) -> str:
    """
    Get step-2 field selection rules/extensions for the component.

    Args:
        component: Component name

    Returns:
        Field selection extension string or empty string if not found
    """
    if component in COMPONENT_METADATA:
        return COMPONENT_METADATA[component].get("twostep_step2_extension", "")
    return ""


def build_chart_instructions(allowed_chart_components: set[str]) -> str:
    """
    Build filtered chart instructions for component selection based on allowed chart components.

    Args:
        allowed_chart_components: Set of allowed chart component names

    Returns:
        Formatted string with chart instructions or empty string if no charts
    """
    if not allowed_chart_components:
        return ""

    # Get chart components in the canonical order from ALL_COMPONENTS
    chart_components_ordered = [c for c in ALL_COMPONENTS if c in CHART_COMPONENTS]

    # Build CHART TYPES section
    chart_types = []
    for chart_comp in chart_components_ordered:
        if chart_comp in allowed_chart_components:
            chart_types.append(
                f"{chart_comp}: {COMPONENT_METADATA[chart_comp]['chart_description']}"
            )

    # Build FIELDS BY TYPE section
    fields_by_type = []
    for chart_comp in chart_components_ordered:
        if chart_comp in allowed_chart_components:
            fields_spec = COMPONENT_METADATA[chart_comp]["chart_fields_spec"]
            if chart_comp == "chart-line":
                # Special formatting for chart-line
                fields_by_type.append(f"{chart_comp}: {fields_spec}")
            elif chart_comp in ["chart-pie", "chart-donut"]:
                # Group pie and donut together
                if "chart-pie/chart-donut:" not in "\n".join(fields_by_type):
                    fields_by_type.append(f"chart-pie/chart-donut: {fields_spec}")
            else:
                fields_by_type.append(f"{chart_comp}: {fields_spec}")

    # Build EXAMPLES section
    examples = []
    for chart_comp in chart_components_ordered:
        if chart_comp in allowed_chart_components:
            inline_examples = COMPONENT_METADATA[chart_comp]["chart_inline_examples"]
            examples.append(inline_examples)

    # Construct the full instruction string
    instruction_parts = [
        "CHART TYPES (count ONLY metrics user requests):",
        "\n".join(chart_types),
        "",
        "FIELDS BY CHART TYPE:",
        "\n".join(fields_by_type),
        "",
        "CHART RULES:",
        CHART_COMMON_RULES,
        "",
        "CHART EXAMPLES:",
        "\n".join(examples),
    ]

    return "\n".join(instruction_parts)
