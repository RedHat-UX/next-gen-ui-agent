"""Shared chart component instructions for LLM prompts."""

CHART_INSTRUCTIONS = """
CHART TYPES (count ONLY metrics user requests):
bar: Compare 1 metric across items
mirrored-bar: Compare 2 metrics side-by-side (e.g., "A and B", "A vs B", different scales)
line: Time-series, trends over time
pie/donut: Distribution of 1 categorical field

FIELDS BY TYPE:
bar: [category, metric]
mirrored-bar: [category, metric1, metric2]
line: [item_id, time, values] ← item_id FIRST
pie/donut: [category] ← backend auto-counts, don't add count!

JSONPATH:
✓ "items[*].field" or "items[*].nested[*].value"
✗ NO "items[size up to 6][*]" or "['key[size...]]..."
Arrays: Use [*] to flatten (e.g., "items[*].genres[*]")

RULES:
• Don't add unrequested metrics
• horizontal=true if labels >15 chars

EXAMPLES:
Bar: {"chartType":"bar","fields":[{"name":"Item","data_path":"items[*].name"},{"name":"Score","data_path":"items[*].score"}]}
Mirrored: {"chartType":"mirrored-bar","fields":[{"name":"Item","data_path":"items[*].name"},{"name":"A","data_path":"items[*].a"},{"name":"B","data_path":"items[*].b"}]}
Line: {"chartType":"line","fields":[{"name":"Item","data_path":"items[*].name"},{"name":"Week","data_path":"items[*].weekly[*].week"},{"name":"Value","data_path":"items[*].weekly[*].value"}]}
Pie: {"chartType":"pie","fields":[{"name":"Genre","data_path":"items[*].genres[*]"}]}
Donut: {"chartType":"donut","fields":[{"name":"Category","data_path":"items[*].category"}]}
"""

# Two-step strategy: field count reference
CHART_FIELD_SELECTION_EXTENSION = """
FIELDS: pie/donut=1 [category], bar=2 [category,metric], mirrored-bar=3 [category,metric1,metric2], line=3 [item_id,time,values]
Pie/donut: backend counts, use [*] for arrays. Line: item_id FIRST!
"""

# Two-step strategy: field examples
CHART_FIELD_SELECTION_EXAMPLES = """
Bar: [{"name":"Movie","data_path":"movies[*].title"},{"name":"Revenue","data_path":"movies[*].revenue"}]
Mirrored: [{"name":"Movie","data_path":"movies[*].title"},{"name":"Rating","data_path":"movies[*].rating"},{"name":"Revenue","data_path":"movies[*].revenue"}]
Line: [{"name":"Movie","data_path":"movies[*].title"},{"name":"Week","data_path":"movies[*].weekly[*].week"},{"name":"Revenue","data_path":"movies[*].weekly[*].revenue"}]
Pie: [{"name":"Genre","data_path":"movies[*].genres[*]"}]
Donut: [{"name":"Category","data_path":"movies[*].category"}]
"""
