"""Mirrored bar chart data transformer."""

import logging
from typing import Any

from next_gen_ui_agent.data_transform.chart.base import ChartDataTransformerBase
from next_gen_ui_agent.data_transform.types import (
    ComponentDataMirroredBarChart,
    DataFieldArrayValue,
)
from next_gen_ui_agent.data_transform.validation.types import (
    ComponentDataValidationError,
)
from next_gen_ui_agent.types import UIComponentMetadata
from typing_extensions import override

logger = logging.getLogger(__name__)


class MirroredBarChartDataTransformer(
    ChartDataTransformerBase[ComponentDataMirroredBarChart]
):
    """Data transformer for mirrored bar charts (chart-mirrored-bar)."""

    COMPONENT_NAME = "chart-mirrored-bar"
    _component_data: ComponentDataMirroredBarChart

    def __init__(self):
        self._component_data = ComponentDataMirroredBarChart.model_construct(data=[])

    def _build_chart_data(
        self,
        fields: list[DataFieldArrayValue],
        json_data: Any,
        component: UIComponentMetadata,
    ) -> None:
        """
        Build mirrored bar chart data: Exactly 3 fields (x-axis, metric1, metric2).

        The mirrored bar chart is used to compare two metrics side-by-side with
        different scales. The rendering handles the mirroring visualization.

        Args:
            fields: Extracted fields with data (must be exactly 3)
            json_data: Original JSON data (unused for mirrored bar charts)
            component: Component metadata (unused for mirrored bar charts)
        """
        if len(fields) != 3:
            logger.warning(
                "Mirrored bar chart expects exactly 3 fields (x-axis, metric1, metric2)"
            )
            return

        x_field = fields[0]
        y_fields = fields[1:]

        # Extract x values
        x_values = self._extract_x_values(x_field)
        if not x_values:
            logger.warning("No x values found, cannot create mirrored bar chart")
            return

        # Create a series for each metric (should be exactly 2)
        series_list = []
        for y_field in y_fields:
            series = self._create_series_from_field(y_field, x_values)
            if series:
                series_list.append(series)

        if len(series_list) != 2:
            logger.warning(
                "Mirrored bar chart should have exactly 2 data series, got %d",
                len(series_list),
            )

        self._component_data.data = series_list

    @override
    def _validate_data_series(self, errors: list[ComponentDataValidationError]) -> None:
        """Validate that the mirrored bar chart has exactly 2 series."""
        if not self._component_data.data or len(self._component_data.data) != 2:
            errors.append(
                ComponentDataValidationError(
                    "chart.invalidSeriesCount",
                    f"Mirrored bar chart requires exactly 2 data series, got {len(self._component_data.data) if self._component_data.data else 0}",
                )
            )
