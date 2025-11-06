"""Shared chart component instructions for LLM prompts."""

# Chart component instructions used by both one-step and two-step selection strategies
CHART_INSTRUCTIONS = """
CHART COMPONENT RULES:

⚠️⚠️⚠️ RULE #1 - ALWAYS CHECK USER'S EXACT WORDS FIRST ⚠️⚠️⚠️
IF the user explicitly says "donut chart" in their query → YOU MUST USE "chartType": "donut"
IF the user explicitly says "pie chart" in their query → YOU MUST USE "chartType": "pie"
IF the user explicitly says "bar chart" in their query → YOU MUST USE "chartType": "bar"
IF the user explicitly says "line chart" in their query → YOU MUST USE "chartType": "line"

DO NOT substitute a different chart type than what the user explicitly requested!

1. CHART TYPE SELECTION:
   - "bar" → compare ONE metric across multiple items (e.g., "compare values", "metric comparison")
   - "line" → trends over time, multi-series comparisons over time
   - "mirrored-bar" → compare TWO DIFFERENT metrics side-by-side (e.g., "metric1 vs metric2", "metric1 and metric2")
   - "pie" → proportions (use when user says "pie chart" or doesn't specify)
   - "donut" → proportions (ONLY when user explicitly says "donut chart")

2. CRITICAL: Count the ACTUAL metrics the user explicitly asks for (DO NOT invent metrics!):

   ⚠️  SINGLE METRIC → bar chart:
   - "compare metric A" → bar (user asked for: metricA)
   - "compare values" → bar (user asked for: value)
   - "show all scores" → bar (user asked for: score)
   - "rating comparison" → bar (user asked for: rating ONLY - don't add other metrics!)
   - "compare prices" → bar (user asked for: price)

   ⚠️  TRENDS OVER TIME → line chart:
   - "compare trends", "weekly/daily/monthly", "over time" → line

   ⚠️  TWO DIFFERENT METRICS → mirrored-bar (user MUST explicitly mention BOTH):
   LOOK FOR: "and", "vs", "versus", commas separating metrics
   - "metric1 vs metric2" → mirrored-bar (user asked for: metric1 AND metric2)
   - "metric1 and metric2" → mirrored-bar (user asked for: metric1 AND metric2)
   - "score and rating" → mirrored-bar (user asked for: score AND rating)
   - "ratings and revenue" → mirrored-bar (user asked for: ratings AND revenue)
   - "cost vs value" → mirrored-bar (user asked for: cost AND value)
   - "compare actual and target" → mirrored-bar (user asked for: actual AND target)
   - "show metric1, metric2" → mirrored-bar (user asked for: metric1 AND metric2)

   ⚠️  ESPECIALLY use mirrored-bar when metrics have DIFFERENT SCALES:
   - ratings (0-10) and revenue (millions) → mirrored-bar is PERFECT for this!
   - percentage and count → mirrored-bar
   - small values and large values → mirrored-bar

   ❌ DO NOT ADD METRICS THE USER DIDN'T ASK FOR!
   If user says "score comparison", they want score only → bar chart with 2 fields total

3. FOR LINE CHARTS WITH NESTED TIME-SERIES DATA:
   ⚠️  CRITICAL FIELD ORDER - DO NOT DEVIATE:
   Field 1: Item identifier (creates series names/lines)
           Example: items[*].name → "Item A", "Item B"
   Field 2: Nested x-axis (time dimension)
           Example: items[*].timeSeries[*].period → 1, 2, 3, 4
   Field 3: Nested y-axis (metric values)
           Example: items[*].timeSeries[*].value → 158411483, 75165786, ...

   ⚠️  USE SIMPLE, STANDARD JSONPATH SYNTAX ONLY:
   ✅ CORRECT: "items[*].timeSeries[*].period"
   ✅ CORRECT: "items[*].nested[*].value"
   ✅ CORRECT: "results[*].item.name" (NOT results[size up to 6][*])
   ❌ WRONG: "'$$'[0]'.timeSeries[*].period" - INVALID SYNTAX
   ❌ WRONG: "['key[size up to 6]'][0]['nested']..." - TOO COMPLEX
   ❌ WRONG: "results[size up to 6][*].item.name" - DO NOT include [size...] type hints!

   ❌ DO NOT use items[*].totalValue (aggregate) - use items[*].timeSeries[*].value (nested period values)
   ❌ DO NOT put time/period field first - put item identifier first
   ❌ DO NOT create "Period" and "Value" as series names - use item names ("Item A", "Item B")

   Result: Multiple lines (one per item), x-axis=time, y-axis=metric

4. FOR SIMPLE BAR CHARTS (flat data):
   Field 1: Categories (e.g., items[*].name)
   Field 2: ONE metric only (e.g., items[*].value OR items[*].metric)

   For mirrored-bar ONLY:
   Field 1: Categories (e.g., items[*].name)
   Field 2: First metric (e.g., items[*].metric1)
   Field 3: Second metric (e.g., items[*].metric2)

   For PIE/DONUT charts (distribution/frequency):
   ⚠️  ONLY ONE field needed! Backend auto-counts occurrences.
   Field 1: Categories to count

   ⚠️  UNDERSTAND WHAT USER WANTS TO DISTRIBUTE:
   - "category distribution" → items[*].categories[*] (count category values)
   - "rating distribution" → items[*].rating (count rating values like 8.3, 9.0, 8.7)
   - "type distribution" → items[*].type (count types)
   - "status distribution" → items[*].status (count status values)

   ⚠️  CRITICAL FOR ARRAYS - ALWAYS USE [*] NOT [size:N]:
   ✅ CORRECT: "items[*].categories[*]" (extracts individual category strings)
   ❌ WRONG: "items[*].categories[size: 1]" (extracts entire array!)
   ❌ WRONG: "items[*].categories" (extracts entire array!)

   ❌ DO NOT confuse different field types - they may have different structures!
   ❌ DO NOT add a second field with counts - backend handles this automatically!

5. HORIZONTAL BAR CHARTS:
   If x-axis labels > 15 chars or contain long names/titles → set horizontal=true

6. CRITICAL: Count ONLY the metrics the user explicitly mentions!
   - "compare metric A" = user said: metricA → 1 metric → bar
   - "compare values" = user said: value → 1 metric → bar
   - "score comparison" = user said: score → 1 metric → bar (DO NOT add other metrics!)
   - "metric1 vs metric2" = user said: metric1, metric2 → 2 metrics → mirrored-bar
   - "score and rating" = user said: score, rating → 2 metrics → mirrored-bar

   ❌ NEVER invent or add metrics the user didn't explicitly request!

EXAMPLES:

⚠️  CRITICAL - Example 1: SIMPLE BAR CHART (single metric comparison)
When user asks "compare scores", "compare values", "metric comparison" → USE chartType="bar"

{
    "title": "Score Comparison",
    "reasonForTheComponentSelection": "User wants to compare one metric (score) across multiple items",
    "confidenceScore": "95%",
    "component": "chart",
    "chartType": "bar",
    "fields" : [
        {"name":"Item","data_path":"items[*].name"},
        {"name":"Score","data_path":"items[*].score"}
    ]
}

⚠️  CRITICAL - Example 2: SINGLE-ITEM NESTED ARRAY (one item with time-series)
When user asks "daily values for Item X", "time series for Item Y" → USE chartType="line"

{
    "title": "Time Series for Item X",
    "reasonForTheComponentSelection": "User wants to view time series data for a specific item",
    "confidenceScore": "95%",
    "component": "chart",
    "chartType": "line",
    "fields" : [
        {"name":"Period","data_path":"item.timeSeries[*].period"},
        {"name":"Value","data_path":"item.timeSeries[*].value"}
    ]
}

CRITICAL: For SINGLE item with nested array, use simple paths like "item.timeSeries[*].period"
DO NOT use complex paths like "['search_item[size up to 6]'][0]['item']..." - that is INVALID!

⚠️  CRITICAL - Example 3: NESTED TIME-SERIES (periodic trends)
When user asks "compare time series", "compare trends", "periodic comparisons" → USE chartType="line"

{
    "title": "Periodic Value Trends",
    "component": "chart",
    "chartType": "line",
    "fields" : [
        {"name":"Item","data_path":"items[*].name"},
        {"name":"Period","data_path":"items[*].timeSeries[*].period"},
        {"name":"Value","data_path":"items[*].timeSeries[*].value"}
    ]
}

❌ WRONG - DO NOT DO THIS:
{
    "fields" : [
        {"name":"Period","data_path":"items[*].timeSeries[*].period"},  ← NO! Period should NOT be first
        {"name":"Value","data_path":"items[*].totalValue"}  ← NO! Use timeSeries[*].value, not totalValue
    ]
}

✅ CORRECT FIELD ORDER:
1. items[*].name → Series names: "Item A", "Item B" (one line per item)
2. items[*].timeSeries[*].period → X-axis: 1, 2, 3, 4
3. items[*].timeSeries[*].value → Y-axis: 158411483, 75165786, ...

⚠️  CRITICAL - Example 4: MIRRORED-BAR (comparing TWO metrics side-by-side)
When user asks "compare metric1 and metric2", "score vs rating", "compare metric A and metric B" → USE MIRRORED-BAR:

{
    "title": "Score vs Rating Comparison",
    "reasonForTheComponentSelection": "User wants to compare two different metrics side-by-side",
    "confidenceScore": "90%",
    "component": "chart",
    "chartType": "mirrored-bar",
    "fields" : [
        {"name":"Item","data_path":"items[*].name"},
        {"name":"Score","data_path":"items[*].score"},
        {"name":"Rating","data_path":"items[*].rating"}
    ]
}

⚠️  CRITICAL - Example 5: MIRRORED-BAR for METRICS WITH DIFFERENT SCALES
When user asks "ratings and revenue", "score and count", metrics with very different scales → USE MIRRORED-BAR:

{
    "title": "Item Ratings and Revenue",
    "reasonForTheComponentSelection": "User wants to compare two metrics (ratings and revenue) which have different scales - mirrored-bar is perfect for this",
    "confidenceScore": "95%",
    "component": "chart",
    "chartType": "mirrored-bar",
    "fields" : [
        {"name":"Item","data_path":"items[*].title"},
        {"name":"Rating","data_path":"items[*].rating"},
        {"name":"Revenue","data_path":"items[*].revenue"}
    ]
}

IMPORTANT: Use mirrored-bar ONLY when comparing TWO different metrics (not trends over time).
Mirrored-bar is ESPECIALLY useful when metrics have different scales (ratings 0-10 vs revenue in millions)!
"""
