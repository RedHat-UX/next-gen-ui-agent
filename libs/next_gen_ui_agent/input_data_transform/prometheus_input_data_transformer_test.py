"""Tests for Prometheus Input Data Transformer."""

import json

import pytest
from next_gen_ui_agent.input_data_transform.prometheus_input_data_transformer import (
    PrometheusInputDataTransformer,
)
from next_gen_ui_agent.types import InputData


def test_transform_basic_prometheus_data():
    """Test basic transformation of Prometheus matrix result."""
    transformer = PrometheusInputDataTransformer()

    prom_data = {
        "result": [
            {
                "metric": {
                    "__name__": "instance:node_cpu_utilisation:rate1m",
                    "pod": "node-exporter-zv64p",
                },
                "values": [
                    [1763032771.933, "0.051437499999995695"],
                    [1763032831.933, "0.0499583333333351"],
                ],
            }
        ],
        "resultType": "matrix",
    }

    result = transformer.transform(json.dumps(prom_data))

    assert result["metadata"]["source"] == "prometheus"
    assert result["metadata"]["resultType"] == "matrix"
    assert len(result["series"]) == 1
    assert result["series"][0]["name"] == "node-exporter-zv64p"
    assert len(result["series"][0]["dataPoints"]) == 2
    assert result["series"][0]["dataPoints"][0]["value"] == pytest.approx(
        0.0514, rel=1e-3
    )
    assert "time" in result["series"][0]["dataPoints"][0]


def test_transform_multiple_series():
    """Test transformation with multiple time series."""
    transformer = PrometheusInputDataTransformer()

    prom_data = {
        "result": [
            {"metric": {"pod": "pod-a"}, "values": [[1700000000, "10.5"]]},
            {"metric": {"pod": "pod-b"}, "values": [[1700000000, "20.3"]]},
        ],
        "resultType": "matrix",
    }

    result = transformer.transform(json.dumps(prom_data))

    assert len(result["series"]) == 2
    assert result["series"][0]["name"] == "pod-a"
    assert result["series"][1]["name"] == "pod-b"
    assert result["series"][0]["dataPoints"][0]["value"] == 10.5
    assert result["series"][1]["dataPoints"][0]["value"] == 20.3


def test_series_name_extraction_priority():
    """Test that series name extraction follows priority order."""
    transformer = PrometheusInputDataTransformer()

    # Test with pod label (highest priority)
    prom_data_pod = {
        "result": [
            {
                "metric": {
                    "__name__": "metric_name",
                    "instance": "inst-123",
                    "pod": "my-pod",
                },
                "values": [[1700000000, "1.0"]],
            }
        ],
        "resultType": "matrix",
    }
    result = transformer.transform(json.dumps(prom_data_pod))
    assert result["series"][0]["name"] == "my-pod"

    # Test with instance label (second priority, no pod)
    prom_data_instance = {
        "result": [
            {
                "metric": {"__name__": "metric_name", "instance": "inst-123"},
                "values": [[1700000000, "1.0"]],
            }
        ],
        "resultType": "matrix",
    }
    result = transformer.transform(json.dumps(prom_data_instance))
    assert result["series"][0]["name"] == "inst-123"

    # Test with only __name__ (lowest priority)
    prom_data_name = {
        "result": [
            {"metric": {"__name__": "metric_name"}, "values": [[1700000000, "1.0"]]}
        ],
        "resultType": "matrix",
    }
    result = transformer.transform(json.dumps(prom_data_name))
    assert result["series"][0]["name"] == "metric_name"


def test_transform_with_input_data():
    """Test transformation using InputData wrapper."""
    transformer = PrometheusInputDataTransformer()

    input_data = InputData(
        id="test-metrics",
        data=json.dumps(
            {
                "result": [
                    {"metric": {"pod": "test-pod"}, "values": [[1700000000, "5.5"]]}
                ],
                "resultType": "matrix",
            }
        ),
    )

    result = transformer.transform_input_data(input_data)

    assert len(result["series"]) == 1
    assert result["series"][0]["name"] == "test-pod"


def test_invalid_json():
    """Test error handling for invalid JSON."""
    transformer = PrometheusInputDataTransformer()

    with pytest.raises(ValueError, match="Invalid JSON format"):
        transformer.transform("not valid json {")


