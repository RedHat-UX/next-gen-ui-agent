"""Line chart data transformer."""

import logging
from typing import Any

from next_gen_ui_agent.data_transform.chart.base import ChartDataTransformerBase
from next_gen_ui_agent.data_transform.types import (
    ChartDataPoint,
    ChartSeries,
    ComponentDataLineChart,
    DataFieldArrayValue,
)
from next_gen_ui_agent.data_transform.validation.types import (
    ComponentDataValidationError,
)
from next_gen_ui_agent.types import InputData, UIComponentMetadata
from typing_extensions import override

logger = logging.getLogger(__name__)


class LineChartDataTransformer(ChartDataTransformerBase[ComponentDataLineChart]):
    """Data transformer for line charts (chart-line)."""

    COMPONENT_NAME = "chart-line"
    _component_data: ComponentDataLineChart

    def __init__(self):
        self._component_data = ComponentDataLineChart.model_construct(data=[])

    def _build_chart_data(
        self,
        fields: list[DataFieldArrayValue],
        json_data: Any,
        component: UIComponentMetadata,
    ) -> None:
        """
        Build line chart data.

        Supports two modes:
        - Standard: 2+ fields (x-axis, y-axis1, y-axis2, ...)
        - Multi-series: 3 fields (series_id, x-axis, y-axis)

        Args:
            fields: Extracted fields with data
            json_data: Original JSON data (unused for line charts)
            component: Component metadata (unused for line charts)
        """
        # Multi-series line chart (3 fields: series_id, x, y)
        if len(fields) == 3:
            self._build_multi_series_line_chart(fields)
            return

        # Standard line chart (2+ fields: x, y1, y2, ...)
        if len(fields) >= 2:
            self._build_standard_line_chart(fields)
            return

        logger.warning("Line chart needs at least 2 fields")

    def _build_standard_line_chart(self, fields: list[DataFieldArrayValue]) -> None:
        """Build standard line chart: First field is x-axis, rest are y-axis series."""
        x_field = fields[0]
        y_fields = fields[1:]

        # Extract x values
        x_values = self._extract_x_values(x_field)
        if not x_values:
            logger.warning("No x values found, cannot create line chart")
            return

        # Create a series for each y field
        series_list = []
        for y_field in y_fields:
            series = self._create_series_from_field(y_field, x_values)
            if series:
                series_list.append(series)

        self._component_data.data = series_list

    def _build_multi_series_line_chart(self, fields: list[DataFieldArrayValue]) -> None:
        """
        Build multi-series line chart from 3 fields: series_id, x, y.

        This handles cases like weekly revenue per movie where:
        - Field 1: Movie title (series identifier)
        - Field 2: Week number (x-axis)
        - Field 3: Revenue (y-axis)

        When JSONPath extracts nested arrays, it flattens them sequentially:
        - series_ids: [movie1, movie2, ..., movieN]
        - x_values: [week1_m1, week2_m1, ..., weekK_m1, week1_m2, ..., weekK_mN]
        - y_values: [rev1_m1, rev2_m1, ..., revK_m1, rev1_m2, ..., revK_mN]

        We calculate how many points belong to each series and group them.
        """
        series_field, x_field, y_field = fields

        if not series_field.data or not x_field.data or not y_field.data:
            logger.warning(
                "Missing data in one or more fields for multi-series line chart"
            )
            return

        series_ids = series_field.data
        x_vals = x_field.data
        y_vals = y_field.data

        num_series = len(series_ids)
        num_points = len(x_vals)

        logger.debug(
            "Building multi-series line chart: %d series, %d x values, %d y values",
            num_series,
            num_points,
            len(y_vals),
        )

        # Calculate points per series (assuming equal distribution)
        if num_points % num_series != 0:
            logger.warning(
                "Data point count (%d) not evenly divisible by series count (%d). "
                "This may indicate incorrect JSONPath or data structure.",
                num_points,
                num_series,
            )
            return

        points_per_series = num_points // num_series
        logger.debug("Each series should have %d data points", points_per_series)

        # Build series list
        series_list = []
        for i, series_id in enumerate(series_ids):
            start_idx = i * points_per_series
            end_idx = start_idx + points_per_series

            data_points = []
            for j in range(start_idx, end_idx):
                # Extract numeric value for y
                numeric_y = self._extract_numeric_value(y_vals[j])
                if numeric_y is not None:
                    data_points.append(ChartDataPoint(x=str(x_vals[j]), y=numeric_y))

            if data_points:  # Only add series if it has data
                series_list.append(ChartSeries(name=str(series_id), data=data_points))

        self._component_data.data = series_list
        logger.debug("Created %d series for multi-series line chart", len(series_list))

    @override
    def validate(
        self,
        component: UIComponentMetadata,
        data: InputData,
        errors: list[ComponentDataValidationError],
    ) -> ComponentDataLineChart:
        """Validate the line chart data."""
        super().validate(component, data, errors)

        # Validate that we have at least one series with data
        if not self._component_data.data or len(self._component_data.data) == 0:
            errors.append(
                ComponentDataValidationError(
                    "chart.noData", "Line chart requires at least one data series"
                )
            )

        # Validate component type is set correctly (defensive check)
        component_value = getattr(self._component_data, "component", None)
        if component_value != "chart-line":
            errors.append(
                ComponentDataValidationError(
                    "chart.invalidComponent",
                    f"Expected component 'chart-line', got '{component_value}'",
                )
            )

        return self._component_data
