from typing import Any

from next_gen_ui_agent.data_transform.data_transformer import DataTransformerBase
from next_gen_ui_agent.data_transform.types import (
    ChartDataPoint,
    ChartSeries,
    ComponentDataChart,
)
from next_gen_ui_agent.types import InputData, UIComponentMetadata
from typing_extensions import override

# Chart type inference patterns
CHART_TYPE_PATTERNS = {
    "bar": ["bar chart", "bar graph"],
    "mirrored-bar": ["mirrored bar", "mirrored-bar", "compare two metrics", "roi vs", "vs budget", "revenue vs profit", "compare roi and budget"],
    "line": ["line chart", "line graph", "trend", "over time", "timeline"],
    "pie": ["pie chart", "proportion", "percentage", "share", "distribution"],
    "donut": ["donut chart", "donut graph"],
}


class ChartDataTransformer(DataTransformerBase[ComponentDataChart]):
    COMPONENT_NAME = "chart"

    def __init__(self):
        self._component_data = ComponentDataChart.model_construct(
            chartType="bar", data=[]  # Default  # Empty list by default
        )
        self._user_prompt = None

    @override
    def main_processing(self, json_data: Any, component: UIComponentMetadata):
        """
        Transform input data into chart format.

        The transformer extracts chartType from component and uses fields to build chart data.

        Args:
            json_data: The input data to transform
            component: Component metadata containing configuration and fields
        """
        print("[Chart] Starting main_processing")
        print(f"[Chart] Component title: {component.title}")
        print(
            f"[Chart] Number of fields: {len(component.fields) if hasattr(component, 'fields') and component.fields else 0}"
        )

        # Extract chartType from component metadata or infer from title/reason
        if hasattr(component, "chartType") and component.chartType:
            self._component_data.chartType = component.chartType
            print(f"[Chart] Using chartType from component: {component.chartType}")
        else:
            # Try to infer from component title, reason, or default to bar
            inferred_type = None

            # Check title first
            if component.title:
                inferred_type = self._infer_chart_type(component.title)
                if inferred_type:
                    print(f"[Chart] Inferred chartType from title: {inferred_type}")

            # If not found in title, check reasonForTheComponentSelection
            if (
                not inferred_type
                and hasattr(component, "reasonForTheComponentSelection")
                and component.reasonForTheComponentSelection
            ):
                inferred_type = self._infer_chart_type(
                    component.reasonForTheComponentSelection
                )
                if inferred_type:
                    print(f"[Chart] Inferred chartType from reason: {inferred_type}")

            self._component_data.chartType = inferred_type if inferred_type else "bar"
            if not inferred_type:
                print("[Chart] Using default chartType: bar")

        # If component has fields defined, use them to extract chart data
        if hasattr(component, "fields") and component.fields:
            print("[Chart] Fields present, calling _extract_data_from_fields")
            self._extract_data_from_fields(json_data, component)
            print(
                f"[Chart] After extraction, data length: {len(self._component_data.data) if self._component_data.data else 0}"
            )
            return

        # Otherwise, try to auto-detect structure
        # If the data is already in chart format with 'data' field containing series
        if isinstance(json_data, dict):
            if "data" in json_data and isinstance(json_data["data"], list):
                # Assume data is already in the correct format
                series_list = []
                for series_data in json_data["data"]:
                    if (
                        isinstance(series_data, dict)
                        and "name" in series_data
                        and "data" in series_data
                    ):
                        data_points = []
                        for point in series_data["data"]:
                            if isinstance(point, dict):
                                data_points.append(
                                    ChartDataPoint(
                                        name=point.get("name"),
                                        x=point.get("x", point.get("label", "")),
                                        y=point.get("y", point.get("value", 0)),
                                    )
                                )
                        series_list.append(
                            ChartSeries(name=series_data["name"], data=data_points)
                        )
                self._component_data.data = series_list

            # Handle simple key-value data that should be converted to a single series
            elif any(
                key not in ["id", "title", "chartType", "type"]
                for key in json_data.keys()
            ):
                # Convert flat data to a single series
                data_points = []
                for key, value in json_data.items():
                    if key not in ["id", "title", "chartType", "type"] and isinstance(
                        value, (int, float)
                    ):
                        data_points.append(ChartDataPoint(x=key, y=value))

                if data_points:
                    self._component_data.data = [
                        ChartSeries(name="Data", data=data_points)
                    ]

        # Handle list of dictionaries (array of objects)
        elif isinstance(json_data, list) and len(json_data) > 0:
            if isinstance(json_data[0], dict):
                # Try to convert list of objects to chart series
                # This is a simple heuristic - can be enhanced based on data structure
                data_points = []
                for item in json_data:
                    # Look for common x/y patterns
                    x_val = (
                        item.get("x")
                        or item.get("name")
                        or item.get("label")
                        or item.get("category")
                    )
                    y_val = item.get("y") or item.get("value") or item.get("count")

                    if x_val is not None and y_val is not None:
                        data_points.append(ChartDataPoint(x=str(x_val), y=float(y_val)))

                if data_points:
                    self._component_data.data = [
                        ChartSeries(name="Data", data=data_points)
                    ]

    def _extract_data_from_fields(self, json_data: Any, component: UIComponentMetadata):
        """Extract chart data using the fields defined in component metadata."""
        from jsonpath_ng import parse

        print("[Chart] _extract_data_from_fields called")
        print(f"[Chart] json_data type: {type(json_data)}")
        print(
            f"[Chart] json_data keys: {json_data.keys() if isinstance(json_data, dict) else 'not a dict'}"
        )

        # Handle empty/null data
        if not json_data or (isinstance(json_data, dict) and not json_data):
            print(
                "[Chart] WARNING: json_data is empty or null, cannot extract chart data"
            )
            return

        # Get all fields from component
        fields = component.fields if hasattr(component, "fields") else []

        print(f"[Chart] Processing {len(fields)} fields")
        for i, field in enumerate(fields):
            print(
                f"[Chart]   Field {i}: name='{field.name}', data_path='{field.data_path}'"
            )

        if not fields or len(fields) < 2:
            # For single field or no fields, try to auto-generate chart from single data point
            print(
                f"[Chart] Not enough fields ({len(fields) if fields else 0}), attempting auto-generation"
            )
            if len(fields) == 1:
                # For pie/donut charts with 1 field, count occurrences
                chart_type = getattr(component, 'chartType', None)
                if chart_type in ['pie', 'donut']:
                    print(f"[Chart] Single field for {chart_type} chart - will count occurrences")
                    self._create_frequency_chart(json_data, component, fields[0])
                else:
                    self._create_single_point_chart(json_data, component, fields[0])
            return

        print(f"[Chart] Have {len(fields)} fields, proceeding with extraction")
        
        # Special case: pie/donut charts with 2 fields where second field is invalid
        chart_type = getattr(component, 'chartType', None)
        if chart_type in ['pie', 'donut'] and len(fields) == 2:
            second_field_path = fields[1].data_path.strip()
            # Check if second field is empty or just brackets (invalid)
            if not second_field_path or second_field_path in ['[]', '{}', '']:
                print(f"[Chart] {chart_type} chart with invalid second field '{second_field_path}' - treating as single field")
                self._create_frequency_chart(json_data, component, fields[0])
                return

        # Detect nested time-series pattern: fields with [*]...[*] indicate nested arrays
        # Pattern: Field 0 = series identifier, Field 1 = nested x-axis, Field 2 = nested y-axis
        is_nested_timeseries = (
            len(fields) >= 3
            and "[*]" in fields[1].data_path
            and "[*]" in fields[2].data_path
            and fields[1].data_path.count("[*]") > fields[0].data_path.count("[*]")
        )

        print(f"[Chart] Detected nested time-series pattern: {is_nested_timeseries}")

        if is_nested_timeseries:
            # For nested time-series: Field 0 = series ID, Field 1 = x-axis, Field 2 = y-axis
            print("[Chart] Using nested time-series field mapping:")
            print(
                f"[Chart]   Series identifier: {fields[0].name} ({fields[0].data_path})"
            )
            print(f"[Chart]   X-axis: {fields[1].name} ({fields[1].data_path})")
            print(f"[Chart]   Y-axis: {fields[2].name} ({fields[2].data_path})")
            self._extract_nested_timeseries_data(json_data, fields)
            return
        else:
            # Traditional flat structure: Field 0 = x-axis, Fields 1+ = y-axis series
            x_field = fields[0]
            y_fields = fields[1:]
            print(
                f"[Chart] Using flat field mapping - x_field: {x_field.name}, y_fields: {[f.name for f in y_fields]}"
            )

        # Extract x values
        x_values = []
        try:
            # Normalize the data_path
            print(f"[Chart] About to normalize x_field path: '{x_field.data_path}'")
            data_path = self._normalize_data_path(x_field.data_path)
            print(
                f"[Chart] Normalized x_field path: '{x_field.data_path}' -> '{data_path}'"
            )
            jsonpath_expr = parse(data_path)
            print("[Chart] Parsed JSONPath expression, searching...")
            matches = jsonpath_expr.find(json_data)
            print(f"[Chart] Found {len(matches)} matches")
            x_values = [match.value for match in matches]
            print(f"[Chart] Extracted {len(x_values)} x values: {x_values}")
        except Exception as e:
            print(f"[Chart] Error extracting x values: {e}")
            import traceback

            traceback.print_exc()
            return

        if not x_values:
            print(
                f"[Chart] WARNING: No x values found for field '{x_field.name}', cannot create chart"
            )
            return

        # Extract y values for each series
        series_list = []
        for y_field in y_fields:
            try:
                # Normalize the data_path
                data_path = self._normalize_data_path(y_field.data_path)
                print(
                    f"[Chart] Normalized y_field path: '{y_field.data_path}' -> '{data_path}'"
                )
                jsonpath_expr = parse(data_path)
                matches = jsonpath_expr.find(json_data)
                y_values = [match.value for match in matches]
                print(
                    f"[Chart] Extracted {len(y_values)} y values for {y_field.name}: {y_values}"
                )

                if y_values:
                    # Create data points by pairing x and y values
                    data_points = []
                    for i, (x_val, y_val) in enumerate(zip(x_values, y_values)):
                        if isinstance(y_val, (int, float)):
                            data_points.append(
                                ChartDataPoint(x=str(x_val), y=float(y_val))
                            )

                    if data_points:
                        series_list.append(
                            ChartSeries(name=y_field.name, data=data_points)
                        )
            except Exception as e:
                print(f"Error extracting y values for {y_field.name}: {e}")

        if series_list:
            self._component_data.data = series_list

    def _extract_nested_timeseries_data(self, json_data: Any, fields: list):
        """
        Extract nested time-series data where:
        - Field 0: Series identifier (e.g., movies[*].title)
        - Field 1: Nested x-axis (e.g., movies[*].weeklyBoxOffice[*].week)
        - Field 2: Nested y-axis (e.g., movies[*].weeklyBoxOffice[*].revenue)
        
        Strategy: Extract base items, then for each item access its nested array directly
        """
        from jsonpath_ng import parse

        print("[Chart] _extract_nested_timeseries_data called")
        print(f"[Chart] Available top-level keys in json_data: {list(json_data.keys()) if isinstance(json_data, dict) else 'not a dict'}")

        series_id_field = fields[0]
        x_field = fields[1]
        y_field = fields[2]

        # Determine the base path (e.g., "movies[*]" from "movies[*].weeklyBoxOffice[*].week")
        original_base_path = None
        if "[*]" in x_field.data_path:
            parts = x_field.data_path.split("[*]")
            if len(parts) >= 2:
                original_base_path = parts[0] + "[*]"
                print(f"[Chart] Detected base path from field: {original_base_path}")

        if not original_base_path:
            print("[Chart] Could not determine base path")
            return

        # Extract base items (e.g., all movie objects)
        base_path = original_base_path  # Start with the path from fields
        try:
            base_data_path = self._normalize_data_path(base_path)
            print(f"[Chart] Normalized base path: {base_data_path}")
            jsonpath_expr = parse(base_data_path)
            base_matches = jsonpath_expr.find(json_data)
            base_items = [match.value for match in base_matches]
            print(f"[Chart] Found {len(base_items)} base items with path '{base_data_path}'")
            
            if base_items and len(base_items) > 0:
                print(f"[Chart] First base item type: {type(base_items[0])}")
                print(f"[Chart] First base item keys: {base_items[0].keys() if isinstance(base_items[0], dict) else 'not a dict'}")
                if isinstance(base_items[0], dict):
                    print(f"[Chart] First base item sample: {list(base_items[0].keys())[:5]}")
        except Exception as e:
            print(f"[Chart] Error extracting base items: {e}")
            import traceback
            traceback.print_exc()
            return

        if not base_items:
            print("[Chart] No base items found with specified path")
            print("[Chart] Attempting fallback: searching for any array in json_data")
            
            # Fallback: try to find the actual array in the data
            if isinstance(json_data, dict):
                for key, value in json_data.items():
                    if isinstance(value, list) and len(value) > 0:
                        print(f"[Chart] Found array at key '{key}' with {len(value)} items")
                        print(f"[Chart] First item in array: {type(value[0])}")
                        if isinstance(value[0], dict):
                            print(f"[Chart] First item keys: {list(value[0].keys())}")
                            # Try to use this array instead
                            base_items = value
                            # Update base path to match actual data (but keep original for suffix calculation)
                            base_path = key + "[*]"
                            print(f"[Chart] Using fallback base path: {base_path}")
                            print(f"[Chart] Original base path was: {original_base_path}")
                            break
            
            if not base_items:
                print("[Chart] Fallback also found no base items")
                return

        # Extract field names from paths
        # The paths might not match the actual data structure, so we need to parse carefully
        # e.g., "movies[*].title" but actual data is compare_movies[*].movie.title
        
        # Parse what comes after the ORIGINAL base path (before fallback)
        series_id_suffix = series_id_field.data_path.replace(original_base_path, "").lstrip(".")
        x_field_suffix = x_field.data_path.replace(original_base_path, "").lstrip(".")
        y_field_suffix = y_field.data_path.replace(original_base_path, "").lstrip(".")
        
        print(f"[Chart] Field suffixes (after removing original base path '{original_base_path}'):")
        print(f"[Chart]   Series ID suffix: {series_id_suffix}")
        print(f"[Chart]   X field suffix: {x_field_suffix}")
        print(f"[Chart]   Y field suffix: {y_field_suffix}")
        
        # Check if base items have a wrapper key (like {"movie": {...}} instead of direct fields)
        # If so, we need to prepend the wrapper key to our suffixes
        if base_items and isinstance(base_items[0], dict):
            item_keys = list(base_items[0].keys())
            print(f"[Chart] Base item has keys: {item_keys}")
            
            # If there's exactly one key and it's an object, it's likely a wrapper
            if len(item_keys) == 1 and isinstance(base_items[0][item_keys[0]], dict):
                wrapper_key = item_keys[0]
                print(f"[Chart] Detected wrapper key: '{wrapper_key}'")
                print(f"[Chart] Wrapper object has keys: {list(base_items[0][wrapper_key].keys())[:10]}")
                
                # Prepend the wrapper key to each suffix ONLY if not already present
                if not series_id_suffix.startswith(f"{wrapper_key}."):
                    series_id_suffix = f"{wrapper_key}.{series_id_suffix}"
                if not x_field_suffix.startswith(f"{wrapper_key}."):
                    x_field_suffix = f"{wrapper_key}.{x_field_suffix}"
                if not y_field_suffix.startswith(f"{wrapper_key}."):
                    y_field_suffix = f"{wrapper_key}.{y_field_suffix}"
                
                print(f"[Chart] Adjusted suffixes with wrapper key:")
                print(f"[Chart]   Series ID suffix: {series_id_suffix}")
                print(f"[Chart]   X field suffix: {x_field_suffix}")
                print(f"[Chart]   Y field suffix: {y_field_suffix}")
        
        # For nested paths like "weeklyBoxOffice[*].week"
        # Extract the nested array name and field: "weeklyBoxOffice" and "week"
        x_parts = x_field_suffix.split("[*]")
        y_parts = y_field_suffix.split("[*]")
        
        if len(x_parts) >= 2:
            x_array_name = x_parts[0]  # "weeklyBoxOffice" or "movie.weeklyBoxOffice"
            x_field_name = x_parts[1].lstrip(".")  # "week"
        else:
            print(f"[Chart] Could not parse x field structure from suffix: {x_field_suffix}")
            return
            
        if len(y_parts) >= 2:
            y_array_name = y_parts[0]  # "weeklyBoxOffice" or "movie.weeklyBoxOffice"
            y_field_name = y_parts[1].lstrip(".")  # "revenue"
        else:
            print(f"[Chart] Could not parse y field structure from suffix: {y_field_suffix}")
            return

        print(f"[Chart] Parsed structure:")
        print(f"[Chart]   Series ID suffix: {series_id_suffix}")
        print(f"[Chart]   X array path: {x_array_name}, field: {x_field_name}")
        print(f"[Chart]   Y array path: {y_array_name}, field: {y_field_name}")

        # Helper function to navigate nested paths like "movie.title"
        def get_nested_value(obj, path):
            """Navigate a dotted path in a nested dict"""
            parts = path.split(".")
            current = obj
            for part in parts:
                if isinstance(current, dict):
                    current = current.get(part)
                    if current is None:
                        return None
                else:
                    return None
            return current

        # Create a series for each base item
        series_list = []
        for idx, base_item in enumerate(base_items):
            if not isinstance(base_item, dict):
                print(f"[Chart] Skipping base item {idx}: not a dictionary")
                continue

            print(f"[Chart] Processing base item {idx}, keys: {list(base_item.keys())}")

            # Get series identifier (might be nested like "movie.title")
            series_id = get_nested_value(base_item, series_id_suffix)
            if series_id is None:
                series_id = f"Series {idx}"
                print(f"[Chart]   Could not find series ID at path '{series_id_suffix}', using default: {series_id}")
            else:
                print(f"[Chart]   Found series ID: {series_id}")

            # Get the nested array (might be nested like "movie.weeklyBoxOffice")
            nested_array = get_nested_value(base_item, x_array_name)
            if not isinstance(nested_array, list):
                print(f"[Chart]   Path '{x_array_name}' did not yield an array (got {type(nested_array)}), skipping")
                continue

            print(f"[Chart]   Found nested array at '{x_array_name}' with {len(nested_array)} items")

            # Extract x and y values from the nested array
            x_values = []
            y_values = []
            for item in nested_array:
                if isinstance(item, dict):
                    x_val = item.get(x_field_name)
                    y_val = item.get(y_field_name)
                    if x_val is not None and y_val is not None:
                        x_values.append(x_val)
                        y_values.append(y_val)

            print(f"[Chart]   Extracted {len(x_values)} x values and {len(y_values)} y values")

            if len(x_values) != len(y_values) or len(x_values) == 0:
                print(f"[Chart]   Skipping series: mismatched or empty data")
                continue

            # Create data points
            data_points = []
            for x_val, y_val in zip(x_values, y_values):
                try:
                    y_numeric = float(y_val) if y_val is not None else 0.0
                    data_points.append(
                        ChartDataPoint(x=str(x_val), y=y_numeric, name=None)
                    )
                except (ValueError, TypeError) as e:
                    print(f"[Chart]   Skipping non-numeric y value: {y_val} for x={x_val}, error: {e}")

            if data_points:
                series_list.append(ChartSeries(name=str(series_id), data=data_points))
                print(f"[Chart]   Created series '{series_id}' with {len(data_points)} points")

        if series_list:
            self._component_data.data = series_list
            print(f"[Chart] Successfully created {len(series_list)} series")
        else:
            print("[Chart] No series created from nested time-series data")

    def _create_single_point_chart(
        self, json_data: Any, component: UIComponentMetadata, field: Any
    ):
        """Create a simple chart from a single data point (fallback for insufficient fields)."""
        from jsonpath_ng import parse

        print(f"[Chart] Creating single-point chart for field: {field.name}")

        # Try to extract value from the single field
        try:
            # Use the same normalization as multi-field extraction
            data_path = self._normalize_data_path(field.data_path)
            print(
                f"[Chart] Normalized single field path: '{field.data_path}' -> '{data_path}'"
            )

            jsonpath_expr = parse(data_path)
            matches = jsonpath_expr.find(json_data)
            print(f"[Chart] Found {len(matches)} matches for single-point chart")

            if matches and len(matches) > 0:
                value = matches[0].value
                print(
                    f"[Chart] Extracted value: {value} (type: {type(value).__name__})"
                )
                if isinstance(value, (int, float)):
                    # Create a simple single-point chart
                    self._component_data.data = [
                        ChartSeries(
                            name=field.name,
                            data=[ChartDataPoint(x=field.name, y=float(value))],
                        )
                    ]
                    print(f"[Chart] Created single point - {field.name}: {value}")
                else:
                    print("[Chart] Value is not numeric, cannot create chart")
        except Exception as e:
            print(f"[Chart] Error creating single-point chart: {e}")
    
    def _create_frequency_chart(
        self, json_data: Any, component: UIComponentMetadata, field: Any
    ):
        """Create a pie/donut chart by counting occurrences of categories (for single field)."""
        from jsonpath_ng import parse
        from collections import Counter

        print(f"[Chart] Creating frequency chart for field: {field.name}")

        # Try to extract categories from the single field
        try:
            # Use the same normalization as multi-field extraction
            data_path = self._normalize_data_path(field.data_path)
            print(
                f"[Chart] Normalized field path: '{field.data_path}' -> '{data_path}'"
            )

            jsonpath_expr = parse(data_path)
            matches = jsonpath_expr.find(json_data)
            print(f"[Chart] Found {len(matches)} matches for frequency chart")

            if matches and len(matches) > 0:
                # Extract all category values, flattening lists/arrays
                categories = []
                for match in matches:
                    value = match.value
                    # If the extracted value is a list/array, flatten it
                    if isinstance(value, (list, tuple)):
                        print(f"[Chart] Flattening list/array: {value}")
                        categories.extend([str(item) for item in value])
                    else:
                        categories.append(str(value))
                
                print(f"[Chart] Extracted categories: {categories[:20]}{'...' if len(categories) > 20 else ''}")
                
                # Count occurrences
                category_counts = Counter(categories)
                print(f"[Chart] Category counts: {dict(category_counts)}")
                
                # Create data points from counts
                data_points = []
                for category, count in category_counts.items():
                    data_points.append(ChartDataPoint(x=category, y=float(count)))
                
                if data_points:
                    self._component_data.data = [
                        ChartSeries(name=field.name, data=data_points)
                    ]
                    print(f"[Chart] Created frequency chart with {len(data_points)} categories")
                else:
                    print("[Chart] No data points created from frequency counts")
            else:
                print("[Chart] No matches found, cannot create frequency chart")
        except Exception as e:
            print(f"[Chart] Error creating frequency chart: {e}")
            import traceback
            traceback.print_exc()

    def _normalize_data_path(self, data_path: str) -> str:
        """Normalize LLM-generated data paths to valid JSONPath."""
        import re

        # Clean up whitespace and convert spaces to dots
        data_path = data_path.strip().replace(" ", ".")

        # Pattern 0: Remove invalid [size:N] or [size up to N] syntax that LLM sometimes generates
        # "genres[size:1][*]" or "genres[size up to 6][*]" -> "genres[*]"
        data_path = re.sub(r"\[size[^\]]*\]", "", data_path)
        print(f"[Chart] After removing [size:N]: {data_path}")

        # Pattern 1: Remove array indices [0], [1], etc. -> treat like []
        # "movies[0].imdbRating" -> "movies.imdbRating"
        data_path = re.sub(r"\[\d+\]", "", data_path)

        # Pattern 2: "movies[].field" or "movies..field" -> "$..field"
        if "[]" in data_path or ".." in data_path:
            # Extract the field name after [] or ..
            field = (
                data_path.split("[].")[-1]
                if "[]." in data_path
                else data_path.split("..")[-1]
            )
            if not field:  # If split didn't work, try getting last segment
                field = data_path.split(".")[-1]
            return f"$..{field}"

        # Pattern 3: "movie.imdbRating" -> "$..imdbRating"
        if "." in data_path and not data_path.startswith("$"):
            # Just use the last part as a recursive search
            field = data_path.split(".")[-1]
            return f"$..{field}"

        # Pattern 4: Already starts with $ - use as is
        if data_path.startswith("$"):
            return data_path

        # Pattern 5: Single field name - search recursively
        return f"$..{data_path}"

    def _infer_chart_type(self, text: str) -> str | None:
        """Infer chart type from text (e.g., component title or user prompt)."""
        if not text:
            return None

        text_lower = text.lower()

        # Check for chart type keywords
        for chart_type, patterns in CHART_TYPE_PATTERNS.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return chart_type

        return None

    @override
    def validate(
        self,
        component: UIComponentMetadata,
        data: InputData,
        errors: list,
    ) -> ComponentDataChart:
        """Validate the chart data."""
        ret = super().validate(component, data, errors)

        # Validate that we have at least one series with data
        if not self._component_data.data or len(self._component_data.data) == 0:
            errors.append(
                {
                    "code": "chart.noData",
                    "message": "Chart component requires at least one data series",
                }
            )

        # Validate chart type is set
        if not self._component_data.chartType:
            errors.append(
                {
                    "code": "chart.noChartType",
                    "message": "Chart component requires chartType to be specified",
                }
            )

        return ret
