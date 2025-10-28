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
    "bar": ["bar chart", "bar graph", "compare", "comparison"],
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
                self._create_single_point_chart(json_data, component, fields[0])
            return

        print(f"[Chart] Have {len(fields)} fields, proceeding with extraction")

        # First field is typically the x-axis (categories/labels)
        # Remaining fields are y-axis values (can be multiple series)
        x_field = fields[0]
        y_fields = fields[1:]

        print(
            f"[Chart] x_field: {x_field.name}, y_fields: {[f.name for f in y_fields]}"
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

    def _normalize_data_path(self, data_path: str) -> str:
        """Normalize LLM-generated data paths to valid JSONPath."""
        import re

        # Clean up whitespace and convert spaces to dots
        data_path = data_path.strip().replace(" ", ".")

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
