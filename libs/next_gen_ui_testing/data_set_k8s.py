# Red Hat OpenShift/K8s Mock Data
# Based on real Kubernetes admin scenarios from PM feedback

from typing import Any, Dict

# OpenShift Cluster Data
openshift_clusters = [
    {
        "cluster": {
            "name": "prod-openshift-us-east",
            "status": "healthy",
            "version": "4.14.8",
            "nodes": 12,
            "api_server_status": "running",
            "etcd_health": "healthy",
            "uptime_days": 45,
            "last_backup": "2024-10-03T02:30:00Z",
            "region": "us-east-1",
            "cpu_usage_percent": 68,
            "memory_usage_percent": 72,
            "storage_usage_percent": 45,
            "cluster_logo_url": "https://connect.redhat.com/sites/default/files/2021-06/OpenShift-LogoType.svg__0.png",
            "monitoring_dashboard_url": "https://console-openshift-console.apps.prod.example.com/monitoring",
            "cluster_overview_video_url": "https://youtu.be/XdlVs37KD1I?si=bKtqtOsPN95IgTGX",
        }
    },
    {
        "cluster": {
            "name": "dev-openshift-us-west",
            "status": "degraded",
            "version": "4.13.12",
            "nodes": 6,
            "api_server_status": "running",
            "etcd_health": "warning",
            "uptime_days": 12,
            "last_backup": "2024-10-02T02:30:00Z",
            "region": "us-west-2",
            "cpu_usage_percent": 45,
            "memory_usage_percent": 89,
            "storage_usage_percent": 78,
            "cluster_logo_url": "https://connect.redhat.com/sites/default/files/2021-06/OpenShift-LogoType.svg__0.png",
            "monitoring_dashboard_url": "https://console-openshift-console.apps.prod.example.com/monitoring",
            "cluster_overview_video_url": "https://youtu.be/XdlVs37KD1I?si=bKtqtOsPN95IgTGX",
        }
    },
]

# Node Status Data
cluster_nodes = [
    {
        "nodes": [
            {
                "name": "worker-01.prod.example.com",
                "status": "Ready",
                "cpu_usage": 65,
                "memory_usage": 78,
                "disk_usage": 42,
                "pod_count": 24,
                "version": "v1.27.6+f67aeb3",
                "uptime_days": 45,
            },
            {
                "name": "worker-02.prod.example.com",
                "status": "Ready",
                "cpu_usage": 71,
                "memory_usage": 68,
                "disk_usage": 38,
                "pod_count": 22,
                "version": "v1.27.6+f67aeb3",
                "uptime_days": 45,
            },
            {
                "name": "worker-03.prod.example.com",
                "status": "NotReady",
                "cpu_usage": 0,
                "memory_usage": 0,
                "disk_usage": 95,
                "pod_count": 0,
                "version": "v1.27.6+f67aeb3",
                "uptime_days": 0,
                "issue": "DiskPressure",
            },
        ]
    }
]

# Resource Usage by Namespace
namespace_resources = [
    {
        "namespaces": [
            {
                "name": "kube-system",
                "cpu_requests": "2.1",
                "cpu_limits": "4.0",
                "cpu_usage": "1.8",
                "memory_requests": "4.2Gi",
                "memory_limits": "8.0Gi",
                "memory_usage": "3.9Gi",
                "pod_count": 18,
                "cost_per_month": 245.50,
            },
            {
                "name": "openshift-monitoring",
                "cpu_requests": "3.5",
                "cpu_limits": "6.0",
                "cpu_usage": "2.9",
                "memory_requests": "8.1Gi",
                "memory_limits": "12.0Gi",
                "memory_usage": "7.8Gi",
                "pod_count": 12,
                "cost_per_month": 412.30,
            },
            {
                "name": "production-app",
                "cpu_requests": "5.2",
                "cpu_limits": "10.0",
                "cpu_usage": "4.1",
                "memory_requests": "12.5Gi",
                "memory_limits": "20.0Gi",
                "memory_usage": "11.2Gi",
                "pod_count": 35,
                "cost_per_month": 678.90,
            },
            {
                "name": "development",
                "cpu_requests": "1.8",
                "cpu_limits": "3.0",
                "cpu_usage": "0.4",
                "memory_requests": "3.2Gi",
                "memory_limits": "6.0Gi",
                "memory_usage": "1.1Gi",
                "pod_count": 8,
                "cost_per_month": 89.20,
                "waste_percentage": 78,
            },
        ]
    }
]

