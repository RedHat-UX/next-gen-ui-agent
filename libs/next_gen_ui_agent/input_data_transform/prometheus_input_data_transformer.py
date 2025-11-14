"""Input Data transformer from Prometheus time-series format.

This transformer handles Prometheus query_range results with resultType="matrix".
It converts Prometheus-specific time-series data into a normalized format that
the NGUI agent's chart transformer can process.
"""

import json
import logging
from datetime import datetime
from typing import Any, Literal

from next_gen_ui_agent.types import InputDataTransformerBase

logger = logging.getLogger(__name__)


class PrometheusInputDataTransformer(InputDataTransformerBase):
    """Input Data transformer from Prometheus matrix result format.

    Transforms Prometheus /query_range results into a normalized time-series format
    suitable for chart rendering.

    Expected input format:
    {
        "result": [
            {
                "metric": {"__name__": "...", "pod": "...", ...},
                "values": [[timestamp, "value"], ...]
            }
        ],
        "resultType": "matrix"
    }

    Output format:
    {
        "metadata": {"source": "prometheus", "resultType": "matrix"},
        "series": [
            {
                "name": "series-name",
                "metric": {...},
                "dataPoints": [
                    {"timestamp": 1234567890.123, "value": 0.051, "time": "14:30"},
                    ...
                ]
            }
        ]
    }
    """

    TRANSFORMER_NAME = "prometheus"

    TRANSFORMER_NAME_LITERAL = Literal["prometheus"]

    # Priority order for extracting series names from metric labels
    METRIC_LABEL_PRIORITY = ["pod", "instance", "job", "container", "node", "__name__"]

    def transform(self, input_data: str) -> Any:
        """Transform Prometheus matrix result into normalized time-series format.

        Args:
            input_data: JSON string containing Prometheus query_range result

        Returns:
            Normalized dictionary with series data suitable for chart rendering

        Raises:
            ValueError: If input is not valid Prometheus format
        """
        try:
            prom_data = json.loads(input_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in Prometheus data: {e}") from e

        # Validate Prometheus structure
        if not isinstance(prom_data, dict):
            raise ValueError("Prometheus data must be a JSON object")

        if "result" not in prom_data:
            raise ValueError(
                "Invalid Prometheus format: missing 'result' field. "
                "Expected Prometheus query_range response format."
            )

        result_type = prom_data.get("resultType")
        if result_type != "matrix":
            logger.warning(
                "Prometheus resultType is '%s', expected 'matrix'. "
                "Transformation may not work correctly.",
                result_type,
            )

        # Transform to normalized format
        normalized = {
            "metadata": {
                "source": "prometheus",
                "resultType": result_type or "unknown",
            },
            "series": self._transform_series(prom_data["result"]),
        }

        logger.info(
            "Transformed Prometheus data with %d series", len(normalized["series"])
        )

        return normalized

    def _transform_series(self, result_data: list) -> list[dict]:
        """Transform Prometheus result array into normalized series format.

        Args:
            result_data: List of Prometheus series from the 'result' field

        Returns:
            List of normalized series dictionaries
        """
        series_list = []

        for series_data in result_data:
            if not isinstance(series_data, dict):
                logger.warning("Skipping invalid series data: not a dictionary")
                continue

            metric = series_data.get("metric", {})
            values = series_data.get("values", [])

            if not values:
                logger.warning("Skipping series with no values")
                continue

            # Extract series name from metric labels
            series_name = self._extract_series_name(metric)

            # Convert timestamp/value pairs to data points
            data_points = []
            for value_pair in values:
                if not isinstance(value_pair, list) or len(value_pair) != 2:
                    logger.warning("Skipping invalid value pair: %s", value_pair)
                    continue

                timestamp, value_str = value_pair

                try:
                    # Convert value to float
                    value = float(value_str)
                except (ValueError, TypeError) as e:
                    logger.warning(
                        "Skipping value that cannot be converted to float: %s (%s)",
                        value_str,
                        e,
                    )
                    continue

                data_points.append(
                    {
                        "timestamp": timestamp,
                        "value": value,
                        "time": self._format_timestamp(timestamp),
                    }
                )

            if data_points:
                series_list.append(
                    {
                        "name": series_name,
                        "metric": metric,
                        "dataPoints": data_points,
                    }
                )

        return series_list

    def _extract_series_name(self, metric: dict) -> str:
        """Extract meaningful series name from Prometheus metric labels.

        Tries labels in priority order: pod, instance, job, container, node, __name__.
        Falls back to "Series" if no labels found.

        Args:
            metric: Dictionary of Prometheus metric labels

        Returns:
            String name for the series
        """
        if not isinstance(metric, dict):
            return "Series"

        # Try labels in priority order
        for label in self.METRIC_LABEL_PRIORITY:
            if label in metric and metric[label]:
                return str(metric[label])

        # If no priority labels found, use first available label
        if metric:
            first_key = next(iter(metric))
            return str(metric[first_key])

        return "Series"

    def _format_timestamp(self, timestamp: float) -> str:
        """Format Unix timestamp to readable time string (HH:MM format).

        Args:
            timestamp: Unix timestamp in seconds (can include fractional seconds)

        Returns:
            Formatted time string in HH:MM format
        """
        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%H:%M")
        except (ValueError, OSError) as e:
            logger.warning("Failed to format timestamp %s: %s", timestamp, e)
            return str(int(timestamp))
