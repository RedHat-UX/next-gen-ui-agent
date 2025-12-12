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
from next_gen_ui_agent.types import UIComponentMetadata

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
          Multiple metrics over the same x-axis (e.g., "Sales and Profit over time")
        - Multi-series: 3 fields (series_id, x-axis, y-axis)
          Same metric across different entities (e.g., "Revenue for Movie A and Movie B")

        Args:
            fields: Extracted fields with data
            json_data: Original JSON data (unused for line charts)
            component: Component metadata (unused for line charts)
        """
        # For 3 fields, detect whether it's standard (multiple metrics) or multi-series (same metric across entities)
        if len(fields) == 3:
            # Use smart detection based on field length ratios
            if self._is_multi_series_pattern(fields):
                self._build_multi_series_line_chart(fields)
                return
            else:
                # Standard mode: first field is x-axis, other two are different metrics
                self._build_standard_line_chart(fields)
                return

        # Standard line chart (2 fields: x, y OR 4+ fields: x, y1, y2, ...)
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

        Note: x-axis label is set from field[1].name (second field) for multi-series charts.

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
        # For multi-series charts, x-axis is the second field (not the first)
        if len(fields) >= 2:
            self._component_data.x_axis_label = fields[1].name
        logger.debug("Created %d series for multi-series line chart", len(series_list))

    def _is_multi_series_pattern(self, fields: list[DataFieldArrayValue]) -> bool:
        """
        Detect if 3 fields represent multi-series pattern (entity_id, x, y) vs standard (x, y1, y2).

        Multi-series pattern:
        - Field 1 (entities): N values (e.g., 2 movies)
        - Field 2 (x-axis, flattened): N × M values (e.g., 2 movies × 2 weeks = 4)
        - Field 3 (y-axis, flattened): N × M values (e.g., 2 movies × 2 weeks = 4)
        - Key property: len2 and len3 are divisible by len1, and len1 < len2
        - Example:
        {
            "movies": [
                {
                "title": "Movie A",
                "weeklyData": [
                    {"week": "W1", "revenue": 100},
                    {"week": "W2", "revenue": 150}
                ]
                },
                {
                "title": "Movie B",
                "weeklyData": [
                    {"week": "W1", "revenue": 80},
                    {"week": "W2", "revenue": 120}
                ]
                }
            ]
        }
        Field 1: Movie → ["Movie A", "Movie B"] (length: 2) ← Entity IDs
        Field 2: Week → ["W1", "W2", "W1", "W2"] (length: 4) ← Flattened x-axis
        Field 3: Revenue → [100, 150, 80, 120] (length: 4) ← Flattened y-axis
        Detection: len2 and len3 are divisible by len1 (4 = 2 × 2 and 4 = 2 × 2) and len1 < len2 (2 < 4) → Multi-series pattern

        Standard pattern:
        - All fields have equal lengths (same number of data points)
        - Field 1 (x-axis): M values
        - Field 2 (y1): M values
        - Field 3 (y2): M values
        - Example:
        {
            "data": [
                {"month": "Jan", "sales": 100, "profit": 20},
                {"month": "Feb", "sales": 150, "profit": 35},
                {"month": "Mar", "sales": 120, "profit": 25}
            ]
        }
        Field 1: Month → ["Jan", "Feb", "Mar"] (length: 3)
        Field 2: Sales → [100, 150, 120] (length: 3)
        Field 3: Profit → [20, 35, 25] (length: 3)
        Detection: All three fields have equal length (3 = 3 = 3) → Standard pattern

        Returns:
            True if pattern suggests multi-series, False for standard
        """
        if len(fields) != 3:
            return False

        field1 = fields[0]
        field2 = fields[1]
        field3 = fields[2]

        if not field1.data or not field2.data or not field3.data:
            return False

        len1 = len(field1.data)
        len2 = len(field2.data)
        len3 = len(field3.data)

        # Standard pattern: all fields have equal length
        if len1 == len2 == len3:
            logger.debug(
                "Field pattern detection: lengths [%d, %d, %d] -> standard (all equal)",
                len1,
                len2,
                len3,
            )
            return False

        # Multi-series pattern: len2 and len3 should match (x and y have same flattened length)
        # and len1 should be less than len2 (entity count < total data points)
        # Note: We check divisibility as a strong signal, but len1 < len2 with matching len2/len3
        # is sufficient to indicate multi-series structure (processing will handle uneven data)
        if len2 == len3 and len1 > 0 and len2 > 0:
            is_divisible = (len2 % len1 == 0) and (len3 % len1 == 0)
            is_multi_series = len1 < len2  # Entity count must be less than total points

            logger.debug(
                "Field pattern detection: lengths [%d, %d, %d], divisible=%s -> %s",
                len1,
                len2,
                len3,
                is_divisible,
                "multi-series" if is_multi_series else "standard",
            )

            return is_multi_series

        # If len2 != len3, something is wrong, default to standard
        logger.warning(
            "Field pattern detection: x and y fields have different lengths [%d, %d], defaulting to standard",
            len2,
            len3,
        )
        return False