# Pod Issues/Troubleshooting
pod_issues = [
    {
        "failing_pods": [
            {
                "name": "payment-service-7d4b6c8f9-xk2j9",
                "namespace": "production-app",
                "status": "CrashLoopBackOff",
                "restart_count": 15,
                "last_restart": "2024-10-03T09:15:23Z",
                "error_message": "Error: ECONNREFUSED connect to database",
                "node": "worker-01.prod.example.com",
                "image": "registry.redhat.io/payment-service:v2.1.3",
                "cpu_limit": "500m",
                "memory_limit": "1Gi",
            },
            {
                "name": "user-auth-6b8d4f7c2-m9n4p",
                "namespace": "production-app",
                "status": "ImagePullBackOff",
                "restart_count": 0,
                "last_restart": "2024-10-03T08:45:12Z",
                "error_message": "Failed to pull image: registry.redhat.io/user-auth:v1.5.2 not found",
                "node": "worker-02.prod.example.com",
                "image": "registry.redhat.io/user-auth:v1.5.2",
                "cpu_limit": "200m",
                "memory_limit": "512Mi",
            },
        ]
    }
]

# RBAC Security Data
rbac_permissions = [
    {
        "rbac_bindings": [
            {
                "user": "admin@redhat.com",
                "role": "cluster-admin",
                "type": "ClusterRoleBinding",
                "namespace": "*",
                "permissions": ["*"],
                "last_login": "2024-10-03T08:30:00Z",
                "mfa_enabled": True,
            },
            {
                "user": "developer@redhat.com",
                "role": "edit",
                "type": "RoleBinding",
                "namespace": "development",
                "permissions": ["get", "list", "create", "update", "delete"],
                "last_login": "2024-10-03T07:15:00Z",
                "mfa_enabled": True,
            },
            {
                "user": "viewer@redhat.com",
                "role": "view",
                "type": "RoleBinding",
                "namespace": "production-app",
                "permissions": ["get", "list"],
                "last_login": "2024-10-02T16:45:00Z",
                "mfa_enabled": False,
            },
        ]
    }
]

# Storage/PVC Data
storage_volumes = [
    {
        "persistent_volumes": [
            {
                "name": "pvc-database-prod",
                "namespace": "production-app",
                "status": "Bound",
                "size": "100Gi",
                "used": "78Gi",
                "storage_class": "gp3-csi",
                "access_mode": "ReadWriteOnce",
                "mount_path": "/var/lib/postgresql/data",
                "last_backup": "2024-10-03T01:00:00Z",
            },
            {
                "name": "pvc-logs-storage",
                "namespace": "openshift-logging",
                "status": "Bound",
                "size": "500Gi",
                "used": "423Gi",
                "storage_class": "gp3-csi",
                "access_mode": "ReadWriteMany",
                "mount_path": "/var/log/containers",
                "last_backup": "2024-10-03T02:30:00Z",
            },
            {
                "name": "pvc-temp-storage",
                "namespace": "development",
                "status": "Pending",
                "size": "50Gi",
                "used": "0Gi",
                "storage_class": "gp3-csi",
                "access_mode": "ReadWriteOnce",
                "mount_path": "/tmp/data",
                "error": "Insufficient storage capacity",
            },
        ]
    }
]

# Network/Service Data
service_connectivity = [
    {
        "services": [
            {
                "name": "payment-service",
                "namespace": "production-app",
                "type": "ClusterIP",
                "cluster_ip": "10.128.45.23",
                "ports": [{"port": 8080, "target_port": 8080}],
                "endpoints": 3,
                "healthy_endpoints": 2,
                "dns_resolution": "healthy",
                "ingress_url": "https://payments.apps.prod.example.com",
            },
            {
                "name": "user-database",
                "namespace": "production-app",
                "type": "ClusterIP",
                "cluster_ip": "10.128.67.89",
                "ports": [{"port": 5432, "target_port": 5432}],
                "endpoints": 1,
                "healthy_endpoints": 1,
                "dns_resolution": "healthy",
                "ingress_url": None,
            },
            {
                "name": "api-gateway",
                "namespace": "production-app",
                "type": "LoadBalancer",
                "cluster_ip": "10.128.12.45",
                "external_ip": "34.123.45.67",
                "ports": [{"port": 443, "target_port": 8443}],
                "endpoints": 2,
                "healthy_endpoints": 0,
                "dns_resolution": "failed",
                "ingress_url": "https://api.prod.example.com",
                "error": "No healthy endpoints available",
            },
        ]
    }
]

