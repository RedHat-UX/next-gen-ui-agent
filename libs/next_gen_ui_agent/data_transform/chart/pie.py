"""Pie chart data transformer."""

import logging
from typing import Any

from next_gen_ui_agent.data_transform.chart.base import ChartDataTransformerBase
from next_gen_ui_agent.data_transform.types import (
    ComponentDataPieChart,
    DataFieldArrayValue,
)
from next_gen_ui_agent.types import UIComponentMetadata

logger = logging.getLogger(__name__)


class PieChartDataTransformer(ChartDataTransformerBase[ComponentDataPieChart]):
    """Data transformer for pie charts (chart-pie)."""

    COMPONENT_NAME = "chart-pie"
    _component_data: ComponentDataPieChart

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
