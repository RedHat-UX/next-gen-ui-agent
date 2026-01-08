#!/usr/bin/env python3
"""
Aggregate evaluation reports from multiple GitLab pipeline runs.
Fetches reports via GitLab API using Job IDs and generates a comprehensive comparison dashboard.

Usage:
    # Using specific job IDs:
    python aggregate_reports.py \\
        --project-id 12345 \\
        --gitlab-url https://gitlab.com \\
        --token $CI_JOB_TOKEN \\
        --job-ids "1001,1002,1003"
    
    # Using automatic mode (last N pipelines):
    python aggregate_reports.py \\
        --project-id 12345 \\
        --gitlab-url https://gitlab.com \\
        --token $CI_JOB_TOKEN \\
        --limit 10
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
from collections import defaultdict

try:
    import requests
    # Disable SSL warnings for internal GitLab instances with self-signed certificates
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    print("Installing requests library...")
    os.system("pip3 install requests")
    import requests
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class GitLabAPIClient:
    """Client for GitLab API interactions."""
    
    def __init__(self, gitlab_url: str, project_id: str, token: str):
        self.gitlab_url = gitlab_url.rstrip('/')
        self.project_id = project_id
        self.token = token
        self.api_base = f"{self.gitlab_url}/api/v4/projects/{project_id}"
        # Use PRIVATE-TOKEN for cross-pipeline artifact access (works with both PAT and CI_JOB_TOKEN)
        self.headers = {"PRIVATE-TOKEN": token} if token else {}
    
    def fetch_job(self, job_id: int) -> Dict:
        """Fetch job details."""
        url = f"{self.api_base}/jobs/{job_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30, verify=False)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"✗ Failed to fetch job {job_id}: {e}")
            return None
    
    def download_artifact(self, job_id: int, artifact_path: str, output_path: Path) -> bool:
        """Download a specific artifact file from a job."""
        url = f"{self.api_base}/jobs/{job_id}/artifacts/{artifact_path}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=60, verify=False)
            response.raise_for_status()
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(response.content)
            return True
        except Exception as e:
            print(f"  ✗ Failed to download {artifact_path} from job {job_id}: {e}")
            return False


class ReportAggregator:
    """Aggregates reports from multiple pipeline runs."""
    
    def __init__(self):
        self.reports: List[Dict] = []
        self.aggregated_data: Dict[str, Any] = {
            "summary": {},
            "components": {},
            "models": {},
            "trends": [],
            "failed_tests": [],
            "warning_tests": []
        }
    
    def add_report(self, metadata: Dict, job_info: Dict = None):
        """Add a report to the aggregation."""
        # Enrich metadata with job info if available
        if job_info:
            metadata["job_info"] = {
                "id": job_info.get("id"),
                "name": job_info.get("name"),
                "status": job_info.get("status"),
                "created_at": job_info.get("created_at"),
                "web_url": job_info.get("web_url")
            }
            # Also add pipeline info from job
            if "pipeline" in job_info:
                metadata["pipeline_info"] = {
                    "id": job_info["pipeline"].get("id"),
                    "web_url": job_info["pipeline"].get("web_url", "#")
                }
        
        self.reports.append(metadata)
        print(f"  ✓ Added report: Pipeline #{metadata.get('pipeline_id', '?')}, Job #{metadata.get('job_id', '?')}")
    
    def aggregate(self):
        """Perform aggregation across all reports."""
        if not self.reports:
            print("No reports to aggregate")
            return
        
        print(f"\nAggregating {len(self.reports)} reports...")
        
        # Sort reports by timestamp
        self.reports.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Aggregate summary
        self._aggregate_summary()
        
        # Aggregate by component
        self._aggregate_components()
        
        # Aggregate by model
        self._aggregate_models()
        
        # Calculate trends
        self._calculate_trends()
        
        # Aggregate failed tests
        self._aggregate_failed_tests()
        
        # Aggregate warning tests
        self._aggregate_warnings()
        
        print("✓ Aggregation complete")
    
    def _aggregate_summary(self):
        """Aggregate overall summary statistics."""
        total_tests = sum(r.get("summary", {}).get("total_tests", 0) for r in self.reports)
        total_passed = sum(r.get("summary", {}).get("passed", 0) for r in self.reports)
        total_failed = sum(r.get("summary", {}).get("failed", 0) for r in self.reports)
        total_warnings = sum(r.get("summary", {}).get("warnings", 0) for r in self.reports)
        
        pass_rates = [r.get("summary", {}).get("pass_rate", 0) for r in self.reports if r.get("summary", {}).get("total_tests", 0) > 0]
        avg_pass_rate = sum(pass_rates) / len(pass_rates) if pass_rates else 0
        
        # Find best and worst runs
        valid_reports = [r for r in self.reports if r.get("summary", {}).get("total_tests", 0) > 0]
        if valid_reports:
            best_run = max(valid_reports, key=lambda x: x.get("summary", {}).get("pass_rate", 0))
            worst_run = min(valid_reports, key=lambda x: x.get("summary", {}).get("pass_rate", 0))
        else:
            best_run = worst_run = {}
        
        # Extract unique models and components
        models = list(set(r.get("model", "Unknown") for r in self.reports))
        all_components = set()
        for r in self.reports:
            all_components.update(r.get("by_component", {}).keys())
        
        self.aggregated_data["summary"] = {
            "total_pipelines": len(self.reports),
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "total_warnings": total_warnings,
            "overall_pass_rate": (total_passed / total_tests * 100) if total_tests > 0 else 0,
            "avg_pass_rate": avg_pass_rate,
            "models_tested": models,
            "unique_components": len(all_components),
            "best_run": {
                "pipeline_id": best_run.get("pipeline_id", "unknown"),
                "pass_rate": best_run.get("summary", {}).get("pass_rate", 0),
                "model": best_run.get("model", "Unknown"),
                "web_url": best_run.get("pipeline_info", {}).get("web_url", "#")
            },
            "worst_run": {
                "pipeline_id": worst_run.get("pipeline_id", "unknown"),
                "pass_rate": worst_run.get("summary", {}).get("pass_rate", 0),
                "model": worst_run.get("model", "Unknown"),
                "web_url": worst_run.get("pipeline_info", {}).get("web_url", "#")
            }
        }
    
    def _aggregate_components(self):
        """Aggregate statistics by component."""
        component_stats = defaultdict(lambda: {
            "total_tests": 0,
            "total_passed": 0,
            "total_failed": 0,
            "runs": [],
            "by_model": defaultdict(lambda: {"total": 0, "passed": 0, "runs": 0}),
            "failed_tests": defaultdict(int),
            "common_errors": defaultdict(int),
            "performance": []
        })
        
        for report in self.reports:
            for component, stats in report.get("by_component", {}).items():
                comp_data = component_stats[component]
                comp_data["total_tests"] += stats.get("total", 0)
                comp_data["total_passed"] += stats.get("passed", 0)
                comp_data["total_failed"] += stats.get("failed", 0)
                
                # Add run details
                comp_data["runs"].append({
                    "pipeline_id": report.get("pipeline_id", "unknown"),
                    "timestamp": report.get("timestamp", ""),
                    "model": report.get("model", "Unknown"),
                    "passed": stats.get("passed", 0),
                    "failed": stats.get("failed", 0),
                    "warnings": stats.get("warnings", 0),
                    "total": stats.get("total", 0),
                    "accuracy": stats.get("accuracy", 0),
                    "web_url": report.get("pipeline_info", {}).get("web_url", "#")
                })
                
                # Aggregate by model
                model = report.get("model", "Unknown")
                comp_data["by_model"][model]["total"] += stats.get("total", 0)
                comp_data["by_model"][model]["passed"] += stats.get("passed", 0)
                comp_data["by_model"][model]["runs"] += 1
                
                # Track failed tests
                for failed_test in stats.get("failed_tests", []):
                    test_key = failed_test.get("id", "unknown")
                    comp_data["failed_tests"][test_key] += 1
                    
                    # Track error patterns
                    error = failed_test.get("error", "Unknown error")
                    if error:
                        error_short = str(error)[:100]  # First 100 chars
                        comp_data["common_errors"][error_short] += 1
            
            # Add performance data
            for perf_key, perf_stats in report.get("performance_by_component", {}).items():
                component = perf_stats.get("component", "")
                if component:
                    component_stats[component]["performance"].append({
                        "pipeline_id": report.get("pipeline_id", "unknown"),
                        "model": report.get("model", "Unknown"),
                        "avg_ms": perf_stats.get("avg_ms", 0),
                        "min_ms": perf_stats.get("min_ms", 0),
                        "max_ms": perf_stats.get("max_ms", 0)
                    })
        
        # Calculate final statistics and trends
        for component, stats in component_stats.items():
            stats["overall_accuracy"] = (
                (stats["total_passed"] / stats["total_tests"] * 100)
                if stats["total_tests"] > 0 else 0
            )
            
            # Calculate trend
            if len(stats["runs"]) >= 3:
                recent_runs = stats["runs"][:3]
                recent_avg = sum(r.get("accuracy", 0) for r in recent_runs) / len(recent_runs)
                
                if len(stats["runs"]) >= 6:
                    older_runs = stats["runs"][3:6]
                    older_avg = sum(r.get("accuracy", 0) for r in older_runs) / len(older_runs)
                    trend_change = recent_avg - older_avg
                    
                    if trend_change > 2:
                        stats["trend"] = "improving"
                        stats["trend_value"] = f"+{trend_change:.1f}%"
                    elif trend_change < -2:
                        stats["trend"] = "degrading"
                        stats["trend_value"] = f"{trend_change:.1f}%"
                    else:
                        stats["trend"] = "stable"
                        stats["trend_value"] = "±0%"
                else:
                    stats["trend"] = "stable"
                    stats["trend_value"] = "N/A"
            else:
                stats["trend"] = "insufficient_data"
                stats["trend_value"] = "N/A"
            
            # Find best and worst model
            model_accs = {}
            for model, model_stats in stats["by_model"].items():
                if model_stats["total"] > 0:
                    model_accs[model] = (model_stats["passed"] / model_stats["total"] * 100)
            
            if model_accs:
                stats["best_model"] = max(model_accs.items(), key=lambda x: x[1])
                stats["worst_model"] = min(model_accs.items(), key=lambda x: x[1])
            
            # Get top errors
            stats["top_errors"] = sorted(
                stats["common_errors"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            # Get most failed tests
            stats["most_failed_tests"] = sorted(
                stats["failed_tests"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            # Calculate average performance
            if stats["performance"]:
                avg_perf = sum(p.get("avg_ms", 0) for p in stats["performance"]) / len(stats["performance"])
                min_perf = min((p.get("min_ms", 0) for p in stats["performance"]), default=0)
                max_perf = max((p.get("max_ms", 0) for p in stats["performance"]), default=0)
                stats["avg_performance_ms"] = {
                    "avg": avg_perf,
                    "min": min_perf,
                    "max": max_perf
                }
            
            # Convert defaultdicts to regular dicts
            stats["by_model"] = dict(stats["by_model"])
            stats["common_errors"] = dict(stats["common_errors"])
            stats["failed_tests"] = dict(stats["failed_tests"])
        
        self.aggregated_data["components"] = dict(component_stats)
    
    def _aggregate_models(self):
        """Aggregate statistics by model."""
        model_stats = defaultdict(lambda: {
            "total_tests": 0,
            "total_passed": 0,
            "total_failed": 0,
            "total_runs": 0,
            "by_component": defaultdict(lambda: {"total": 0, "passed": 0}),
            "performance": []
        })
        
        for report in self.reports:
            model = report.get("model", "Unknown")
            model_data = model_stats[model]
            
            summary = report.get("summary", {})
            model_data["total_tests"] += summary.get("total_tests", 0)
            model_data["total_passed"] += summary.get("passed", 0)
            model_data["total_failed"] += summary.get("failed", 0)
            model_data["total_runs"] += 1
            
            # Aggregate by component
            for component, stats in report.get("by_component", {}).items():
                model_data["by_component"][component]["total"] += stats.get("total", 0)
                model_data["by_component"][component]["passed"] += stats.get("passed", 0)
            
            # Add performance data
            for perf_stats in report.get("performance_by_component", {}).values():
                model_data["performance"].append(perf_stats.get("avg_ms", 0))
        
        # Calculate final statistics
        for model, stats in model_stats.items():
            stats["overall_pass_rate"] = (
                (stats["total_passed"] / stats["total_tests"] * 100)
                if stats["total_tests"] > 0 else 0
            )
            
            # Find best and worst component
            comp_accs = {}
            for component, comp_stats in stats["by_component"].items():
                if comp_stats["total"] > 0:
                    comp_accs[component] = (comp_stats["passed"] / comp_stats["total"] * 100)
            
            if comp_accs:
                stats["best_component"] = max(comp_accs.items(), key=lambda x: x[1])
                stats["worst_component"] = min(comp_accs.items(), key=lambda x: x[1])
            
            # Calculate average performance
            if stats["performance"]:
                stats["avg_performance_ms"] = sum(stats["performance"]) / len(stats["performance"])
            
            # Convert defaultdicts to regular dicts
            stats["by_component"] = dict(stats["by_component"])
        
        self.aggregated_data["models"] = dict(model_stats)
    
    def _calculate_trends(self):
        """Calculate trends over time."""
        trends = []
        for report in reversed(self.reports):  # Oldest to newest
            summary = report.get("summary", {})
            trends.append({
                "timestamp": report.get("timestamp", ""),
                "pipeline_id": report.get("pipeline_id", "unknown"),
                "model": report.get("model", "Unknown"),
                "pass_rate": summary.get("pass_rate", 0),
                "total_tests": summary.get("total_tests", 0)
            })
        
        self.aggregated_data["trends"] = trends
    
    def _aggregate_failed_tests(self):
        """Aggregate all failed tests across runs."""
        failed_tests = defaultdict(lambda: {
            "test_id": "",
            "component": "",
            "prompt": "",
            "failure_count": 0,
            "total_runs": 0,
            "errors": [],
            "models_failed": set(),
            "pipelines": []
        })
        
        for report in self.reports:
            for failed_test in report.get("failed_tests", []):
                test_id = failed_test.get("id", "unknown")
                test_data = failed_tests[test_id]
                
                test_data["test_id"] = test_id
                test_data["component"] = failed_test.get("component", "Unknown")
                test_data["prompt"] = failed_test.get("prompt", "")
                test_data["failure_count"] += 1
                test_data["total_runs"] = len(self.reports)
                test_data["errors"].append(failed_test.get("error", "Unknown"))
                test_data["models_failed"].add(report.get("model", "Unknown"))
                test_data["pipelines"].append({
                    "pipeline_id": report.get("pipeline_id", "unknown"),
                    "job_id": report.get("job_id", "unknown"),
                    "model": report.get("model", "Unknown"),
                    "error": failed_test.get("error", "Unknown"),
                    "llm_selected": failed_test.get("llm_selected", "Unknown"),
                    "expected_component": failed_test.get("component", "Unknown"),
                    "backend_data": failed_test.get("backend_data", ""),
                    "llm_output": failed_test.get("llm_output", "")
                })
        
        # Convert to list and sort
        failed_tests_list = []
        for test_data in failed_tests.values():
            test_data["models_failed"] = list(test_data["models_failed"])
            test_data["failure_rate"] = (
                (test_data["failure_count"] / test_data["total_runs"] * 100)
                if test_data["total_runs"] > 0 else 0
            )
            failed_tests_list.append(test_data)
        
        failed_tests_list.sort(key=lambda x: x["failure_count"], reverse=True)
        
        self.aggregated_data["failed_tests"] = failed_tests_list
    
    def _aggregate_warnings(self):
        """Aggregate warning tests across all reports."""
        warning_tests = defaultdict(lambda: {
            "test_id": "",
            "component": "",
            "prompt": "",
            "llm_selected": "",
            "warning_count": 0,
            "total_runs": 0,
            "reasons": [],
            "models_warned": set(),
            "pipelines": []
        })
        
        for report in self.reports:
            for warning_test in report.get("warning_tests", []):
                test_id = warning_test.get("id", "unknown")
                test_data = warning_tests[test_id]
                
                test_data["test_id"] = test_id
                test_data["component"] = warning_test.get("component", "Unknown")
                test_data["prompt"] = warning_test.get("prompt", "")
                test_data["llm_selected"] = warning_test.get("llm_selected", "Unknown")
                test_data["warning_count"] += 1
                test_data["total_runs"] = len(self.reports)
                test_data["reasons"].append(warning_test.get("judge_reasoning", ""))
                test_data["models_warned"].add(report.get("model", "Unknown"))
                test_data["pipelines"].append({
                    "pipeline_id": report.get("pipeline_id", "unknown"),
                    "job_id": report.get("job_id", "unknown"),
                    "model": report.get("model", "Unknown"),
                    "judge_reasoning": warning_test.get("judge_reasoning", "Unknown"),
                    "llm_selected": warning_test.get("llm_selected", "Unknown"),
                    "expected_component": warning_test.get("component", "Unknown"),
                    "backend_data": warning_test.get("backend_data", ""),
                    "llm_output": warning_test.get("llm_output", "")
                })
        
        # Convert to list and sort
        warning_tests_list = []
        for test_data in warning_tests.values():
            test_data["models_warned"] = list(test_data["models_warned"])
            test_data["warning_rate"] = (
                (test_data["warning_count"] / test_data["total_runs"] * 100)
                if test_data["total_runs"] > 0 else 0
            )
            warning_tests_list.append(test_data)
        
        warning_tests_list.sort(key=lambda x: x["warning_count"], reverse=True)
        
        self.aggregated_data["warning_tests"] = warning_tests_list
    
    def save(self, output_dir: Path):
        """Save aggregated data to JSON files."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save full aggregated data
        data_file = output_dir / "aggregated_data.json"
        with data_file.open("w") as f:
            json.dump(self.aggregated_data, f, indent=2)
        
        print(f"✓ Saved aggregated data: {data_file}")
        
        # Save individual reports
        reports_file = output_dir / "all_reports.json"
        with reports_file.open("w") as f:
            json.dump(self.reports, f, indent=2)
        
        print(f"✓ Saved individual reports: {reports_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate evaluation reports from GitLab jobs"
    )
    parser.add_argument(
        "--project-id",
        default=os.getenv("CI_PROJECT_ID"),
        help="GitLab project ID (default: $CI_PROJECT_ID)"
    )
    parser.add_argument(
        "--gitlab-url",
        default=os.getenv("CI_SERVER_URL", "https://gitlab.com"),
        help="GitLab URL (default: $CI_SERVER_URL or https://gitlab.com)"
    )
    parser.add_argument(
        "--token",
        default=os.getenv("CI_JOB_TOKEN"),
        help="GitLab API token (default: $CI_JOB_TOKEN)"
    )
    parser.add_argument(
        "--job-ids",
        help="Comma-separated job IDs to aggregate (e.g., '1001,1002,1003')"
    )
    parser.add_argument(
        "--output",
        default="public",
        help="Output directory (default: public)"
    )
    parser.add_argument(
        "--local-reports",
        help="Path to directory with local report_metadata.json files (for testing)"
    )
    
    args = parser.parse_args()
    
    output_dir = Path(args.output)
    
    print("="*70)
    print("Next Gen UI Agent Evaluation - Report Aggregator")
    print("="*70)
    
    aggregator = ReportAggregator()
    
    # Check if using local reports for testing
    if args.local_reports:
        print(f"\nLoading local reports from: {args.local_reports}")
        local_dir = Path(args.local_reports)
        
        for metadata_file in local_dir.glob("**/report_metadata.json"):
            print(f"  Loading {metadata_file.name}...")
            with metadata_file.open("r") as f:
                metadata = json.load(f)
                aggregator.add_report(metadata)
    
    else:
        # Fetch from GitLab API
        if not args.project_id:
            print("ERROR: No project ID provided. Set --project-id or CI_PROJECT_ID")
            sys.exit(1)
        
        if not args.token:
            print("ERROR: No API token provided. Set --token or CI_JOB_TOKEN")
            sys.exit(1)
        
        if not args.job_ids:
            print("ERROR: No job IDs provided. Use --job-ids with comma-separated IDs")
            print("Example: --job-ids '45128409,45129838,45128592'")
            sys.exit(1)
        
        print(f"\nConnecting to GitLab: {args.gitlab_url}")
        print(f"Project ID: {args.project_id}")
        
        client = GitLabAPIClient(args.gitlab_url, args.project_id, args.token)
        
        # Parse job IDs
        job_ids = [jid.strip() for jid in args.job_ids.split(",")]
        print(f"Fetching {len(job_ids)} job(s): {', '.join(job_ids)}")
        
        # Create reports directory
        reports_dir = output_dir / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Process each job ID
        for job_id in job_ids:
            print(f"\nProcessing job #{job_id}...")
            
            # Get job info
            job_info = client.fetch_job(int(job_id))
            if not job_info:
                print(f"  ⚠ Skipping job {job_id} (not found)")
                continue
            
            print(f"  Job: {job_info.get('name', 'unknown')} (status: {job_info.get('status', 'unknown')})")
            
            # Download metadata
            metadata_path = reports_dir / f"pipeline_{job_info.get('pipeline', {}).get('id', job_id)}_metadata.json"
            success = client.download_artifact(
                int(job_id),
                "tests/ai_eval_arh/report_metadata.json",
                metadata_path
            )
            
            if success:
                # Load metadata
                with metadata_path.open("r") as f:
                    metadata = json.load(f)
                
                # Download HTML report to extract backend_data
                html_path = reports_dir / f"pipeline_{job_info.get('pipeline', {}).get('id', job_id)}.html"
                html_success = client.download_artifact(
                    int(job_id),
                    "tests/ai_eval_arh/arh_eval_report.html",
                    html_path
                )
                
                # Extract backend_data and llm_output from HTML (always, for reliability)
                if html_success and html_path.exists():
                    print(f"  → Extracting backend_data from HTML...")
                    try:
                        # Import extraction function
                        sys.path.insert(0, str(Path(__file__).parent))
                        from save_report_metadata import extract_full_metadata_from_html
                        
                        # Extract from HTML
                        html_data = extract_full_metadata_from_html(html_path)
                        
                        if html_data:
                            # Build test_id map for failed tests
                            html_failed_map = {ft['id']: ft for ft in html_data.get('failed_tests', [])}
                            html_warning_map = {wt['id']: wt for wt in html_data.get('warning_tests', [])}
                            
                            # Enrich metadata failed tests
                            for failed_test in metadata.get('failed_tests', []):
                                test_id = failed_test.get('id')
                                if test_id in html_failed_map:
                                    html_test = html_failed_map[test_id]
                                    failed_test['backend_data'] = html_test.get('backend_data', '')
                                    failed_test['llm_output'] = html_test.get('llm_output', '')
                            
                            # Enrich metadata warning tests
                            for warning_test in metadata.get('warning_tests', []):
                                test_id = warning_test.get('id')
                                if test_id in html_warning_map:
                                    html_test = html_warning_map[test_id]
                                    warning_test['backend_data'] = html_test.get('backend_data', '')
                                    warning_test['llm_output'] = html_test.get('llm_output', '')
                            
                            print(f"  ✓ Enriched {len(html_failed_map)} failed + {len(html_warning_map)} warning tests with backend_data")
                    except Exception as e:
                        print(f"  ⚠ Could not extract from HTML: {e}")
                
                # Add enriched metadata to aggregator
                aggregator.add_report(metadata, job_info)
            else:
                print(f"  ⚠ Could not download metadata for job {job_id}")
    
    # Perform aggregation
    if len(aggregator.reports) == 0:
        print("\nERROR: No reports found to aggregate!")
        sys.exit(1)
    
    aggregator.aggregate()
    
    # Save aggregated data
    aggregator.save(output_dir)
    
    print("\n" + "="*70)
    print(f"SUCCESS: Aggregation complete! Found {len(aggregator.reports)} report(s)")
    print(f"Output directory: {output_dir.absolute()}")
    print("="*70)
    print("\nNext step: Run generate_dashboard.py to create the HTML dashboard")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