# Cost/Efficiency Data
cost_analysis = [
    {
        "cost_efficiency": [
            {
                "namespace": "production-app",
                "monthly_cost": 1245.67,
                "cpu_waste_percentage": 23,
                "memory_waste_percentage": 31,
                "suggested_savings": 387.45,
                "right_sizing_recommendations": [
                    "Reduce payment-service memory from 2Gi to 1.2Gi",
                    "Reduce user-auth CPU from 1000m to 400m",
                ],
            },
            {
                "namespace": "development",
                "monthly_cost": 456.23,
                "cpu_waste_percentage": 67,
                "memory_waste_percentage": 72,
                "suggested_savings": 312.18,
                "right_sizing_recommendations": [
                    "Use spot instances for dev workloads",
                    "Scale down replicas during off-hours",
                ],
            },
        ]
    }
]

# Disaster Recovery Status
disaster_recovery = [
    {
        "backup_status": {
            "etcd_snapshots": {
                "last_successful": "2024-10-03T02:30:00Z",
                "frequency": "daily",
                "retention_days": 30,
                "storage_location": "s3://openshift-backups-prod",
                "size_gb": 2.3,
                "status": "healthy",
            },
            "velero_backups": {
                "last_successful": "2024-10-03T01:00:00Z",
                "frequency": "daily",
                "retention_days": 90,
                "storage_location": "s3://velero-backups-prod",
                "applications_backed_up": 12,
                "status": "healthy",
            },
            "recovery_time_objective": "4 hours",
            "recovery_point_objective": "1 hour",
            "last_recovery_test": "2024-09-15T10:00:00Z",
            "test_result": "successful",
        }
    }
]


def find_cluster(cluster_name: str = "") -> Dict[str, Any]:
    """Find OpenShift cluster information"""
    if cluster_name:
        for cluster_data in openshift_clusters:
            if cluster_name.lower() in cluster_data["cluster"]["name"].lower():  # type: ignore
                return cluster_data
    return openshift_clusters[0]  # Default to first cluster


def find_cluster_nodes(cluster_name: str = "") -> Dict[str, Any]:
    """Find cluster node status information"""
    return cluster_nodes[0]


def find_namespace_resources(namespace: str = "") -> Dict[str, Any]:
    """Find resource usage by namespace"""
    return namespace_resources[0]


def find_pod_issues(namespace: str = "") -> Dict[str, Any]:
    """Find failing pods and issues"""
    return pod_issues[0]


def find_rbac_permissions(user_email: str = "") -> Dict[str, Any]:
    """Find RBAC permissions and security info"""
    return rbac_permissions[0]


def find_storage_volumes(namespace: str = "") -> Dict[str, Any]:
    """Find persistent volume and storage information"""
    return storage_volumes[0]


def find_service_connectivity(service_name: str = "") -> Dict[str, Any]:
    """Find service and networking information"""
    return service_connectivity[0]


def find_cost_analysis(namespace: str = "") -> Dict[str, Any]:
    """Find cost and efficiency analysis"""
    return cost_analysis[0]


def find_disaster_recovery() -> Dict[str, Any]:
    """Find backup and disaster recovery status"""
    return disaster_recovery[0]


# Legacy Red Hat data (keep for backward compatibility)
rhel_subscriptions = [
    {
        "subscription": {
            "subscriptionNumber": "12345678",
            "productName": "Red Hat Enterprise Linux Server",
            "endDate": "2025-12-31T23:59:59Z",
            "productLogoUrl": "https://upload.wikimedia.org/wikipedia/commons/d/d8/Red_Hat_logo.svg",
            "productOverviewVideoUrl": "https://youtu.be/XdlVs37KD1I?si=bKtqtOsPN95IgTGX",
        }
    }
]


def find_subscription(subscription_number: str = "") -> Dict[str, Any]:
    """Find RHEL subscription information"""
    return rhel_subscriptions[0]
