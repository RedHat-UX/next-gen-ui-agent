import logging
from collections import Counter
from typing import Any

from next_gen_ui_agent.data_transform import data_transformer_utils
from next_gen_ui_agent.data_transform.data_transformer import DataTransformerBase
from next_gen_ui_agent.data_transform.types import (
    ChartDataPoint,
    ChartSeries,
    ComponentDataBarChart,
    ComponentDataChart,
    ComponentDataDonutChart,
    ComponentDataLineChart,
    ComponentDataMirroredBarChart,
    ComponentDataPieChart,
    DataFieldArrayValue,
)
from next_gen_ui_agent.data_transform.validation.types import (
    ComponentDataValidationError,
)
from next_gen_ui_agent.types import InputData, UIComponentMetadata
from typing_extensions import override

logger = logging.getLogger(__name__)

# Chart type inference patterns
CHART_TYPE_PATTERNS = {
    "bar": ["bar chart", "bar graph"],
    "mirrored-bar": [
        "mirrored bar",
        "mirrored-bar",
        "compare two metrics",
        "roi vs",
        "vs budget",
        "revenue vs profit",
        "compare roi and budget",
    ],
    "line": ["line chart", "line graph", "trend", "over time", "timeline"],
    "pie": ["pie chart", "proportion", "percentage", "share", "distribution"],
    "donut": ["donut chart", "donut graph"],
}


