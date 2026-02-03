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
    return build_components_description(
        set(COMPONENT_METADATA.keys()), COMPONENT_METADATA
    )


def get_all_chart_instructions() -> str:
    """
    Get complete chart instructions for all chart types.

    This function builds the chart instructions from COMPONENT_METADATA.
    Used primarily for AI evaluation and documentation purposes.

    Returns:
        Formatted string with chart instructions for all chart types
    """
    return build_chart_instructions(CHART_COMPONENTS, COMPONENT_METADATA)


# ============================================================================
# SECTION 2: Unified Component Metadata (Public API)
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

# Unified component metadata containing all information for both strategies
COMPONENT_METADATA = {
    "one-card": {
        "description": "component to visualize multiple fields from one-item data. One image can be shown if url is available together with other fields. Array of simple values from one-item data can be shown as a field. Array of objects can't be shown as a field.",
        "twostep_step2configure_example": '[{"reason":"It is always good to show order name","confidenceScore":"98%","name":"Name","data_path":"order.name"},{"reason":"It is generally good to show order date","confidenceScore":"94%","name":"Order date","data_path":"order.createdDate"},{"reason":"User asked to see the order status","confidenceScore":"98%","name":"Order status","data_path":"order.status.name"}]',
        "twostep_step2configure_rules": 'Value the "data_path" points to must be either simple value or array of simple values. Do not point to objects in the "data_path".\nDo not use the same "data_path" for multiple fields.\nOne field can point to the large image shown as the main image in the card UI, if url is available in the "Data".\nShow ID value only if it seems important for the user, like order ID. Do not show ID value if it is not important for the user.',
    },
    "image": {
        "description": "component to show one image from one-item data. Images like posters, covers, pictures. Do not use for video! Select it if no other fields are necessary to be shown. Data must contain url pointing to the image to be shown, e.g. https://www.images.com/v-PjgYDrg70.jpeg",
        "twostep_step2configure_example": '[{"reason":"image UI component is used, so we have to provide image url","confidenceScore":"98%","name":"Image Url","data_path":"order.pictureUrl"}]',
        "twostep_step2configure_rules": 'Provide one field only in the list, containing url of the image to be shown, taken from the "Data".',
    },
    "video-player": {
        "description": "component to play video from one-item data. Videos like trailers, promo videos. Data must contain url pointing to the video to be shown, e.g. https://www.youtube.com/watch?v=v-PjgYDrg70",
        "twostep_step2configure_example": '[{"reason":"video-player UI component is used, so we have to provide video url","confidenceScore":"98%","name":"Video Url","data_path":"order.trailerUrl"}]',
        "twostep_step2configure_rules": 'Provide one field only in the list, containing url of the video to be played, taken from the "Data".',
    },
    "table": {
        "description": "component to visualize array of objects with multiple items (typically 3 or more) in a tabular format. Use when user explicitly requests a table, or for data with many items (especially >6), small number of fields, and short values.",
        "twostep_step2configure_example": '[{"reason":"It is always good to show order name","confidenceScore":"98%","name":"Name","data_path":"order[].name"},{"reason":"It is generally good to show order date","confidenceScore":"94%","name":"Order date","data_path":"order[].createdDate"},{"reason":"User asked to see the order status","confidenceScore":"98%","name":"Order status","data_path":"order[].status.name"}]',
    },
    "set-of-cards": {
        "description": "component to visualize array of objects with multiple items. Use for data with fewer items (<6), high number of fields, or fields with long values. Also good when visual separation between items is important.",
        "twostep_step2configure_example": '[{"reason":"It is always good to show product name","confidenceScore":"98%","name":"Name","data_path":"products[].name"},{"reason":"Product description provides important context","confidenceScore":"92%","name":"Description","data_path":"products[].description"},{"reason":"Price is essential information for products","confidenceScore":"95%","name":"Price","data_path":"products[].price"}]',
    },
    "chart-bar": {
        "description": "component to visualize numeric data as a bar chart. Use for comparing one metric across categories.",
        "twostep_step2configure_example": '[{"name":"Movie","data_path":"movies[*].title"},{"name":"Revenue","data_path":"movies[*].revenue"}]',
        "twostep_step2configure_rules": "FIELDS: chart-bar=2 [category,metric]",
        "chart_description": "Compare 1 metric across items",
        "chart_fields_spec": "[category, metric]",
        "chart_rules": "",
        "chart_inline_examples": 'Bar (vertical): {"component":"chart-bar","fields":[{"name":"Item","data_path":"items[*].name"},{"name":"Score","data_path":"items[*].score"}]}\nBar (nested): {"component":"chart-bar","fields":[{"name":"Item","data_path":"items[*].product.name"},{"name":"Sales","data_path":"items[*].product.sales"}]}',
    },
    "chart-line": {
        "description": "component to visualize numeric data as a line chart. Use for trends over time or continuous data.",
        "twostep_step2configure_example": '[{"name":"Month","data_path":"data[*].month"},{"name":"Revenue","data_path":"data[*].revenue"}]',
        "twostep_step2configure_rules": "FIELDS: chart-line=2+ [time/x-axis,metric1,metric2,...] OR 3 [entity_id,time/x-axis,metric] for multi-series\nLine: Use standard pattern [time,metric1,metric2] for multiple metrics, or [entity_id,time,metric] for same metric across entities.",
        "chart_description": "Time-series, trends over time",
        "chart_fields_spec": "Two patterns:\n  - Standard: [time/x-axis, metric1, metric2, ...] - Multiple metrics over same x-axis\n  - Multi-series: [entity_id, time/x-axis, metric] - Same metric across different entities",
        "chart_rules": "Use standard pattern when showing multiple different metrics. Use multi-series pattern when showing same metric for different entities.",
        "chart_inline_examples": 'Line (standard, 2 metrics): {"component":"chart-line","fields":[{"name":"Month","data_path":"data[*].month"},{"name":"Sales","data_path":"data[*].sales"},{"name":"Profit","data_path":"data[*].profit"}]}\nLine (standard, 1 metric): {"component":"chart-line","fields":[{"name":"Month","data_path":"data[*].month"},{"name":"Revenue","data_path":"data[*].revenue"}]}\nLine (multi-series): {"component":"chart-line","fields":[{"name":"Movie","data_path":"items[*].movieTitle"},{"name":"Week","data_path":"items[*].week"},{"name":"Revenue","data_path":"items[*].revenue"}]}',
    },
    "chart-pie": {
        "description": "component to visualize data distribution as a pie chart. Use for showing proportions or percentages.",
        "twostep_step2configure_example": '[{"name":"Genre","data_path":"movies[*].genres"}]',
        "twostep_step2configure_rules": "FIELDS: chart-pie=1 [category]\nPie: backend counts, use [*] for arrays.",
        "chart_description": "Distribution of 1 categorical field",
        "chart_fields_spec": "[category] - backend auto-counts, don't add count field",
        "chart_rules": "",
        "chart_inline_examples": 'Pie: {"component":"chart-pie","fields":[{"name":"Genre","data_path":"items[*].genres"}]}',
    },
    "chart-donut": {
        "description": "component to visualize data distribution as a donut chart. Use for showing proportions with a central metric.",
        "twostep_step2configure_example": '[{"name":"Category","data_path":"movies[*].category"}]',
        "twostep_step2configure_rules": "FIELDS: chart-donut=1 [category]\nDonut: backend counts, use [*] for arrays.",
        "chart_description": "Distribution of 1 categorical field",
        "chart_fields_spec": "[category] - backend auto-counts, don't add count field",
        "chart_rules": "",
        "chart_inline_examples": 'Donut: {"component":"chart-donut","fields":[{"name":"Category","data_path":"items[*].category"}]}',
    },
    "chart-mirrored-bar": {
        "description": "component to visualize two metrics side-by-side as mirrored bars. Use for comparing two metrics across categories.",
        "twostep_step2configure_example": '[{"name":"Movie","data_path":"get_all_movies[*].movie.title"},{"name":"ROI","data_path":"get_all_movies[*].movie.roi"},{"name":"Budget","data_path":"get_all_movies[*].movie.budget"}]',
        "twostep_step2configure_rules": "FIELDS: chart-mirrored-bar=3 [category,metric1,metric2]",
        "chart_description": 'Compare 2 metrics side-by-side (e.g., "A and B", "A vs B", different scales)',
        "chart_fields_spec": "[category, metric1, metric2]",
        "chart_rules": "",
        "chart_inline_examples": 'Mirrored: {"component":"chart-mirrored-bar","fields":[{"name":"Item","data_path":"items[*].name"},{"name":"A","data_path":"items[*].a"},{"name":"B","data_path":"items[*].b"}]}',
    },
}


