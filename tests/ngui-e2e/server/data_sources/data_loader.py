"""Data loader for mock OpenShift resources.

This module provides sample data for pods and nodes that matches
the data used in the frontend inline datasets.
"""

# Sample pods data matching the frontend dataset
PODS_DATA = [
    {
        "name": "pod-a-123",
        "status": "Running",
        "created": "2024-01-10T10:00:00Z",
        "cpu_usage": 0.15,
        "memory_usage": 0.3,
        "namespace": "default",
    },
    {
        "name": "pod-b-456",
        "status": "Pending",
        "created": "2024-01-10T11:30:00Z",
        "cpu_usage": 0.05,
        "memory_usage": 0.1,
        "namespace": "kube-system",
    },
    {
        "name": "pod-c-789",
        "status": "Error",
        "created": "2024-01-09T14:00:00Z",
        "cpu_usage": 0.2,
        "memory_usage": 0.45,
        "namespace": "app-dev",
    },
    {
        "name": "pod-d-101",
        "status": "Running",
        "created": "2024-01-11T08:00:00Z",
        "cpu_usage": 0.1,
        "memory_usage": 0.25,
        "namespace": "default",
    },
    {
        "name": "pod-e-202",
        "status": "Running",
        "created": "2024-01-12T09:15:00Z",
        "cpu_usage": 0.35,
        "memory_usage": 0.55,
        "namespace": "production",
    },
    {
        "name": "pod-f-303",
        "status": "Pending",
        "created": "2024-01-12T12:45:00Z",
        "cpu_usage": 0.02,
        "memory_usage": 0.08,
        "namespace": "staging",
    },
    {
        "name": "pod-g-404",
        "status": "Running",
        "created": "2024-01-13T07:20:00Z",
        "cpu_usage": 0.28,
        "memory_usage": 0.42,
        "namespace": "monitoring",
    },
]

# Sample nodes data matching the frontend dataset
NODES_DATA = [
    {
        "name": "worker-0",
        "status": "Ready",
        "created": "2024-01-05T08:00:00Z",
        "cpu": 0.12,
        "memory": 0.45,
        "version": "v1.27.6",
        "region": "us-east-1",
    },
    {
        "name": "worker-1",
        "status": "Ready",
        "created": "2024-01-06T09:15:00Z",
        "cpu": 0.35,
        "memory": 0.65,
        "version": "v1.27.6",
        "region": "us-west-2",
    },
    {
        "name": "master-0",
        "status": "Ready",
        "created": "2024-01-04T10:30:00Z",
        "cpu": 0.22,
        "memory": 0.85,
        "version": "v1.27.6",
        "region": "us-east-1",
    },
    {
        "name": "worker-2",
        "status": "NotReady",
        "created": "2024-01-07T14:20:00Z",
        "cpu": 0.0,
        "memory": 0.0,
        "version": "v1.27.6",
        "region": "eu-west-1",
    },
]


def get_pods_data() -> list[dict]:
    """Get sample pods data."""
    return PODS_DATA.copy()


def get_nodes_data() -> list[dict]:
    """Get sample nodes data."""
    return NODES_DATA.copy()


# Sample namespaces data
NAMESPACES_DATA = [
    {
        "name": "default",
        "status": "Active",
        "created": "2024-01-01T00:00:00Z",
        "pod_count": 12,
        "service_count": 5,
        "project": "default-project",
    },
    {
        "name": "kube-system",
        "status": "Active",
        "created": "2024-01-01T00:00:00Z",
        "pod_count": 8,
        "service_count": 3,
        "project": "system",
    },
    {
        "name": "app-dev",
        "status": "Active",
        "created": "2024-01-05T10:00:00Z",
        "pod_count": 15,
        "service_count": 7,
        "project": "development",
    },
    {
        "name": "production",
        "status": "Active",
        "created": "2024-01-03T08:00:00Z",
        "pod_count": 25,
        "service_count": 12,
        "project": "production",
    },
    {
        "name": "staging",
        "status": "Active",
        "created": "2024-01-04T09:00:00Z",
        "pod_count": 18,
        "service_count": 9,
        "project": "staging",
    },
    {
        "name": "monitoring",
        "status": "Active",
        "created": "2024-01-06T11:00:00Z",
        "pod_count": 6,
        "service_count": 4,
        "project": "monitoring",
    },
]


def get_namespaces_data() -> list[dict]:
    """Get sample namespaces data."""
    return NAMESPACES_DATA.copy()