class ChartDataTransformer(DataTransformerBase[ComponentDataChart]):
    COMPONENT_NAME = "chart"
    DEFAULT_CHART_TYPE = "bar"

    def __init__(self):
        self._component_data = ComponentDataBarChart.model_construct(
            chartType=self.DEFAULT_CHART_TYPE, data=[]
        )

    def _set_chart_type(self, chart_type: str) -> None:
        """Set the chart type by reconstructing the component data with the correct class."""
        chart_class_map = {
            "bar": ComponentDataBarChart,
            "line": ComponentDataLineChart,
            "pie": ComponentDataPieChart,
            "donut": ComponentDataDonutChart,
            "mirrored-bar": ComponentDataMirroredBarChart,
        }

        chart_class = chart_class_map.get(chart_type, ComponentDataBarChart)

        # Preserve existing data when reconstructing
        existing_dict = self._component_data.model_dump()
        existing_dict["chartType"] = chart_type

        # Reconstruct with the appropriate class
        self._component_data = chart_class.model_validate(existing_dict)

    @override
    def main_processing(self, json_data: Any, component: UIComponentMetadata):
        """
        Transform input data into chart format.

        The transformer extracts chartType from component and uses fields to build chart data.

        Args:
            json_data: The input data to transform
            component: Component metadata containing configuration and fields
        """
        logger.debug("Starting chart main_processing")
        logger.debug("Component title: %s", component.title)

        # 1. Determine chart type
        chart_type = self._determine_chart_type(component)
        self._set_chart_type(chart_type)
        logger.debug("Chart type: %s", chart_type)

        # 2. Extract data using standard utilities (like other transformers)
        fields = data_transformer_utils.copy_array_fields_from_ui_component_metadata(
            component.fields
        )
        data_transformer_utils.fill_fields_with_array_data(fields, json_data)

        logger.debug("Extracted %d fields", len(fields))
        for i, field in enumerate(fields):
            data_length = len(field.data) if field.data else 0
            logger.debug(
                "  Field %d: %s, data_path=%s, data_length=%d",
                i,
                field.name,
                field.data_path,
                data_length,
            )

        # 3. Transform extracted data into chart series
        self._build_chart_series(fields, chart_type)

        if self._component_data.data:
            logger.debug(
                "Created %d chart series with %d data points in first series",
                len(self._component_data.data),
                len(self._component_data.data[0].data)
                if self._component_data.data
                else 0,
            )
        else:
            logger.warning("No chart data created")

    def _determine_chart_type(self, component: UIComponentMetadata) -> str:
        """Determine chart type from component metadata or infer from title/reason."""
        # Use explicit chartType if provided
        if hasattr(component, "chartType") and component.chartType:
            logger.debug("Using chartType from component: %s", component.chartType)
            return component.chartType

        # Try to infer from component title
        if component.title:
            inferred_type = self._infer_chart_type(component.title)
            if inferred_type:
                logger.debug("Inferred chartType from title: %s", inferred_type)
                return inferred_type

        # Try to infer from reasonForTheComponentSelection
        if (
            hasattr(component, "reasonForTheComponentSelection")
            and component.reasonForTheComponentSelection
        ):
            inferred_type = self._infer_chart_type(
                component.reasonForTheComponentSelection
            )
            if inferred_type:
                logger.debug("Inferred chartType from reason: %s", inferred_type)
                return inferred_type

        # Default to bar chart
        logger.debug("Using default chartType: %s", self.DEFAULT_CHART_TYPE)
        return self.DEFAULT_CHART_TYPE

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

    def _build_chart_series(
        self, fields: list[DataFieldArrayValue], chart_type: str
    ) -> None:
        """Build chart series from extracted field data."""
        if not fields:
            logger.warning("No fields provided, cannot build chart series")
            return

        # Special handling for pie/donut charts with single field
        if chart_type in ["pie", "donut"] and len(fields) == 1:
            self._build_frequency_series(fields[0])
            return

        # Standard chart: First field is x-axis, rest are y-axis series
        if len(fields) < 2:
            logger.warning(
                "Need at least 2 fields for standard charts (x-axis and y-axis)"
            )
            return

        x_field = fields[0]
        y_fields = fields[1:]

        # Extract x values
        x_values = self._extract_x_values(x_field)
        if not x_values:
            logger.warning("No x values found, cannot create chart")
            return

        # Create a series for each y field
        series_list = []
        for y_field in y_fields:
            series = self._create_series_from_field(y_field, x_values)
            if series:
                series_list.append(series)

        self._component_data.data = series_list

    def _extract_x_values(self, x_field: DataFieldArrayValue) -> list[str]:
        """Extract x-axis values from field data."""
        if not x_field.data:
            return []

        x_values = []
        for item in x_field.data:
            # Handle None values
            if item is None:
                continue
            # Handle lists (flatten to first item or join)
            if isinstance(item, list):
                if len(item) > 0:
                    x_values.append(str(item[0]))
            else:
                x_values.append(str(item))

        return x_values

    def _create_series_from_field(
        self, y_field: DataFieldArrayValue, x_values: list[str]
    ) -> ChartSeries | None:
        """Create a chart series from a y-axis field and x-axis values."""
        if not y_field.data:
            logger.debug("No data in field %s", y_field.name)
            return None

        data_points = []
        for i, (x_val, y_item) in enumerate(zip(x_values, y_field.data)):
            # Skip None values
            if y_item is None:
                continue

            # Extract numeric value from y_item
            y_val = self._extract_numeric_value(y_item)
            if y_val is not None:
                data_points.append(ChartDataPoint(x=x_val, y=y_val))

        if not data_points:
            logger.debug("No valid data points in field %s", y_field.name)
            return None

        return ChartSeries(name=y_field.name, data=data_points)

    def _extract_numeric_value(self, item: Any) -> float | None:
        """Extract a numeric value from various data types."""
        # Direct numeric value
        if isinstance(item, (int, float)):
            return float(item)

        # List - take first numeric item
        if isinstance(item, list):
            for sub_item in item:
                if isinstance(sub_item, (int, float)):
                    return float(sub_item)

        # String - try to parse
        if isinstance(item, str):
            try:
                return float(item)
            except (ValueError, TypeError):
                pass

        return None

    def _build_frequency_series(self, field: DataFieldArrayValue) -> None:
        """Build a frequency chart (pie/donut) by counting occurrences."""
        if not field.data:
            logger.warning("No data in field for frequency chart")
            return

        # Flatten and collect all categories
        categories = []
        for item in field.data:
            if item is None:
                continue
            # If item is a list, flatten it
            if isinstance(item, list):
                categories.extend([str(x) for x in item if x is not None])
            else:
                categories.append(str(item))

        if not categories:
            logger.warning("No categories found for frequency chart")
            return

        # Count occurrences
        category_counts = Counter(categories)
        logger.debug("Category counts: %s", dict(category_counts))

        # Create data points from counts
        data_points = []
        for category, count in category_counts.items():
            data_points.append(ChartDataPoint(x=category, y=float(count)))

        self._component_data.data = [ChartSeries(name=field.name, data=data_points)]
        logger.debug("Created frequency chart with %d categories", len(data_points))

    @override
    def validate(
        self,
        component: UIComponentMetadata,
        data: InputData,
        errors: list[ComponentDataValidationError],
    ) -> ComponentDataChart:
        """Validate the chart data."""
        ret = super().validate(component, data, errors)

        # Validate that we have at least one series with data
        if not self._component_data.data or len(self._component_data.data) == 0:
            errors.append(
                ComponentDataValidationError(
                    "chart.noData", "Chart component requires at least one data series"
                )
            )

        # Validate chart type is set
        if not self._component_data.chartType:
            errors.append(
                ComponentDataValidationError(
                    "chart.noChartType",
                    "Chart component requires chartType to be specified",
                )
            )

        return ret
