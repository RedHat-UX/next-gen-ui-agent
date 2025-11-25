"""Pie chart data transformer."""

import logging
from collections import Counter
from typing import Any

from next_gen_ui_agent.data_transform.chart.base import ChartDataTransformerBase
from next_gen_ui_agent.data_transform.types import (
    ChartDataPoint,
    ChartSeries,
    ComponentDataPieChart,
    DataFieldArrayValue,
)
from next_gen_ui_agent.data_transform.validation.types import (
    ComponentDataValidationError,
)
from next_gen_ui_agent.types import InputData, UIComponentMetadata
from typing_extensions import override

logger = logging.getLogger(__name__)


class PieChartDataTransformer(ChartDataTransformerBase):
    """Data transformer for pie charts (chart-pie)."""

    COMPONENT_NAME = "chart-pie"

    def __init__(self):
        self._component_data = ComponentDataPieChart.model_construct(data=[])

    def _build_chart_data(
        self,
        fields: list[DataFieldArrayValue],
        json_data: Any,
        component: UIComponentMetadata,
    ) -> None:
        """
        Build pie chart data by counting occurrences of categories.

        Pie charts expect exactly 1 field containing categories to count.

        Args:
            fields: Extracted fields with data
            json_data: Original JSON data (unused for pie charts)
            component: Component metadata (unused for pie charts)
        """
        if not fields or len(fields) != 1:
            logger.warning("Pie chart expects exactly 1 field")
            return

        self._build_frequency_series(fields[0])

    def _build_frequency_series(self, field: DataFieldArrayValue) -> None:
        """Build a frequency chart by counting occurrences."""
        if not field.data:
            logger.warning("No data in field for pie chart")
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
            logger.warning("No categories found for pie chart")
            return

        # Count occurrences
        category_counts = Counter(categories)
        logger.debug("Category counts: %s", dict(category_counts))

        # Create data points from counts
        data_points = []
        for category, count in category_counts.items():
            data_points.append(ChartDataPoint(x=category, y=float(count)))

        self._component_data.data = [ChartSeries(name=field.name, data=data_points)]
        logger.debug("Created pie chart with %d categories", len(data_points))

    @override
    def validate(
        self,
        component: UIComponentMetadata,
        data: InputData,
        errors: list[ComponentDataValidationError],
    ) -> ComponentDataPieChart:
        """Validate the pie chart data."""
        ret = super().validate(component, data, errors)

        # Validate that we have at least one series with data
        if not self._component_data.data or len(self._component_data.data) == 0:
            errors.append(
                ComponentDataValidationError(
                    "chart.noData", "Pie chart requires at least one data series"
                )
            )

        # Validate component type is set correctly
        if self._component_data.component != "chart-pie":
            errors.append(
                ComponentDataValidationError(
                    "chart.invalidComponent",
                    f"Expected component 'chart-pie', got '{self._component_data.component}'",
                )
            )

        return ret