def normalize_allowed_components(
    allowed_components: set[str] | None,
    metadata: dict,
) -> set[str]:
    """
    Normalize allowed_components to a set of strings.

    Args:
        allowed_components: Set of allowed component names, or None for all components
        metadata: Component metadata dictionary

    Returns:
        Set of allowed component names
    """
    if allowed_components is None:
        return set(metadata.keys())
    return allowed_components


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
    metadata: dict,
) -> str:
    """
    Build filtered component descriptions based on allowed components.

    Args:
        allowed_components: Set of allowed component names
        metadata: Component metadata dictionary

    Returns:
        Formatted string with component descriptions
    """

    descriptions = []
    for component in ALL_COMPONENTS:
        if component in allowed_components:
            descriptions.append(f"* {component} - {metadata[component]['description']}")

    return "\n".join(descriptions)


def build_twostep_step2configure_example(component: str, metadata: dict) -> str:
    """
    Get step2 (component configuration) field example for the selected component.

    Args:
        component: Component name
        metadata: Component metadata dictionary

    Returns:
        Field selection example string or empty string if not found
    """
    if component in metadata:
        return str(metadata[component].get("twostep_step2configure_example", ""))
    return ""


def build_twostep_step2configure_rules(component: str, metadata: dict) -> str:
    """
    Get step2 (component configuration) additional field selection rules for the component.

    Args:
        component: Component name
        metadata: Component metadata dictionary

    Returns:
        Field selection extension string or empty string if not found
    """
    if component in metadata:
        return str(metadata[component].get("twostep_step2configure_rules", ""))
    return ""


