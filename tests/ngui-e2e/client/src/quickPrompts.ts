// Quick prompt suggestions for testing different component types through the LLM
// Dataset prompts automatically attach their backend data when clicked
// This file is auto-generated from tests/ai_eval_components/dataset/ and dataset_k8s/
// To regenerate, run: pants run tests/ai_eval_components/sync_datasets_to_e2e.py

export type QuickPromptCategory = 'one-card' | 'set-of-cards' | 'tables' | 'charts' | 'image' | 'video-player' | 'mixed';
export type QuickPromptSource = 'general' | 'k8s';

export interface QuickPromptDataset {
  datasetId: string;
  dataType: string | null;
}

export interface QuickPrompt {
  id: string;
  category: QuickPromptCategory;
  prompt: string;
  expectedComponent: string;
  source: QuickPromptSource;
  dataset?: QuickPromptDataset;
}

export const quickPrompts: QuickPrompt[] = [
  // Charts
  {
    id: "chart_000001",
    category: "charts",
    prompt: "Show CPU usage comparison chart",
    expectedComponent: "chart-bar",
    source: "k8s",
    dataset: {
      datasetId: "chart-bar_pod_metrics",
      dataType: "chart-bar.dataset",
    }
  },
  {
    id: "chart_000002",
    category: "charts",
    prompt: "Display pod CPU as a bar chart",
    expectedComponent: "chart-bar",
    source: "k8s",
    dataset: {
      datasetId: "chart-bar_pod_metrics",
      dataType: "chart-bar.dataset",
    }
  },
  {
    id: "chart_000003",
    category: "charts",
    prompt: "Compare CPU across pods in a chart",
    expectedComponent: "chart-bar",
    source: "k8s",
    dataset: {
      datasetId: "chart-bar_pod_metrics",
      dataType: "chart-bar.dataset",
    }
  },
  {
    id: "chart_000004",
    category: "charts",
    prompt: "Show me a bar chart of pod memory usage",
    expectedComponent: "chart-bar",
    source: "k8s",
    dataset: {
      datasetId: "chart-bar_pod_metrics",
      dataType: "chart-bar.dataset",
    }
  },
  {
    id: "chart_000005",
    category: "charts",
    prompt: "Chart the resource usage by pod",
    expectedComponent: "chart-bar",
    source: "k8s",
    dataset: {
      datasetId: "chart-bar_pod_metrics",
      dataType: "chart-bar.dataset",
    }
  },
  {
    id: "chart_000006",
    category: "charts",
    prompt: "Show CPU and memory comparison chart",
    expectedComponent: "chart-mirrored-bar",
    source: "k8s",
    dataset: {
      datasetId: "chart-mirrored-bar_pod_metrics",
      dataType: "chart-mirrored-bar.dataset",
    }
  },
  {
    id: "chart_000007",
    category: "charts",
    prompt: "Compare CPU vs memory in a bar chart",
    expectedComponent: "chart-mirrored-bar",
    source: "k8s",
    dataset: {
      datasetId: "chart-mirrored-bar_pod_metrics",
      dataType: "chart-mirrored-bar.dataset",
    }
  },
  {
    id: "chart_000008",
    category: "charts",
    prompt: "Display dual metric comparison for pods",
    expectedComponent: "chart-mirrored-bar",
    source: "k8s",
    dataset: {
      datasetId: "chart-mirrored-bar_pod_metrics",
      dataType: "chart-mirrored-bar.dataset",
    }
  },
  {
    id: "chart_000009",
    category: "charts",
    prompt: "Show side-by-side CPU and memory chart",
    expectedComponent: "chart-mirrored-bar",
    source: "k8s",
    dataset: {
      datasetId: "chart-mirrored-bar_pod_metrics",
      dataType: "chart-mirrored-bar.dataset",
    }
  },
  {
    id: "chart_000010",
    category: "charts",
    prompt: "Show pod status distribution as a pie chart",
    expectedComponent: "chart-pie",
    source: "k8s",
    dataset: {
      datasetId: "chart-pie_pod_status_distribution",
      dataType: "chart-pie.dataset",
    }
  },
  {
    id: "chart_000011",
    category: "charts",
    prompt: "Display pod status as a pie chart",
    expectedComponent: "chart-pie",
    source: "k8s",
    dataset: {
      datasetId: "chart-pie_pod_status_distribution",
      dataType: "chart-pie.dataset",
    }
  },
  {
    id: "chart_000012",
    category: "charts",
    prompt: "Show pod breakdown in a pie chart",
    expectedComponent: "chart-pie",
    source: "k8s",
    dataset: {
      datasetId: "chart-pie_pod_status_distribution",
      dataType: "chart-pie.dataset",
    }
  },
  {
    id: "chart_000013",
    category: "charts",
    prompt: "What percentage of pods are running?",
    expectedComponent: "chart-pie",
    source: "k8s",
    dataset: {
      datasetId: "chart-pie_pod_status_distribution",
      dataType: "chart-pie.dataset",
    }
  },
  {
    id: "chart_000014",
    category: "charts",
    prompt: "Show pod status as a pie chart",
    expectedComponent: "chart-pie",
    source: "k8s",
    dataset: {
      datasetId: "chart-pie_pod_status_distribution",
      dataType: "chart-pie.dataset",
    }
  },
  {
    id: "chart_000015",
    category: "charts",
    prompt: "Show pod age distribution as a pie chart",
    expectedComponent: "chart-pie",
    source: "k8s",
    dataset: {
      datasetId: "chart-pie_pod_age_distribution",
      dataType: "chart-pie.dataset",
    }
  },
  {
    id: "chart_000016",
    category: "charts",
    prompt: "Display pod age breakdown as a pie chart",
    expectedComponent: "chart-pie",
    source: "k8s",
    dataset: {
      datasetId: "chart-pie_pod_age_distribution",
      dataType: "chart-pie.dataset",
    }
  },
  {
    id: "chart_000017",
    category: "charts",
    prompt: "What's the age distribution of pods? Show as chart",
    expectedComponent: "chart-pie",
    source: "k8s",
    dataset: {
      datasetId: "chart-pie_pod_age_distribution",
      dataType: "chart-pie.dataset",
    }
  },
  {
    id: "chart_000018",
    category: "charts",
    prompt: "Show pod age as a pie chart",
    expectedComponent: "chart-pie",
    source: "k8s",
    dataset: {
      datasetId: "chart-pie_pod_age_distribution",
      dataType: "chart-pie.dataset",
    }
  },
  {
    id: "chart_000019",
    category: "charts",
    prompt: "Compare CPU used vs capacity across nodes in a chart",
    expectedComponent: "chart-mirrored-bar",
    source: "k8s",
    dataset: {
      datasetId: "chart-mirrored-bar_node_capacity",
      dataType: "chart-mirrored-bar.dataset",
    }
  },
  {
    id: "chart_000020",
    category: "charts",
    prompt: "Show node resource utilization as a comparison chart",
    expectedComponent: "chart-mirrored-bar",
    source: "k8s",
    dataset: {
      datasetId: "chart-mirrored-bar_node_capacity",
      dataType: "chart-mirrored-bar.dataset",
    }
  },
  {
    id: "chart_000021",
    category: "charts",
    prompt: "Compare memory usage and capacity chart for all nodes",
    expectedComponent: "chart-mirrored-bar",
    source: "k8s",
    dataset: {
      datasetId: "chart-mirrored-bar_node_capacity",
      dataType: "chart-mirrored-bar.dataset",
    }
  },
  {
    id: "chart_000022",
    category: "charts",
    prompt: "Display node CPU and memory side-by-side chart",
    expectedComponent: "chart-mirrored-bar",
    source: "k8s",
    dataset: {
      datasetId: "chart-mirrored-bar_node_capacity",
      dataType: "chart-mirrored-bar.dataset",
    }
  },
  {
    id: "chart_000023",
    category: "charts",
    prompt: "Show pod phase distribution from Prometheus",
    expectedComponent: "chart-line",
    source: "k8s",
    dataset: {
      datasetId: "chart-line_prometheus_node_cpu_timeseries",
      dataType: "chart-line.dataset",
    }
  },
  {
    id: "chart_000024",
    category: "charts",
    prompt: "Display pod status breakdown as a chart",
    expectedComponent: "chart-line",
    source: "k8s",
    dataset: {
      datasetId: "chart-line_prometheus_node_cpu_timeseries",
      dataType: "chart-line.dataset",
    }
  },
  {
    id: "chart_000025",
    category: "charts",
    prompt: "What's the pod status distribution?",
    expectedComponent: "chart-line",
    source: "k8s",
    dataset: {
      datasetId: "chart-line_prometheus_node_cpu_timeseries",
      dataType: "chart-line.dataset",
    }
  },
  {
    id: "chart_000026",
    category: "charts",
    prompt: "Show pod phases as a pie chart",
    expectedComponent: "chart-line",
    source: "k8s",
    dataset: {
      datasetId: "chart-line_prometheus_node_cpu_timeseries",
      dataType: "chart-line.dataset",
    }
  },
  {
    id: "chart_000027",
    category: "charts",
    prompt: "Compare available memory across nodes as a chart",
    expectedComponent: "chart-bar",
    source: "k8s",
    dataset: {
      datasetId: "chart-bar_prometheus_memory_usage",
      dataType: "chart-bar.dataset",
    }
  },
  {
    id: "chart_000028",
    category: "charts",
    prompt: "Show node memory availability bar chart",
    expectedComponent: "chart-bar",
    source: "k8s",
    dataset: {
      datasetId: "chart-bar_prometheus_memory_usage",
      dataType: "chart-bar.dataset",
    }
  },
  {
    id: "chart_000029",
    category: "charts",
    prompt: "Which nodes have the most available memory? Chart it",
    expectedComponent: "chart-bar",
    source: "k8s",
    dataset: {
      datasetId: "chart-bar_prometheus_memory_usage",
      dataType: "chart-bar.dataset",
    }
  },
  {
    id: "chart_000030",
    category: "charts",
    prompt: "Display memory metrics by node in a bar chart",
    expectedComponent: "chart-bar",
    source: "k8s",
    dataset: {
      datasetId: "chart-bar_prometheus_memory_usage",
      dataType: "chart-bar.dataset",
    }
  },
  {
    id: "chart_000031",
    category: "charts",
    prompt: "Show container restart counts as a bar chart",
    expectedComponent: "chart-bar",
    source: "k8s",
    dataset: {
      datasetId: "chart-bar_prometheus_container_restarts",
      dataType: "chart-bar.dataset",
    }
  },
  {
    id: "chart_000032",
    category: "charts",
    prompt: "Which containers have restarted the most? Show chart",
    expectedComponent: "chart-bar",
    source: "k8s",
    dataset: {
      datasetId: "chart-bar_prometheus_container_restarts",
      dataType: "chart-bar.dataset",
    }
  },
  {
    id: "chart_000033",
    category: "charts",
    prompt: "Display restart statistics for containers in a chart",
    expectedComponent: "chart-bar",
    source: "k8s",
    dataset: {
      datasetId: "chart-bar_prometheus_container_restarts",
      dataType: "chart-bar.dataset",
    }
  },
  {
    id: "chart_000034",
    category: "charts",
    prompt: "Compare container restarts in a bar chart",
    expectedComponent: "chart-bar",
    source: "k8s",
    dataset: {
      datasetId: "chart-bar_prometheus_container_restarts",
      dataType: "chart-bar.dataset",
    }
  },
  {
    id: "chart_000035",
    category: "charts",
    prompt: "Show pod phase distribution from Prometheus as a pie chart",
    expectedComponent: "chart-pie",
    source: "k8s",
    dataset: {
      datasetId: "chart-pie_prometheus_pod_status_count",
      dataType: "chart-pie.dataset",
    }
  },
  {
    id: "chart_000036",
    category: "charts",
    prompt: "Display pod status distribution as a pie chart",
    expectedComponent: "chart-pie",
    source: "k8s",
    dataset: {
      datasetId: "chart-pie_prometheus_pod_status_count",
      dataType: "chart-pie.dataset",
    }
  },
  {
    id: "chart_000037",
    category: "charts",
    prompt: "What's the pod status distribution?",
    expectedComponent: "chart-pie",
    source: "k8s",
    dataset: {
      datasetId: "chart-pie_prometheus_pod_status_count",
      dataType: "chart-pie.dataset",
    }
  },
  {
    id: "chart_000038",
    category: "charts",
    prompt: "Show pod phases as a pie chart",
    expectedComponent: "chart-pie",
    source: "k8s",
    dataset: {
      datasetId: "chart-pie_prometheus_pod_status_count",
      dataType: "chart-pie.dataset",
    }
  },
  {
    id: "chart_000039",
    category: "charts",
    prompt: "Count pods by status",
    expectedComponent: "chart-pie",
    source: "k8s",
    dataset: {
      datasetId: "chart-pie_pods_status_frequency",
      dataType: "chart-pie.dataset",
    }
  },
  {
    id: "chart_000040",
    category: "charts",
    prompt: "How many pods are in each status?",
    expectedComponent: "chart-pie",
    source: "k8s",
    dataset: {
      datasetId: "chart-pie_pods_status_frequency",
      dataType: "chart-pie.dataset",
    }
  },
  {
    id: "chart_000041",
    category: "charts",
    prompt: "Show pod status count as pie chart",
    expectedComponent: "chart-pie",
    source: "k8s",
    dataset: {
      datasetId: "chart-pie_pods_status_frequency",
      dataType: "chart-pie.dataset",
    }
  },
  {
    id: "chart_000042",
    category: "charts",
    prompt: "Count and display pod statuses",
    expectedComponent: "chart-pie",
    source: "k8s",
    dataset: {
      datasetId: "chart-pie_pods_status_frequency",
      dataType: "chart-pie.dataset",
    }
  },
  {
    id: "chart_000043",
    category: "charts",
    prompt: "What's the distribution of pod statuses?",
    expectedComponent: "chart-pie",
    source: "k8s",
    dataset: {
      datasetId: "chart-pie_pods_status_frequency",
      dataType: "chart-pie.dataset",
    }
  },
  {
    id: "chart_000044",
    category: "charts",
    prompt: "Show label distribution as donut chart",
    expectedComponent: "chart-donut",
    source: "k8s",
    dataset: {
      datasetId: "chart-donut_pods_labels_frequency",
      dataType: "chart-donut.dataset",
    }
  },
  {
    id: "chart_000045",
    category: "charts",
    prompt: "Count pod labels across all pods",
    expectedComponent: "chart-donut",
    source: "k8s",
    dataset: {
      datasetId: "chart-donut_pods_labels_frequency",
      dataType: "chart-donut.dataset",
    }
  },
  {
    id: "chart_000046",
    category: "charts",
    prompt: "What labels are most common?",
    expectedComponent: "chart-donut",
    source: "k8s",
    dataset: {
      datasetId: "chart-donut_pods_labels_frequency",
      dataType: "chart-donut.dataset",
    }
  },
  {
    id: "chart_000047",
    category: "charts",
    prompt: "Display label frequency as donut",
    expectedComponent: "chart-donut",
    source: "k8s",
    dataset: {
      datasetId: "chart-donut_pods_labels_frequency",
      dataType: "chart-donut.dataset",
    }
  },
  {
    id: "chart_000048",
    category: "charts",
    prompt: "Show label breakdown counting occurrences",
    expectedComponent: "chart-donut",
    source: "k8s",
    dataset: {
      datasetId: "chart-donut_pods_labels_frequency",
      dataType: "chart-donut.dataset",
    }
  },
  {
    id: "chart_000049",
    category: "charts",
    prompt: "Show pod status as a donut chart",
    expectedComponent: "chart-donut",
    source: "k8s",
    dataset: {
      datasetId: "chart-donut_pod_status_distribution",
      dataType: "chart-donut.dataset",
    }
  },
  {
    id: "chart_000050",
    category: "charts",
    prompt: "Display pod distribution as donut",
    expectedComponent: "chart-donut",
    source: "k8s",
    dataset: {
      datasetId: "chart-donut_pod_status_distribution",
      dataType: "chart-donut.dataset",
    }
  },
  {
    id: "chart_000051",
    category: "charts",
    prompt: "Create donut chart of pod statuses",
    expectedComponent: "chart-donut",
    source: "k8s",
    dataset: {
      datasetId: "chart-donut_pod_status_distribution",
      dataType: "chart-donut.dataset",
    }
  },
  {
    id: "chart_000052",
    category: "charts",
    prompt: "Show pod status breakdown in a donut chart",
    expectedComponent: "chart-donut",
    source: "k8s",
    dataset: {
      datasetId: "chart-donut_pod_status_distribution",
      dataType: "chart-donut.dataset",
    }
  },
  {
    id: "chart_000053",
    category: "charts",
    prompt: "Visualize pod status as donut with center metric",
    expectedComponent: "chart-donut",
    source: "k8s",
    dataset: {
      datasetId: "chart-donut_pod_status_distribution",
      dataType: "chart-donut.dataset",
    }
  },
  {
    id: "chart_000054",
    category: "charts",
    prompt: "Show pod age distribution as donut chart",
    expectedComponent: "chart-donut",
    source: "k8s",
    dataset: {
      datasetId: "chart-donut_pod_age_distribution",
      dataType: "chart-donut.dataset",
    }
  },
  {
    id: "chart_000055",
    category: "charts",
    prompt: "Display pod age ranges in a donut chart",
    expectedComponent: "chart-donut",
    source: "k8s",
    dataset: {
      datasetId: "chart-donut_pod_age_distribution",
      dataType: "chart-donut.dataset",
    }
  },
  {
    id: "chart_000056",
    category: "charts",
    prompt: "Create donut chart showing pod ages",
    expectedComponent: "chart-donut",
    source: "k8s",
    dataset: {
      datasetId: "chart-donut_pod_age_distribution",
      dataType: "chart-donut.dataset",
    }
  },
  {
    id: "chart_000057",
    category: "charts",
    prompt: "Visualize pod age breakdown as donut with center",
    expectedComponent: "chart-donut",
    source: "k8s",
    dataset: {
      datasetId: "chart-donut_pod_age_distribution",
      dataType: "chart-donut.dataset",
    }
  },
  {
    id: "chart_000058",
    category: "charts",
    prompt: "Show CPU history for each pod",
    expectedComponent: "chart-line",
    source: "k8s",
    dataset: {
      datasetId: "chart-line_pods_cpu_history_nested",
      dataType: "chart-line.dataset",
    }
  },
  {
    id: "chart_000059",
    category: "charts",
    prompt: "Display CPU trends per pod over time",
    expectedComponent: "chart-line",
    source: "k8s",
    dataset: {
      datasetId: "chart-line_pods_cpu_history_nested",
      dataType: "chart-line.dataset",
    }
  },
  {
    id: "chart_000060",
    category: "charts",
    prompt: "Chart historical CPU usage for all pods",
    expectedComponent: "chart-line",
    source: "k8s",
    dataset: {
      datasetId: "chart-line_pods_cpu_history_nested",
      dataType: "chart-line.dataset",
    }
  },
  {
    id: "chart_000061",
    category: "charts",
    prompt: "Compare pod CPU trends",
    expectedComponent: "chart-line",
    source: "k8s",
    dataset: {
      datasetId: "chart-line_pods_cpu_history_nested",
      dataType: "chart-line.dataset",
    }
  },
  {
    id: "chart_000062",
    category: "charts",
    prompt: "Show CPU over time for multiple pods",
    expectedComponent: "chart-line",
    source: "k8s",
    dataset: {
      datasetId: "chart-line_pods_cpu_history_nested",
      dataType: "chart-line.dataset",
    }
  },
  {
    id: "chart_000063",
    category: "charts",
    prompt: "Count pods per namespace",
    expectedComponent: "chart-pie",
    source: "k8s",
    dataset: {
      datasetId: "chart-pie_pods_namespace_frequency",
      dataType: "chart-pie.dataset",
    }
  },
  {
    id: "chart_000064",
    category: "charts",
    prompt: "How many pods in each namespace?",
    expectedComponent: "chart-pie",
    source: "k8s",
    dataset: {
      datasetId: "chart-pie_pods_namespace_frequency",
      dataType: "chart-pie.dataset",
    }
  },
  {
    id: "chart_000065",
    category: "charts",
    prompt: "Show namespace distribution",
    expectedComponent: "chart-pie",
    source: "k8s",
    dataset: {
      datasetId: "chart-pie_pods_namespace_frequency",
      dataType: "chart-pie.dataset",
    }
  },
  {
    id: "chart_000066",
    category: "charts",
    prompt: "Display pod count by namespace as pie chart",
    expectedComponent: "chart-pie",
    source: "k8s",
    dataset: {
      datasetId: "chart-pie_pods_namespace_frequency",
      dataType: "chart-pie.dataset",
    }
  },
  {
    id: "chart_000067",
    category: "charts",
    prompt: "Which namespaces have the most pods?",
    expectedComponent: "chart-pie",
    source: "k8s",
    dataset: {
      datasetId: "chart-pie_pods_namespace_frequency",
      dataType: "chart-pie.dataset",
    }
  },
  {
    id: "chart_000068",
    category: "charts",
    prompt: "Compare all node metrics",
    expectedComponent: "chart-bar",
    source: "k8s",
    dataset: {
      datasetId: "chart-bar_node_multi_metrics",
      dataType: "chart-bar.dataset",
    }
  },
  {
    id: "chart_000069",
    category: "charts",
    prompt: "Show CPU, memory, disk and network for nodes",
    expectedComponent: "chart-bar",
    source: "k8s",
    dataset: {
      datasetId: "chart-bar_node_multi_metrics",
      dataType: "chart-bar.dataset",
    }
  },
  {
    id: "chart_000070",
    category: "charts",
    prompt: "Display comprehensive node metrics",
    expectedComponent: "chart-bar",
    source: "k8s",
    dataset: {
      datasetId: "chart-bar_node_multi_metrics",
      dataType: "chart-bar.dataset",
    }
  },
  {
    id: "chart_000071",
    category: "charts",
    prompt: "Chart all resource metrics across nodes",
    expectedComponent: "chart-bar",
    source: "k8s",
    dataset: {
      datasetId: "chart-bar_node_multi_metrics",
      dataType: "chart-bar.dataset",
    }
  },
  {
    id: "chart_000072",
    category: "charts",
    prompt: "Compare multiple metrics for each node",
    expectedComponent: "chart-bar",
    source: "k8s",
    dataset: {
      datasetId: "chart-bar_node_multi_metrics",
      dataType: "chart-bar.dataset",
    }
  },
  // Image
  {
    id: "image_000001",
    category: "image",
    prompt: "Show me Toy Story poster",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsNames_camelCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000002",
    category: "image",
    prompt: "Show me the poster",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsNames_camelCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000003",
    category: "image",
    prompt: "Show me poster of the movie",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsNames_camelCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000004",
    category: "image",
    prompt: "Show me movie image",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsNames_camelCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000005",
    category: "image",
    prompt: "Show me the movie image",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsNames_camelCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000006",
    category: "image",
    prompt: "What about poster?",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsNames_camelCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000007",
    category: "image",
    prompt: "Do you like the movie poster?",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsNames_camelCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000008",
    category: "image",
    prompt: "What is the movie poster about?",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsNames_camelCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000009",
    category: "image",
    prompt: "Show me Toy Story poster",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsNames_snakeCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000010",
    category: "image",
    prompt: "Show me the poster",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsNames_snakeCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000011",
    category: "image",
    prompt: "Show me poster of the movie",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsNames_snakeCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000012",
    category: "image",
    prompt: "Show me movie image",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsNames_snakeCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000013",
    category: "image",
    prompt: "Show me the movie image",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsNames_snakeCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000014",
    category: "image",
    prompt: "What about poster?",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsNames_snakeCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000015",
    category: "image",
    prompt: "Do you like the movie poster?",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsNames_snakeCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000016",
    category: "image",
    prompt: "What is the movie poster about?",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsNames_snakeCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000017",
    category: "image",
    prompt: "Show me Toy Story poster",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsObjects_camelCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000018",
    category: "image",
    prompt: "Show me the poster",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsObjects_camelCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000019",
    category: "image",
    prompt: "Show me poster of the movie",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsObjects_camelCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000020",
    category: "image",
    prompt: "Show me movie image",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsObjects_camelCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000021",
    category: "image",
    prompt: "Show me the movie image",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsObjects_camelCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000022",
    category: "image",
    prompt: "What about poster?",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsObjects_camelCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000023",
    category: "image",
    prompt: "Do you like the movie poster?",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsObjects_camelCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000024",
    category: "image",
    prompt: "What is the movie poster about?",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsObjects_camelCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000025",
    category: "image",
    prompt: "Show me Toy Story poster",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsObjects_snakeCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000026",
    category: "image",
    prompt: "Show me the poster",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsObjects_snakeCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000027",
    category: "image",
    prompt: "Show me poster of the movie",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsObjects_snakeCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000028",
    category: "image",
    prompt: "Show me movie image",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsObjects_snakeCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000029",
    category: "image",
    prompt: "Show me the movie image",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsObjects_snakeCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000030",
    category: "image",
    prompt: "What about poster?",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsObjects_snakeCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000031",
    category: "image",
    prompt: "Do you like the movie poster?",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsObjects_snakeCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000032",
    category: "image",
    prompt: "What is the movie poster about?",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsObjects_snakeCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000033",
    category: "image",
    prompt: "Show me Toy Story poster",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsNames_imdbNested_camelCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000034",
    category: "image",
    prompt: "Show me the poster",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsNames_imdbNested_camelCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000035",
    category: "image",
    prompt: "Show me poster of the movie",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsNames_imdbNested_camelCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000036",
    category: "image",
    prompt: "Show me movie image",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsNames_imdbNested_camelCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000037",
    category: "image",
    prompt: "Show me the movie image",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsNames_imdbNested_camelCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000038",
    category: "image",
    prompt: "What about poster?",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsNames_imdbNested_camelCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000039",
    category: "image",
    prompt: "Do you like the movie poster?",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsNames_imdbNested_camelCase",
      dataType: "image.dataset",
    }
  },
  {
    id: "image_000040",
    category: "image",
    prompt: "What is the movie poster about?",
    expectedComponent: "image",
    source: "general",
    dataset: {
      datasetId: "image_simple_movie_actorsNames_imdbNested_camelCase",
      dataType: "image.dataset",
    }
  },
  // One Card
  {
    id: "one_card_000001",
    category: "one-card",
    prompt: "When does my RHEL subscription end?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_inobject",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000001",
    category: "one-card",
    prompt: "Tell me about prod-openshift-us-east cluster",
    expectedComponent: "one-card",
    source: "k8s",
    dataset: {
      datasetId: "one-card_cluster_info",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000002",
    category: "one-card",
    prompt: "When do I have to renew my RHEL subscription?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_inobject",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000002",
    category: "one-card",
    prompt: "Show me backup status",
    expectedComponent: "one-card",
    source: "k8s",
    dataset: {
      datasetId: "one-card_backup_status",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000003",
    category: "one-card",
    prompt: "How many runtimes is included in my RHEL subscription?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_inobject",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000003",
    category: "one-card",
    prompt: "When was the last etcd snapshot?",
    expectedComponent: "one-card",
    source: "k8s",
    dataset: {
      datasetId: "one-card_backup_status",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000004",
    category: "one-card",
    prompt: "Where can I find details about my RHEL subscription?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_inobject",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000004",
    category: "one-card",
    prompt: "Show me disaster recovery status",
    expectedComponent: "one-card",
    source: "k8s",
    dataset: {
      datasetId: "one-card_backup_status",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000005",
    category: "one-card",
    prompt: "Where can I edit my RHEL subscription?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_inobject",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000005",
    category: "one-card",
    prompt: "Are backups healthy?",
    expectedComponent: "one-card",
    source: "k8s",
    dataset: {
      datasetId: "one-card_backup_status",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000006",
    category: "one-card",
    prompt: "When does my RHEL subscription end?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_inobject_inarray",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000007",
    category: "one-card",
    prompt: "When do I have to renew my RHEL subscription?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_inobject_inarray",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000008",
    category: "one-card",
    prompt: "How many runtimes is included in my RHEL subscription?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_inobject_inarray",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000009",
    category: "one-card",
    prompt: "Where can I find details about my RHEL subscription?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_inobject_inarray",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000010",
    category: "one-card",
    prompt: "Where can I edit my RHEL subscription?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_inobject_inarray",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000011",
    category: "one-card",
    prompt: "When does my RHEL subscription end?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_direct",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000012",
    category: "one-card",
    prompt: "When do I have to renew my RHEL subscription?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_direct",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000013",
    category: "one-card",
    prompt: "How many runtimes is included in my RHEL subscription?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_direct",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000014",
    category: "one-card",
    prompt: "Where can I find details about my RHEL subscription?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_direct",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000015",
    category: "one-card",
    prompt: "Where can I edit my RHEL subscription?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_direct",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000016",
    category: "one-card",
    prompt: "When does my RHEL subscription end?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_direct",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000017",
    category: "one-card",
    prompt: "When do I have to renew my RHEL subscription?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_direct",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000018",
    category: "one-card",
    prompt: "How many runtimes is included in my RHEL subscription?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_direct",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000019",
    category: "one-card",
    prompt: "Where can I find details about my RHEL subscription?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_direct",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000020",
    category: "one-card",
    prompt: "Where can I edit my RHEL subscription?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_direct",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000021",
    category: "one-card",
    prompt: "When does my RHEL subscription end?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_direct_inarray",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000022",
    category: "one-card",
    prompt: "When do I have to renew my RHEL subscription?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_direct_inarray",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000023",
    category: "one-card",
    prompt: "How many runtimes is included in my RHEL subscription?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_direct_inarray",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000024",
    category: "one-card",
    prompt: "Where can I find details about my RHEL subscription?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_direct_inarray",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000025",
    category: "one-card",
    prompt: "Where can I edit my RHEL subscription?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_direct_inarray",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000026",
    category: "one-card",
    prompt: "When does my RHEL subscription end?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_inobject_inarray",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000027",
    category: "one-card",
    prompt: "When do I have to renew my RHEL subscription?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_inobject_inarray",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000028",
    category: "one-card",
    prompt: "How many runtimes is included in my RHEL subscription?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_inobject_inarray",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000029",
    category: "one-card",
    prompt: "Where can I find details about my RHEL subscription?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_inobject_inarray",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000030",
    category: "one-card",
    prompt: "Where can I edit my RHEL subscription?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_inobject_inarray",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000031",
    category: "one-card",
    prompt: "When does my RHEL subscription end?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_direct_inarray",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000032",
    category: "one-card",
    prompt: "When do I have to renew my RHEL subscription?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_direct_inarray",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000033",
    category: "one-card",
    prompt: "How many runtimes is included in my RHEL subscription?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_direct_inarray",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000034",
    category: "one-card",
    prompt: "Where can I find details about my RHEL subscription?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_direct_inarray",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000035",
    category: "one-card",
    prompt: "Where can I edit my RHEL subscription?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_subscription_direct_inarray",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000036",
    category: "one-card",
    prompt: "Show me info about the Toy Story movie.",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsNames_camelCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000037",
    category: "one-card",
    prompt: "What is Toy Story about?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsNames_camelCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000038",
    category: "one-card",
    prompt: "What about Toy Story?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsNames_camelCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000039",
    category: "one-card",
    prompt: "What is Toy Story IMDB rating?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsNames_camelCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000040",
    category: "one-card",
    prompt: "Show me info about the Toy Story movie.",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsNames_snakeCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000041",
    category: "one-card",
    prompt: "What is Toy Story about?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsNames_snakeCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000042",
    category: "one-card",
    prompt: "What about Toy Story?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsNames_snakeCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000043",
    category: "one-card",
    prompt: "What is Toy Story IMDB rating?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsNames_snakeCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000044",
    category: "one-card",
    prompt: "Show me info about the Toy Story movie.",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsObjects_camelCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000045",
    category: "one-card",
    prompt: "What is Toy Story about?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsObjects_camelCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000046",
    category: "one-card",
    prompt: "What about Toy Story?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsObjects_camelCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000047",
    category: "one-card",
    prompt: "What is Toy Story IMDB rating?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsObjects_camelCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000048",
    category: "one-card",
    prompt: "Show me info about the Toy Story movie.",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsObjects_snakeCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000049",
    category: "one-card",
    prompt: "What is Toy Story about?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsObjects_snakeCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000050",
    category: "one-card",
    prompt: "What about Toy Story?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsObjects_snakeCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000051",
    category: "one-card",
    prompt: "What is Toy Story IMDB rating?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsObjects_snakeCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000052",
    category: "one-card",
    prompt: "Show me info about the Toy Story movie.",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsNames_imdbNested_camelCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000053",
    category: "one-card",
    prompt: "What is Toy Story about?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsNames_imdbNested_camelCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000054",
    category: "one-card",
    prompt: "What about Toy Story?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsNames_imdbNested_camelCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000055",
    category: "one-card",
    prompt: "What is Toy Story IMDB rating?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsNames_imdbNested_camelCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000056",
    category: "one-card",
    prompt: "Who acted in the Toy Story?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsNames_camelCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000057",
    category: "one-card",
    prompt: "Who acted in the movie?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsNames_camelCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000058",
    category: "one-card",
    prompt: "What is the movie about and who acted in it?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsNames_camelCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000059",
    category: "one-card",
    prompt: "What is Toy Story movie about and who acted in it?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsNames_camelCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000060",
    category: "one-card",
    prompt: "Who acted in the Toy Story?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsNames_snakeCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000061",
    category: "one-card",
    prompt: "Who acted in the movie?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsNames_snakeCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000062",
    category: "one-card",
    prompt: "What is the movie about and who acted in it?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsNames_snakeCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000063",
    category: "one-card",
    prompt: "What is Toy Story movie about and who acted in it?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsNames_snakeCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000064",
    category: "one-card",
    prompt: "Who acted in the Toy Story?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsNames_imdbNested_camelCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000065",
    category: "one-card",
    prompt: "Who acted in the movie?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsNames_imdbNested_camelCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000066",
    category: "one-card",
    prompt: "What is the movie about and who acted in it?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsNames_imdbNested_camelCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000067",
    category: "one-card",
    prompt: "What is Toy Story movie about and who acted in it?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_simple_movie_actorsNames_imdbNested_camelCase",
      dataType: "one-card.dataset",
    }
  },
  {
    id: "one_card_000068",
    category: "one-card",
    prompt: "My latest order?",
    expectedComponent: "one-card",
    source: "general",
    dataset: {
      datasetId: "one-card_item1",
      dataType: "one-card.dataset",
    }
  },
  // Set Of Cards
  {
    id: "set_of_cards_000001",
    category: "set-of-cards",
    prompt: "What are my subscriptions?",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_array_subscription_inobject_short",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000001",
    category: "set-of-cards",
    prompt: "Show me OpenShift cluster status",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_cluster_info",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000002",
    category: "set-of-cards",
    prompt: "List my subscriptions.",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_array_subscription_inobject_short",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000002",
    category: "set-of-cards",
    prompt: "Which cluster is degraded?",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_cluster_info",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000003",
    category: "set-of-cards",
    prompt: "Show me my subscriptions.",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_array_subscription_inobject_short",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000003",
    category: "set-of-cards",
    prompt: "Show me all worker nodes",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_nodes",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000004",
    category: "set-of-cards",
    prompt: "Give me my subscriptions.",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_array_subscription_inobject_short",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000004",
    category: "set-of-cards",
    prompt: "Are any nodes NotReady?",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_nodes",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000005",
    category: "set-of-cards",
    prompt: "When do I have to renew my subscriptions?",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_array_subscription_inobject_short",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000005",
    category: "set-of-cards",
    prompt: "Which node has high CPU usage?",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_nodes",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000006",
    category: "set-of-cards",
    prompt: "How many runtimes is included in my subscriptions?",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_array_subscription_inobject_short",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000006",
    category: "set-of-cards",
    prompt: "Show me node resource usage",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_nodes",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000007",
    category: "set-of-cards",
    prompt: "How many runtimes is included in each of my subscription?",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_array_subscription_inobject_short",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000007",
    category: "set-of-cards",
    prompt: "Is worker-03 healthy?",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_nodes",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000008",
    category: "set-of-cards",
    prompt: "What are my subscriptions?",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_array_subscription_inobjectmore_short",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000008",
    category: "set-of-cards",
    prompt: "Which namespaces consume the most resources?",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_namespaces",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000009",
    category: "set-of-cards",
    prompt: "List my subscriptions.",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_array_subscription_inobjectmore_short",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000009",
    category: "set-of-cards",
    prompt: "Show me namespace resource usage",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_namespaces",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000010",
    category: "set-of-cards",
    prompt: "Show me my subscriptions.",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_array_subscription_inobjectmore_short",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000010",
    category: "set-of-cards",
    prompt: "How much is production-app namespace using?",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_namespaces",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000011",
    category: "set-of-cards",
    prompt: "Give me my subscriptions.",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_array_subscription_inobjectmore_short",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000011",
    category: "set-of-cards",
    prompt: "Show me kube-system namespace details",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_namespaces",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000012",
    category: "set-of-cards",
    prompt: "When do I have to renew my subscriptions?",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_array_subscription_inobjectmore_short",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000012",
    category: "set-of-cards",
    prompt: "Show me failing pods",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_failing_pods",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000013",
    category: "set-of-cards",
    prompt: "How many runtimes is included in my subscriptions?",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_array_subscription_inobjectmore_short",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000013",
    category: "set-of-cards",
    prompt: "Show me pods in CrashLoopBackOff",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_failing_pods",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000014",
    category: "set-of-cards",
    prompt: "How many runtimes is included in each of my subscription?",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_array_subscription_inobjectmore_short",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000014",
    category: "set-of-cards",
    prompt: "Which pods have high restart counts?",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_failing_pods",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000015",
    category: "set-of-cards",
    prompt: "What are my subscriptions?",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_array_subscription_direct_short",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000015",
    category: "set-of-cards",
    prompt: "Why is payment-service crashing?",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_failing_pods",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000016",
    category: "set-of-cards",
    prompt: "List my subscriptions.",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_array_subscription_direct_short",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000016",
    category: "set-of-cards",
    prompt: "Show me ImagePullBackOff errors",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_failing_pods",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000017",
    category: "set-of-cards",
    prompt: "Show me my subscriptions.",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_array_subscription_direct_short",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000017",
    category: "set-of-cards",
    prompt: "Who has cluster-admin access?",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_rbac_bindings",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000018",
    category: "set-of-cards",
    prompt: "Give me my subscriptions.",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_array_subscription_direct_short",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000018",
    category: "set-of-cards",
    prompt: "Show me RBAC permissions",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_rbac_bindings",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000019",
    category: "set-of-cards",
    prompt: "When do I have to renew my subscriptions?",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_array_subscription_direct_short",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000019",
    category: "set-of-cards",
    prompt: "Which users don't have MFA enabled?",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_rbac_bindings",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000020",
    category: "set-of-cards",
    prompt: "How many runtimes is included in my subscriptions?",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_array_subscription_direct_short",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000020",
    category: "set-of-cards",
    prompt: "Show me developer permissions",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_rbac_bindings",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000021",
    category: "set-of-cards",
    prompt: "How many runtimes is included in each of my subscription?",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_array_subscription_direct_short",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000021",
    category: "set-of-cards",
    prompt: "Show me persistent volume status",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_persistent_volumes",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000022",
    category: "set-of-cards",
    prompt: "What are my subscriptions?",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_array_subscription_direct_short",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000022",
    category: "set-of-cards",
    prompt: "Are any PVCs pending?",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_persistent_volumes",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000023",
    category: "set-of-cards",
    prompt: "List my subscriptions.",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_array_subscription_direct_short",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000023",
    category: "set-of-cards",
    prompt: "Which volumes are almost full?",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_persistent_volumes",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000024",
    category: "set-of-cards",
    prompt: "Show me my subscriptions.",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_array_subscription_direct_short",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000024",
    category: "set-of-cards",
    prompt: "Show me storage usage",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_persistent_volumes",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000025",
    category: "set-of-cards",
    prompt: "Give me my subscriptions.",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_array_subscription_direct_short",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000025",
    category: "set-of-cards",
    prompt: "Show me service status",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_services",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000026",
    category: "set-of-cards",
    prompt: "When do I have to renew my subscriptions?",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_array_subscription_direct_short",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000026",
    category: "set-of-cards",
    prompt: "Which services have unhealthy endpoints?",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_services",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000027",
    category: "set-of-cards",
    prompt: "How many runtimes is included in my subscriptions?",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_array_subscription_direct_short",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000027",
    category: "set-of-cards",
    prompt: "Is payment-service reachable?",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_services",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000028",
    category: "set-of-cards",
    prompt: "How many runtimes is included in each of my subscription?",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_array_subscription_direct_short",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000028",
    category: "set-of-cards",
    prompt: "Show me LoadBalancer services",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_services",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000029",
    category: "set-of-cards",
    prompt: "Who acted in the Toy Story?",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_simple_movie_actorsObjects_camelCase",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000029",
    category: "set-of-cards",
    prompt: "Show me cost analysis",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_cost_efficiency",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000030",
    category: "set-of-cards",
    prompt: "Who acted in the movie?",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_simple_movie_actorsObjects_camelCase",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000030",
    category: "set-of-cards",
    prompt: "Which namespaces are wasting resources?",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_cost_efficiency",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000031",
    category: "set-of-cards",
    prompt: "Toy Story actors?",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_simple_movie_actorsObjects_camelCase",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000031",
    category: "set-of-cards",
    prompt: "How much can we save in development?",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_cost_efficiency",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000032",
    category: "set-of-cards",
    prompt: "What are Toy Story actors?",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_simple_movie_actorsObjects_camelCase",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000032",
    category: "set-of-cards",
    prompt: "Show me right-sizing recommendations",
    expectedComponent: "set-of-cards",
    source: "k8s",
    dataset: {
      datasetId: "set-of-cards_cost_efficiency",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000033",
    category: "set-of-cards",
    prompt: "Who acted in the Toy Story?",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_simple_movie_actorsObjects_snakeCase",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000034",
    category: "set-of-cards",
    prompt: "Who acted in the movie?",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_simple_movie_actorsObjects_snakeCase",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000035",
    category: "set-of-cards",
    prompt: "Toy Story actors?",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_simple_movie_actorsObjects_snakeCase",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000036",
    category: "set-of-cards",
    prompt: "What are Toy Story actors?",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_simple_movie_actorsObjects_snakeCase",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000037",
    category: "set-of-cards",
    prompt: "List users from my cluster",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_array_k8s_users",
      dataType: "set-of-cards.dataset",
    }
  },
  {
    id: "set_of_cards_000038",
    category: "set-of-cards",
    prompt: "Show me RBAC permissions",
    expectedComponent: "set-of-cards",
    source: "general",
    dataset: {
      datasetId: "set-of-cards_array_k8s_users",
      dataType: "set-of-cards.dataset",
    }
  },
  // Tables
  {
    id: "table_000001",
    category: "tables",
    prompt: "What are my subscriptions?",
    expectedComponent: "table",
    source: "general",
    dataset: {
      datasetId: "table_array_subscription_inobject_long",
      dataType: "table.dataset",
    }
  },
  {
    id: "table_000001",
    category: "tables",
    prompt: "Are all my clusters healthy?",
    expectedComponent: "table",
    source: "k8s",
    dataset: {
      datasetId: "table_cluster_info",
      dataType: "table.dataset",
    }
  },
  {
    id: "table_000002",
    category: "tables",
    prompt: "List my subscriptions.",
    expectedComponent: "table",
    source: "general",
    dataset: {
      datasetId: "table_array_subscription_inobject_long",
      dataType: "table.dataset",
    }
  },
  {
    id: "table_000002",
    category: "tables",
    prompt: "Why is api-gateway failing?",
    expectedComponent: "table",
    source: "k8s",
    dataset: {
      datasetId: "table_services",
      dataType: "table.dataset",
    }
  },
  {
    id: "table_000003",
    category: "tables",
    prompt: "Show me my subscriptions.",
    expectedComponent: "table",
    source: "general",
    dataset: {
      datasetId: "table_array_subscription_inobject_long",
      dataType: "table.dataset",
    }
  },
  {
    id: "table_000004",
    category: "tables",
    prompt: "Give me my subscriptions.",
    expectedComponent: "table",
    source: "general",
    dataset: {
      datasetId: "table_array_subscription_inobject_long",
      dataType: "table.dataset",
    }
  },
  {
    id: "table_000005",
    category: "tables",
    prompt: "When do I have to renew my subscriptions?",
    expectedComponent: "table",
    source: "general",
    dataset: {
      datasetId: "table_array_subscription_inobject_long",
      dataType: "table.dataset",
    }
  },
  {
    id: "table_000006",
    category: "tables",
    prompt: "How many runtimes is included in my subscriptions?",
    expectedComponent: "table",
    source: "general",
    dataset: {
      datasetId: "table_array_subscription_inobject_long",
      dataType: "table.dataset",
    }
  },
  {
    id: "table_000007",
    category: "tables",
    prompt: "How many runtimes is included in each of my subscription?",
    expectedComponent: "table",
    source: "general",
    dataset: {
      datasetId: "table_array_subscription_inobject_long",
      dataType: "table.dataset",
    }
  },
  {
    id: "table_000008",
    category: "tables",
    prompt: "What are my subscriptions?",
    expectedComponent: "table",
    source: "general",
    dataset: {
      datasetId: "table_array_subscription_direct_long",
      dataType: "table.dataset",
    }
  },
  {
    id: "table_000009",
    category: "tables",
    prompt: "List my subscriptions.",
    expectedComponent: "table",
    source: "general",
    dataset: {
      datasetId: "table_array_subscription_direct_long",
      dataType: "table.dataset",
    }
  },
  {
    id: "table_000010",
    category: "tables",
    prompt: "Show me my subscriptions.",
    expectedComponent: "table",
    source: "general",
    dataset: {
      datasetId: "table_array_subscription_direct_long",
      dataType: "table.dataset",
    }
  },
  {
    id: "table_000011",
    category: "tables",
    prompt: "Give me my subscriptions.",
    expectedComponent: "table",
    source: "general",
    dataset: {
      datasetId: "table_array_subscription_direct_long",
      dataType: "table.dataset",
    }
  },
  {
    id: "table_000012",
    category: "tables",
    prompt: "When do I have to renew my subscriptions?",
    expectedComponent: "table",
    source: "general",
    dataset: {
      datasetId: "table_array_subscription_direct_long",
      dataType: "table.dataset",
    }
  },
  {
    id: "table_000013",
    category: "tables",
    prompt: "How many runtimes is included in my subscriptions?",
    expectedComponent: "table",
    source: "general",
    dataset: {
      datasetId: "table_array_subscription_direct_long",
      dataType: "table.dataset",
    }
  },
  {
    id: "table_000014",
    category: "tables",
    prompt: "How many runtimes is included in each of my subscription?",
    expectedComponent: "table",
    source: "general",
    dataset: {
      datasetId: "table_array_subscription_direct_long",
      dataType: "table.dataset",
    }
  },
  {
    id: "table_000015",
    category: "tables",
    prompt: "What are my subscriptions?",
    expectedComponent: "table",
    source: "general",
    dataset: {
      datasetId: "table_array_subscription_direct_long",
      dataType: "table.dataset",
    }
  },
  {
    id: "table_000016",
    category: "tables",
    prompt: "List my subscriptions.",
    expectedComponent: "table",
    source: "general",
    dataset: {
      datasetId: "table_array_subscription_direct_long",
      dataType: "table.dataset",
    }
  },
  {
    id: "table_000017",
    category: "tables",
    prompt: "Show me my subscriptions.",
    expectedComponent: "table",
    source: "general",
    dataset: {
      datasetId: "table_array_subscription_direct_long",
      dataType: "table.dataset",
    }
  },
  {
    id: "table_000018",
    category: "tables",
    prompt: "Give me my subscriptions.",
    expectedComponent: "table",
    source: "general",
    dataset: {
      datasetId: "table_array_subscription_direct_long",
      dataType: "table.dataset",
    }
  },
  {
    id: "table_000019",
    category: "tables",
    prompt: "When do I have to renew my subscriptions?",
    expectedComponent: "table",
    source: "general",
    dataset: {
      datasetId: "table_array_subscription_direct_long",
      dataType: "table.dataset",
    }
  },
  {
    id: "table_000020",
    category: "tables",
    prompt: "How many runtimes is included in my subscriptions?",
    expectedComponent: "table",
    source: "general",
    dataset: {
      datasetId: "table_array_subscription_direct_long",
      dataType: "table.dataset",
    }
  },
  {
    id: "table_000021",
    category: "tables",
    prompt: "How many runtimes is included in each of my subscription?",
    expectedComponent: "table",
    source: "general",
    dataset: {
      datasetId: "table_array_subscription_direct_long",
      dataType: "table.dataset",
    }
  },
  // Video Player
  {
    id: "video_player_000001",
    category: "video-player",
    prompt: "Show me Toy Story trailer.",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsNames_camelCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000002",
    category: "video-player",
    prompt: "Show me trailer of the Toy Story movie.",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsNames_camelCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000003",
    category: "video-player",
    prompt: "Show me the trailer",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsNames_camelCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000004",
    category: "video-player",
    prompt: "Show me trailer of the movie",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsNames_camelCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000005",
    category: "video-player",
    prompt: "Show movie trailer",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsNames_camelCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000006",
    category: "video-player",
    prompt: "Movie trailer?",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsNames_camelCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000007",
    category: "video-player",
    prompt: "Do you have movie trailer?",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsNames_camelCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000008",
    category: "video-player",
    prompt: "Show me Toy Story trailer.",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsNames_snakeCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000009",
    category: "video-player",
    prompt: "Show me trailer of the Toy Story movie.",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsNames_snakeCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000010",
    category: "video-player",
    prompt: "Show me the trailer",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsNames_snakeCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000011",
    category: "video-player",
    prompt: "Show me trailer of the movie",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsNames_snakeCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000012",
    category: "video-player",
    prompt: "Show movie trailer",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsNames_snakeCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000013",
    category: "video-player",
    prompt: "Movie trailer?",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsNames_snakeCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000014",
    category: "video-player",
    prompt: "Do you have movie trailer?",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsNames_snakeCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000015",
    category: "video-player",
    prompt: "Show me Toy Story trailer.",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsObjects_camelCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000016",
    category: "video-player",
    prompt: "Show me trailer of the Toy Story movie.",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsObjects_camelCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000017",
    category: "video-player",
    prompt: "Show me the trailer",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsObjects_camelCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000018",
    category: "video-player",
    prompt: "Show me trailer of the movie",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsObjects_camelCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000019",
    category: "video-player",
    prompt: "Show movie trailer",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsObjects_camelCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000020",
    category: "video-player",
    prompt: "Movie trailer?",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsObjects_camelCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000021",
    category: "video-player",
    prompt: "Do you have movie trailer?",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsObjects_camelCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000022",
    category: "video-player",
    prompt: "Show me Toy Story trailer.",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsObjects_snakeCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000023",
    category: "video-player",
    prompt: "Show me trailer of the Toy Story movie.",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsObjects_snakeCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000024",
    category: "video-player",
    prompt: "Show me the trailer",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsObjects_snakeCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000025",
    category: "video-player",
    prompt: "Show me trailer of the movie",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsObjects_snakeCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000026",
    category: "video-player",
    prompt: "Show movie trailer",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsObjects_snakeCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000027",
    category: "video-player",
    prompt: "Movie trailer?",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsObjects_snakeCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000028",
    category: "video-player",
    prompt: "Do you have movie trailer?",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsObjects_snakeCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000029",
    category: "video-player",
    prompt: "Show me Toy Story trailer.",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsNames_imdbNested_camelCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000030",
    category: "video-player",
    prompt: "Show me trailer of the Toy Story movie.",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsNames_imdbNested_camelCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000031",
    category: "video-player",
    prompt: "Show me the trailer",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsNames_imdbNested_camelCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000032",
    category: "video-player",
    prompt: "Show me trailer of the movie",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsNames_imdbNested_camelCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000033",
    category: "video-player",
    prompt: "Show movie trailer",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsNames_imdbNested_camelCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000034",
    category: "video-player",
    prompt: "Movie trailer?",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsNames_imdbNested_camelCase",
      dataType: "video-player.dataset",
    }
  },
  {
    id: "video_player_000035",
    category: "video-player",
    prompt: "Do you have movie trailer?",
    expectedComponent: "video-player",
    source: "general",
    dataset: {
      datasetId: "video-player_simple_movie_actorsNames_imdbNested_camelCase",
      dataType: "video-player.dataset",
    }
  },
];

// Group prompts by category and source, sorted by ID
export const groupedPrompts = {
  'one-card': {
    general: quickPrompts.filter(p => p.category === 'one-card' && p.source === 'general').sort((a, b) => a.id.localeCompare(b.id)),
    k8s: quickPrompts.filter(p => p.category === 'one-card' && p.source === 'k8s').sort((a, b) => a.id.localeCompare(b.id)),
  },
  'set-of-cards': {
    general: quickPrompts.filter(p => p.category === 'set-of-cards' && p.source === 'general').sort((a, b) => a.id.localeCompare(b.id)),
    k8s: quickPrompts.filter(p => p.category === 'set-of-cards' && p.source === 'k8s').sort((a, b) => a.id.localeCompare(b.id)),
  },
  'tables': {
    general: quickPrompts.filter(p => p.category === 'tables' && p.source === 'general').sort((a, b) => a.id.localeCompare(b.id)),
    k8s: quickPrompts.filter(p => p.category === 'tables' && p.source === 'k8s').sort((a, b) => a.id.localeCompare(b.id)),
  },
  'charts': {
    general: quickPrompts.filter(p => p.category === 'charts' && p.source === 'general').sort((a, b) => a.id.localeCompare(b.id)),
    k8s: quickPrompts.filter(p => p.category === 'charts' && p.source === 'k8s').sort((a, b) => a.id.localeCompare(b.id)),
  },
  'image': {
    general: quickPrompts.filter(p => p.category === 'image' && p.source === 'general').sort((a, b) => a.id.localeCompare(b.id)),
    k8s: quickPrompts.filter(p => p.category === 'image' && p.source === 'k8s').sort((a, b) => a.id.localeCompare(b.id)),
  },
  'video-player': {
    general: quickPrompts.filter(p => p.category === 'video-player' && p.source === 'general').sort((a, b) => a.id.localeCompare(b.id)),
    k8s: quickPrompts.filter(p => p.category === 'video-player' && p.source === 'k8s').sort((a, b) => a.id.localeCompare(b.id)),
  },
  'mixed': {
    general: quickPrompts.filter(p => p.category === 'mixed' && p.source === 'general').sort((a, b) => a.id.localeCompare(b.id)),
    k8s: quickPrompts.filter(p => p.category === 'mixed' && p.source === 'k8s').sort((a, b) => a.id.localeCompare(b.id)),
  },
};

// Get a random prompt from a category
export const getRandomPrompt = (category?: QuickPromptCategory): QuickPrompt => {
  const prompts = category ? quickPrompts.filter(p => p.category === category) : quickPrompts;
  return prompts[Math.floor(Math.random() * prompts.length)];
};
