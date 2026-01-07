"""Base class for chart data transformers with shared utility methods."""

import logging
from abc import abstractmethod
from collections import Counter
from typing import Any, Generic, TypeVar

from next_gen_ui_agent.data_transform import data_transformer_utils
from next_gen_ui_agent.data_transform.data_transformer import DataTransformerBase
from next_gen_ui_agent.data_transform.types import (
    ChartDataPoint,
    ChartSeries,
    ComponentDataChart,
    DataFieldArrayValue,
)
from next_gen_ui_agent.data_transform.validation.types import (
    ComponentDataValidationError,
)
from next_gen_ui_agent.types import InputData, UIComponentMetadata
from typing_extensions import override

logger = logging.getLogger(__name__)

TChart = TypeVar("TChart", bound=ComponentDataChart)


class ChartDataTransformerBase(DataTransformerBase[TChart], Generic[TChart]):
    """Base class for all chart transformers with shared utility methods."""

    @override
    def main_processing(self, json_data: Any, component: UIComponentMetadata):
        """
        Transform input data into chart format.

        The transformer uses component metadata and fields to build chart data.

        Args:
            json_data: The input data to transform
            component: Component metadata containing configuration and fields
        """
        logger.debug("Starting chart main_processing for %s", self.COMPONENT_NAME)
        logger.debug("Component title: %s", component.title)

        # Extract data using standard utilities (like other transformers)
        # Charts allow nested arrays (e.g., movies[*].weeklyData[*]) because they
        # have flattening logic in their _build_chart_data implementations
        fields = data_transformer_utils.copy_array_fields_from_ui_component_metadata(
            component.fields
        )
        data_transformer_utils.fill_fields_with_array_data(
            fields, json_data, allow_nested_arrays=True
        )

        logger.debug("Extracted %d fields", len(fields))
        if logger.isEnabledFor(logging.DEBUG):
            for i, field in enumerate(fields):
                data_length = len(field.data) if field.data else 0
                logger.debug(
                    "  Field %d: %s, data_path=%s, data_length=%d",
                    i,
                    field.name,
                    field.data_path,
                    data_length,
                )

        # Build chart data (implemented by subclasses)
        self._build_chart_data(fields, json_data, component)

        # Set x-axis label from appropriate field name (all series share the same x-axis)
        # For most charts, first field is x-axis. For multi-series line charts, second field is x-axis.
        # Subclasses can override this by setting x_axis_label in _build_chart_data if needed.
        if fields and len(fields) > 0 and not self._component_data.x_axis_label:
            self._component_data.x_axis_label = fields[0].name

        if self._component_data.data:
            logger.debug(
                "Created %d chart series with %d data points in first series",
                len(self._component_data.data),
                (
                    len(self._component_data.data[0].data)
                    if self._component_data.data
                    else 0
                ),
            )
        else:
            logger.warning("No chart data created")

    @abstractmethod
    def _build_chart_data(
        self,
        fields: list[DataFieldArrayValue],
        json_data: Any,
        component: UIComponentMetadata,
    ) -> None:
        """
        Build chart-specific data structure. Implemented by each subclass.

        Args:
            fields: Extracted fields with data
            json_data: Original JSON data
            component: Component metadata
        """
        pass

    # ===== Shared Utility Methods =====

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
        """
        Build a frequency chart by counting occurrences.

        Used by pie and donut charts to count category occurrences.

        Args:
            field: Field containing category data to count
        """
        if not field.data:
            logger.warning("No data in field for %s", self.COMPONENT_NAME)
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
            logger.warning("No categories found for %s", self.COMPONENT_NAME)
            return

        # Count occurrences
        category_counts = Counter(categories)
        logger.debug("Category counts: %s", dict(category_counts))

        # Create data points from counts
        data_points = []
        for category, count in category_counts.items():
            data_points.append(ChartDataPoint(x=category, y=float(count)))

        self._component_data.data = [ChartSeries(name=field.name, data=data_points)]
        logger.debug(
            "Created %s with %d categories", self.COMPONENT_NAME, len(data_points)
        )

    # ===== Validation Methods =====

    @override
    def validate(
        self,
        component: UIComponentMetadata,
        data: InputData,
        errors: list[ComponentDataValidationError],
    ) -> TChart:
        """
        Validate the chart data.

        Subclasses can override _validate_data_series for custom series validation.
        """
        super().validate(component, data, errors)

        # Validate data series (can be overridden by subclasses)
        self._validate_data_series(errors)

        # Validate component type is set correctly (defensive check)
        component_value = getattr(self._component_data, "component", None)
        if component_value != self.COMPONENT_NAME:
            errors.append(
                ComponentDataValidationError(
                    "chart.invalidComponent",
                    f"Expected component '{self.COMPONENT_NAME}', got '{component_value}'",
                )
            )

        return self._component_data

    def _validate_data_series(self, errors: list[ComponentDataValidationError]) -> None:
        """
        Validate that the chart has valid data series.

        Override in subclasses for custom validation (e.g., mirrored bar requires exactly 2).
        """
        if not self._component_data.data or len(self._component_data.data) == 0:
            errors.append(
                ComponentDataValidationError(
                    "chart.noData",
                    f"{self.COMPONENT_NAME} requires at least one data series",
                )
            )