def build_chart_instructions(
    allowed_chart_components: set[str], metadata: dict, template: str | None = None
) -> str:
    """
    Build filtered chart instructions for component selection based on allowed chart components.

    Args:
        allowed_chart_components: Set of allowed chart component names
        metadata: Component metadata dictionary
        template: Optional template string with placeholders: {charts_description}, {charts_fields_spec},
                  {charts_rules}, {charts_inline_examples}. If None, uses default template.

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
        if (
            chart_comp in allowed_chart_components
            and metadata[chart_comp]["chart_description"] is not None
            and metadata[chart_comp]["chart_description"].strip() != ""
        ):
            chart_types.append(
                f"{chart_comp}: {metadata[chart_comp]['chart_description']}"
            )

    # Build FIELDS BY TYPE section
    fields_by_type: list[str] = []
    for chart_comp in chart_components_ordered:
        if (
            chart_comp in allowed_chart_components
            and metadata[chart_comp]["chart_fields_spec"] is not None
            and metadata[chart_comp]["chart_fields_spec"].strip() != ""
        ):
            fields_spec = metadata[chart_comp]["chart_fields_spec"]
            fields_by_type.append(f"{chart_comp}: {fields_spec}")

    # Build CHART RULES section
    chart_rules = []
    for chart_comp in chart_components_ordered:
        if (
            chart_comp in allowed_chart_components
            and metadata[chart_comp]["chart_rules"] is not None
            and metadata[chart_comp]["chart_rules"].strip() != ""
        ):
            chart_rules.append(metadata[chart_comp]["chart_rules"])

    # Build EXAMPLES section
    examples = []
    for chart_comp in chart_components_ordered:
        if (
            chart_comp in allowed_chart_components
            and metadata[chart_comp]["chart_inline_examples"] is not None
            and metadata[chart_comp]["chart_inline_examples"].strip() != ""
        ):
            inline_examples = metadata[chart_comp]["chart_inline_examples"]
            examples.append(inline_examples)

    # Prepare component-specific chart rules
    chart_rules_content = "\n".join(chart_rules) if chart_rules else ""

    # Use custom template or default
    if template:
        # User provides full template, including any common rules they want
        return template.format(
            charts_description="\n".join(chart_types),
            charts_fields_spec="\n".join(fields_by_type),
            charts_rules=chart_rules_content,
            charts_inline_examples="\n".join(examples),
        )
    else:
        # Default template (existing behavior)

        instruction_parts = [
            "CHART TYPES (count ONLY metrics user requests):",
            "\n".join(chart_types),
            "",
            "FIELDS BY CHART TYPE:",
            "\n".join(fields_by_type),
            "",
            "CHART RULES:",
            "- Don't add unrequested metrics",
            chart_rules_content,
            "",
            "CHART EXAMPLES:",
            "\n".join(examples),
        ]
        return "\n".join(instruction_parts)
