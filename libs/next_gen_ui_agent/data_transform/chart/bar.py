"""Bar chart data transformer."""

import logging
from typing import Any

from next_gen_ui_agent.data_transform.chart.base import ChartDataTransformerBase
from next_gen_ui_agent.data_transform.types import (
    ComponentDataBarChart,
    DataFieldArrayValue,
)
from next_gen_ui_agent.data_transform.validation.types import (
    ComponentDataValidationError,
)
from next_gen_ui_agent.types import InputData, UIComponentMetadata
from typing_extensions import override

logger = logging.getLogger(__name__)


class BarChartDataTransformer(ChartDataTransformerBase[ComponentDataBarChart]):
    """Data transformer for bar charts (chart-bar)."""

    COMPONENT_NAME = "chart-bar"
    _component_data: ComponentDataBarChart

    def __init__(self):
        self._component_data = ComponentDataBarChart.model_construct(data=[])

    def _build_chart_data(
        self,
        fields: list[DataFieldArrayValue],
        json_data: Any,
        component: UIComponentMetadata,
    ) -> None:
        """
        Build bar chart data: First field is x-axis, rest are y-axis series.

        Args:
            fields: Extracted fields with data
            json_data: Original JSON data (unused for bar charts)
            component: Component metadata (unused for bar charts)
        """
        if len(fields) < 2:
            logger.warning("Bar chart needs at least 2 fields (x-axis and y-axis)")
            return

        x_field = fields[0]
        y_fields = fields[1:]

        # Extract x values
        x_values = self._extract_x_values(x_field)
        if not x_values:
            logger.warning("No x values found, cannot create bar chart")
            return

        # Create a series for each y field
        series_list = []
        for y_field in y_fields:
            series = self._create_series_from_field(y_field, x_values)
            if series:
                series_list.append(series)

        self._component_data.data = series_list

    @override
    def validate(
        self,
        component: UIComponentMetadata,
        data: InputData,
        errors: list[ComponentDataValidationError],
    ) -> ComponentDataBarChart:
        """Validate the bar chart data."""
        super().validate(component, data, errors)

        # Validate that we have at least one series with data
        if not self._component_data.data or len(self._component_data.data) == 0:
            errors.append(
                ComponentDataValidationError(
                    "chart.noData", "Bar chart requires at least one data series"
                )
            )

        # Validate component type is set correctly (defensive check)
        component_value = getattr(self._component_data, "component", None)
        if component_value != "chart-bar":
            errors.append(
                ComponentDataValidationError(
                    "chart.invalidComponent",
                    f"Expected component 'chart-bar', got '{component_value}'",
                )
            )

        return self._component_data