def test_missing_result_field():
    """Test error handling when 'result' field is missing."""
    transformer = PrometheusInputDataTransformer()

    with pytest.raises(ValueError, match="missing 'result' field"):
        transformer.transform(json.dumps({"resultType": "matrix"}))


def test_non_matrix_result_type():
    """Test handling of non-matrix result types (should warn but process)."""
    transformer = PrometheusInputDataTransformer()

    prom_data = {
        "result": [{"metric": {"pod": "test"}, "values": [[1700000000, "1.0"]]}],
        "resultType": "vector",  # Not matrix
    }

    # Should still process but log warning
    result = transformer.transform(json.dumps(prom_data))
    assert result["metadata"]["resultType"] == "vector"
    assert len(result["series"]) == 1


def test_empty_values():
    """Test handling of series with no values."""
    transformer = PrometheusInputDataTransformer()

    prom_data = {
        "result": [
            {"metric": {"pod": "empty-pod"}, "values": []},
            {"metric": {"pod": "valid-pod"}, "values": [[1700000000, "1.0"]]},
        ],
        "resultType": "matrix",
    }

    result = transformer.transform(json.dumps(prom_data))

    # Should skip empty series
    assert len(result["series"]) == 1
    assert result["series"][0]["name"] == "valid-pod"


def test_invalid_value_conversion():
    """Test handling of values that cannot be converted to float."""
    transformer = PrometheusInputDataTransformer()

    prom_data = {
        "result": [
            {
                "metric": {"pod": "test"},
                "values": [
                    [1700000000, "1.0"],
                    [1700000001, "invalid"],
                    [1700000002, "2.0"],
                ],
            }
        ],
        "resultType": "matrix",
    }

    result = transformer.transform(json.dumps(prom_data))

    # Should skip invalid value
    assert len(result["series"][0]["dataPoints"]) == 2
    assert result["series"][0]["dataPoints"][0]["value"] == 1.0
    assert result["series"][0]["dataPoints"][1]["value"] == 2.0


def test_timestamp_formatting():
    """Test timestamp formatting to HH:MM format."""
    transformer = PrometheusInputDataTransformer()

    # Use a known timestamp: 2023-11-15 14:30:00
    timestamp = 1700058600.0

    prom_data = {
        "result": [{"metric": {"pod": "test"}, "values": [[timestamp, "1.0"]]}],
        "resultType": "matrix",
    }

    result = transformer.transform(json.dumps(prom_data))

    # Check that time is formatted as HH:MM
    time_str = result["series"][0]["dataPoints"][0]["time"]
    assert ":" in time_str
    assert len(time_str) == 5  # HH:MM format


def test_metric_preserved_in_output():
    """Test that original metric labels are preserved."""
    transformer = PrometheusInputDataTransformer()

    original_metric = {
        "__name__": "cpu_usage",
        "pod": "my-pod",
        "namespace": "default",
        "node": "worker-1",
    }

    prom_data = {
        "result": [{"metric": original_metric, "values": [[1700000000, "1.0"]]}],
        "resultType": "matrix",
    }

    result = transformer.transform(json.dumps(prom_data))

    # Original metric should be preserved
    assert result["series"][0]["metric"] == original_metric


def test_real_world_cpu_data():
    """Test with real-world-like CPU utilization data."""
    transformer = PrometheusInputDataTransformer()

    prom_data = {
        "result": [
            {
                "metric": {
                    "__name__": "instance:node_cpu_utilisation:rate1m",
                    "container": "kube-rbac-proxy",
                    "endpoint": "https",
                    "instance": "ip-10-0-18-210.ec2.internal",
                    "job": "node-exporter",
                    "pod": "node-exporter-zv64p",
                },
                "values": [
                    [1763032771.933, "0.051437499999995695"],
                    [1763032831.933, "0.0499583333333351"],
                    [1763032891.933, "0.0639791666666858"],
                ],
            }
        ],
        "resultType": "matrix",
    }

    result = transformer.transform(json.dumps(prom_data))

    assert len(result["series"]) == 1
    assert result["series"][0]["name"] == "node-exporter-zv64p"
    assert len(result["series"][0]["dataPoints"]) == 3

    # Check that values are properly converted (percentages)
    values = [dp["value"] for dp in result["series"][0]["dataPoints"]]
    assert all(0 < v < 1 for v in values)  # CPU utilization should be 0-1
