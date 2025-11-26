"""Shared chart component instructions for LLM prompts."""

CHART_INSTRUCTIONS = """
CHART TYPES (count ONLY metrics user requests):
chart-bar: Compare 1 metric across items
chart-mirrored-bar: Compare 2 metrics side-by-side (e.g., "A and B", "A vs B", different scales)
chart-line: Time-series, trends over time
chart-pie/chart-donut: Distribution of 1 categorical field

FIELDS BY TYPE:
chart-bar: [category, metric]
chart-mirrored-bar: [category, metric1, metric2]
chart-line: [item_id, time, values] - item_id REQUIRED for multi-series to separate items
chart-pie/chart-donut: [category] - backend auto-counts, don't add count field

RULES:
- Don't add unrequested metrics
- Line charts: ALWAYS include item identifier field FIRST to separate multiple time-series

EXAMPLES:
Bar (vertical): {"component":"chart-bar","fields":[{"name":"Item","data_path":"items[*].name"},{"name":"Score","data_path":"items[*].score"}]}
Bar (nested): {"component":"chart-bar","fields":[{"name":"Item","data_path":"items[*].product.name"},{"name":"Sales","data_path":"items[*].product.sales"}]}
Mirrored: {"component":"chart-mirrored-bar","fields":[{"name":"Item","data_path":"items[*].name"},{"name":"A","data_path":"items[*].a"},{"name":"B","data_path":"items[*].b"}]}
Line (flattened time-series): {"component":"chart-line","fields":[{"name":"Movie","data_path":"items[*].movieTitle"},{"name":"Week","data_path":"items[*].week"},{"name":"Revenue","data_path":"items[*].revenue"}]}
Pie: {"component":"chart-pie","fields":[{"name":"Genre","data_path":"items[*].genres"}]}
Donut: {"component":"chart-donut","fields":[{"name":"Category","data_path":"items[*].category"}]}
"""

# Two-step strategy: field count reference
CHART_FIELD_SELECTION_EXTENSION = """
FIELDS: chart-pie/chart-donut=1 [category], chart-bar=2 [category,metric], chart-mirrored-bar=3 [category,metric1,metric2], chart-line=3 [item_id,time,values]
Pie/donut: backend counts, use [*] for arrays. Line: item_id FIRST!
"""

# Two-step strategy: field examples
CHART_FIELD_SELECTION_EXAMPLES = """
Bar (flat): [{"name":"Movie","data_path":"movies[*].title"},{"name":"Revenue","data_path":"movies[*].revenue"}]
Bar (nested): [{"name":"Movie","data_path":"get_all_movies[*].movie.title"},{"name":"Revenue","data_path":"get_all_movies[*].movie.revenue"}]
Mirrored (nested): [{"name":"Movie","data_path":"get_all_movies[*].movie.title"},{"name":"ROI","data_path":"get_all_movies[*].movie.roi"},{"name":"Budget","data_path":"get_all_movies[*].movie.budget"}]
Line (flattened): [{"name":"Movie","data_path":"movies[*].movieTitle"},{"name":"Week","data_path":"movies[*].week"},{"name":"Revenue","data_path":"movies[*].revenue"}]
Pie: [{"name":"Genre","data_path":"movies[*].genres"}]
Donut: [{"name":"Category","data_path":"movies[*].category"}]
"""
