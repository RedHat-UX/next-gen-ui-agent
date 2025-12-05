"""Donut chart data transformer."""

import logging
from typing import Any

from next_gen_ui_agent.data_transform.chart.base import ChartDataTransformerBase
from next_gen_ui_agent.data_transform.types import (
    ComponentDataDonutChart,
    DataFieldArrayValue,
)
from next_gen_ui_agent.types import UIComponentMetadata

logger = logging.getLogger(__name__)


class DonutChartDataTransformer(ChartDataTransformerBase[ComponentDataDonutChart]):
    """Data transformer for donut charts (chart-donut)."""

    COMPONENT_NAME = "chart-donut"
    _component_data: ComponentDataDonutChart

    def __init__(self):
        self._component_data = ComponentDataDonutChart.model_construct(data=[])

    def _build_chart_data(
        self,
        fields: list[DataFieldArrayValue],
        json_data: Any,
        component: UIComponentMetadata,
    ) -> None:
        """
        Build donut chart data by counting occurrences of categories.

        Donut charts expect exactly 1 field containing categories to count.

        Args:
            fields: Extracted fields with data
            json_data: Original JSON data (unused for donut charts)
            component: Component metadata (unused for donut charts)
        """
        if not fields or len(fields) != 1:
            logger.warning("Donut chart expects exactly 1 field")
            return

        self._build_frequency_series(fields[0])
