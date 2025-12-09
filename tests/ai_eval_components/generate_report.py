"""
Generic HTML report generator for evaluation results.
Works with single or multiple datasets (Velias's movies/subscriptions, K8s, etc.)

Usage:
  # Single dataset (K8s only):
  python -m ai_eval_components.generate_report --datasets dataset_k8s --title "K8s Tests"

  # Single dataset (Velias's only):
  python -m ai_eval_components.generate_report --datasets dataset --title "Movies/Subscriptions"

  # Combined (both datasets):
  python -m ai_eval_components.generate_report \
    --datasets dataset,dataset_k8s \
    --title "Complete Evaluation" \
    --labels "Movies/Subscriptions,Kubernetes"
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

# Defaults (can be overridden by command line args)
ERRORS_DIR = Path("tests/ai_eval_components/errors")
REPORT_OUTPUT = Path("tests/ai_eval_components/eval_report.html")


def load_dataset_file(filepath: Path):
    """Load a dataset JSON file."""
    with filepath.open("r") as f:
        return json.load(f)


def load_perf_stats(error_dirs, dataset_labels):
    """Load performance stats from all error directories with dataset labels."""
    all_perf_stats = {
        "overall": {"min": 0, "mean": 0, "avg": 0, "perc95": 0, "max": 0},
        "by_component": {},  # Format: {(component, dataset_label): stats}
        "judge_enabled": False,  # Will be set to True if any dataset has judges enabled
        "judge_model": None,
        "agent_model": None,
    }

    for i, error_dir in enumerate(error_dirs):
        perf_file = error_dir / "perf_stats.json"
        if perf_file.exists():
            dataset_label = (
                dataset_labels[i] if i < len(dataset_labels) else f"Dataset {i+1}"
            )
            with perf_file.open("r") as f:
                stats = json.load(f)
                # Store component stats with dataset label
                if "by_component" in stats:
                    for component, component_stats in stats["by_component"].items():
                        key = (component, dataset_label)
                        all_perf_stats["by_component"][key] = component_stats

                # Capture judge info if present
                if stats.get("judge_enabled", False):
                    all_perf_stats["judge_enabled"] = True
                    all_perf_stats["judge_model"] = stats.get("judge_model")

                # Capture agent model
                if stats.get("agent_model"):
                    all_perf_stats["agent_model"] = stats.get("agent_model")

    return all_perf_stats


def load_error_file(filepath: Path):
    """Load error file if it exists."""
    if filepath.exists():
        with filepath.open("r") as f:
            return f.readlines()
    return []


def analyze_results(dataset_dirs, dataset_labels=None, error_dirs=None):
    """Analyze dataset files and their error reports from one or more datasets."""
    results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "by_component": {},
        "by_dataset": {},
        "test_details": [],
    }

    # Convert dataset_dirs to list of Path objects
    if isinstance(dataset_dirs, str):
        dataset_dirs = [Path(f"tests/ai_eval_components/{dataset_dirs}")]
    else:
        dataset_dirs = [Path(f"tests/ai_eval_components/{d}") for d in dataset_dirs]

    # Default labels if not provided
    if dataset_labels is None:
        dataset_labels = [d.name for d in dataset_dirs]

    # Convert error_dirs to list of Path objects (default to single errors dir)
    if error_dirs is None:
        error_dirs = [Path("tests/ai_eval_components/errors")]
    elif isinstance(error_dirs, str):
        error_dirs = [Path(f"tests/ai_eval_components/{error_dirs}")]
    else:
        error_dirs = [Path(f"tests/ai_eval_components/{d}") for d in error_dirs]

    # Map error directories to dataset directories (same index)
    # This assumes error_dirs[i] corresponds to dataset_dirs[i]
    dataset_to_error_dir = {}
    for i, dataset_dir in enumerate(dataset_dirs):
        if i < len(error_dirs):
            dataset_to_error_dir[dataset_dir] = error_dirs[i]
        else:
            dataset_to_error_dir[dataset_dir] = error_dirs[0]  # fallback to first

    # Iterate through ALL dataset files (not just error files)
    for i, dataset_dir in enumerate(dataset_dirs):
        dataset_label = dataset_labels[i]
        error_dir = dataset_to_error_dir[dataset_dir]

        for dataset_file in sorted(dataset_dir.glob("*.json")):
            # Check if corresponding error file exists
            error_filename = dataset_file.stem + "-errors.txt"
            error_file = error_dir / error_filename

            dataset = load_dataset_file(dataset_file)
            error_lines = load_error_file(error_file) if error_file.exists() else []

            # Parse errors to get failed test IDs
            failed_ids = set()
            for line in error_lines:
                if line.startswith("==== AGENT "):
                    # Extract test ID from "==== AGENT set-of-cards-000017 ===="
                    test_id = line.split("==== AGENT ")[1].split(" ====")[0].strip()
                    failed_ids.add(test_id)

            component = dataset_file.stem.rsplit("-", 1)[
                0
            ]  # e.g., "set-of-cards" from "set-of-cards-5"

            # Initialize component stats if needed
            if component not in results["by_component"]:
                results["by_component"][component] = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                }

            # Initialize dataset stats if needed
            if dataset_label not in results["by_dataset"]:
                results["by_dataset"][dataset_label] = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                }

            for test in dataset:
                # Skip warn_only tests (these are not actually run by eval.py)
                if test.get("warn_only") is True:
                    continue

                test_id = test["id"]
                user_prompt = test["user_prompt"]
                expected_component = test["expected_component"]

                is_passed = test_id not in failed_ids

                # Update global stats
                results["total_tests"] += 1
                results["by_component"][component]["total"] += 1
                results["by_dataset"][dataset_label]["total"] += 1

                if is_passed:
                    results["passed"] += 1
                    results["by_component"][component]["passed"] += 1
                    results["by_dataset"][dataset_label]["passed"] += 1
                    status = "PASS"
                    error_msg = None
                else:
                    results["failed"] += 1
                    results["by_component"][component]["failed"] += 1
                    results["by_dataset"][dataset_label]["failed"] += 1
                    status = "FAIL"
                    # Extract error message from error file
                    error_msg = "Unknown error"
                    in_errors_section = False
                    for line in error_lines:
                        if f"==== AGENT {test_id} ====" in line:
                            in_errors_section = True
                        elif in_errors_section:
                            if line.strip().startswith('"'):
                                # Found error message like "component.invalid: ..."
                                error_msg = line.strip().strip('"').strip(",")
                                break
                            elif line.startswith("===="):
                                break

                results["test_details"].append(
                    {
                        "id": test_id,
                        "prompt": user_prompt,
                        "component": expected_component,
                        "dataset": dataset_label,
                        "dataset_file": dataset_file.name,
                        "status": status,
                        "error": error_msg,
                    }
                )

    # Load performance stats from error directories
    results["perf_stats"] = load_perf_stats(error_dirs, dataset_labels)

    return results


def generate_html_report(results, title="Evaluation Report", model=None):
    """Generate HTML report from results."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    pass_rate = (
        (results["passed"] / results["total_tests"] * 100)
        if results["total_tests"] > 0
        else 0
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 28px;
        }}
        .timestamp {{
            color: #7f8c8d;
            font-size: 14px;
            margin-bottom: 30px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            padding: 20px;
            border-radius: 6px;
            text-align: center;
        }}
        .summary-card.total {{
            background: #3498db;
            color: white;
        }}
        .summary-card.passed {{
            background: #2ecc71;
            color: white;
        }}
        .summary-card.failed {{
            background: #e74c3c;
            color: white;
        }}
        .summary-card .number {{
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .summary-card .label {{
            font-size: 14px;
            opacity: 0.9;
        }}
        .component-stats {{
            margin-bottom: 30px;
        }}
        .component-stats h2 {{
            color: #2c3e50;
            font-size: 20px;
            margin-bottom: 15px;
        }}
        .component-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }}
        .component-item {{
            padding: 15px;
            background: #ecf0f1;
            border-radius: 6px;
            border-left: 4px solid #3498db;
        }}
        .component-name {{
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 8px;
        }}
        .component-stats-text {{
            font-size: 14px;
            color: #555;
        }}
        .test-results {{
            margin-top: 30px;
        }}
        .test-results h2 {{
            color: #2c3e50;
            font-size: 20px;
            margin-bottom: 15px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        th {{
            background: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #ecf0f1;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .status {{
            padding: 4px 12px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 12px;
            display: inline-block;
        }}
        .status.pass {{
            background: #d4edda;
            color: #155724;
        }}
        .status.fail {{
            background: #f8d7da;
            color: #721c24;
        }}
        .error {{
            color: #e74c3c;
            font-size: 12px;
            font-family: monospace;
        }}
        .prompt {{
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .stats-table {{
            width: 100%;
            margin-top: 20px;
            background: white;
            border-radius: 6px;
            overflow: hidden;
        }}
        .stats-table th {{
            background: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            font-size: 14px;
        }}
        .stats-table td {{
            padding: 12px;
            border-bottom: 1px solid #ecf0f1;
            font-size: 14px;
        }}
        .stats-table tr:last-child td {{
            border-bottom: none;
        }}
        .stats-table tr:hover {{
            background: #f8f9fa;
        }}
        .pass-rate {{
            font-weight: bold;
        }}
        .pass-rate.high {{
            color: #27ae60;
        }}
        .pass-rate.medium {{
            color: #f39c12;
        }}
        .pass-rate.low {{
            color: #e74c3c;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 {title}</h1>
        <div class="timestamp">Generated: {timestamp}{' | Model: ' + model if model else ''}</div>

        <div class="component-stats" style="margin-bottom: 20px;">
            <h2>📋 Test Execution Summary</h2>
            <table class="stats-table">
                <tbody>
                    <tr>
                        <td><strong>Total Tests Executed</strong></td>
                        <td>{results["total_tests"]} tests</td>
                    </tr>
                    <tr>
                        <td><strong>Tests Passed</strong></td>
                        <td style="color: #27ae60;">{results["passed"]} tests ({pass_rate:.1f}%)</td>
                    </tr>
                    <tr>
                        <td><strong>Tests Failed</strong></td>
                        <td style="color: #e74c3c;">{results["failed"]} tests ({100-pass_rate:.1f}%)</td>
                    </tr>
                    <tr>
                        <td><strong>Datasets Tested</strong></td>
                        <td>{len(results["by_dataset"])} dataset(s)</td>
                    </tr>
                    <tr>
                        <td><strong>Components Evaluated</strong></td>
                        <td>{len(results["by_component"])} component(s)</td>
                    </tr>"""

    # Add model info
    agent_model = results["perf_stats"].get("agent_model", model or "Unknown")
    html += f"""
                    <tr>
                        <td><strong>🔧 Agent Model</strong></td>
                        <td>{agent_model}</td>
                    </tr>"""

    # Add judge info if judges were enabled
    if results["perf_stats"].get("judge_enabled", False):
        judge_model = results["perf_stats"].get("judge_model", "Unknown")
        html += f"""
                    <tr>
                        <td><strong>🤖 Judge Model</strong></td>
                        <td>{judge_model}</td>
                    </tr>
                    <tr>
                        <td><strong>Judge Evaluation</strong></td>
                        <td style="color: #27ae60;">✅ Enabled</td>
                    </tr>"""

    html += f"""
                </tbody>
            </table>
        </div>

        <div class="summary">
            <div class="summary-card total">
                <div class="number">{results["total_tests"]}</div>
                <div class="label">Total Tests</div>
            </div>
            <div class="summary-card passed">
                <div class="number">{results["passed"]}</div>
                <div class="label">Passed</div>
            </div>
            <div class="summary-card failed">
                <div class="number">{results["failed"]}</div>
                <div class="label">Failed</div>
            </div>
            <div class="summary-card total">
                <div class="number">{pass_rate:.1f}%</div>
                <div class="label">Pass Rate</div>
            </div>
        </div>
"""

    # Add dataset breakdown if we have multiple datasets
    if len(results["by_dataset"]) > 1:
        html += """
        <div class="component-stats">
            <h2>📂 Results by Dataset</h2>
            <div class="component-grid">
"""
        for dataset, stats in results["by_dataset"].items():
            ds_pass_rate = (
                (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            )
            html += f"""
                <div class="component-item">
                    <div class="component-name">{dataset}</div>
                    <div class="component-stats-text">
                        Total: {stats["total"]} |
                        Passed: {stats["passed"]} |
                        Failed: {stats["failed"]} |
                        Pass Rate: {ds_pass_rate:.1f}%
                    </div>
                </div>
"""
        html += """
            </div>
        </div>
"""

    html += """
        <div class="component-stats">
            <h2>📊 Results by Component</h2>
            <div class="component-grid">
"""

    for component, stats in results["by_component"].items():
        comp_pass_rate = (
            (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
        )
        html += f"""
                <div class="component-item">
                    <div class="component-name">{component}</div>
                    <div class="component-stats-text">
                        Total: {stats["total"]} |
                        Passed: {stats["passed"]} |
                        Failed: {stats["failed"]} |
                        Pass Rate: {comp_pass_rate:.1f}%
                    </div>
                </div>
"""

    html += """
            </div>
        </div>

        <div class="component-stats">
            <h2>📈 Detailed Statistics</h2>
            <table class="stats-table">
                <thead>
                    <tr>
                        <th>Component</th>
                        <th>Total Tests</th>
                        <th>Passed</th>
                        <th>Failed</th>
                        <th>Pass Rate</th>
                        <th>Error Rate</th>
                    </tr>
                </thead>
                <tbody>
"""

    # Add component statistics rows
    for component, stats in sorted(results["by_component"].items()):
        comp_pass_rate = (
            (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
        )
        comp_error_rate = (
            (stats["failed"] / stats["total"] * 100) if stats["total"] > 0 else 0
        )

        # Color code pass rate
        if comp_pass_rate >= 70:
            rate_class = "high"
        elif comp_pass_rate >= 40:
            rate_class = "medium"
        else:
            rate_class = "low"

        html += f"""
                    <tr>
                        <td><strong>{component}</strong></td>
                        <td>{stats["total"]}</td>
                        <td style="color: #27ae60;">{stats["passed"]}</td>
                        <td style="color: #e74c3c;">{stats["failed"]}</td>
                        <td><span class="pass-rate {rate_class}">{comp_pass_rate:.1f}%</span></td>
                        <td>{comp_error_rate:.1f}%</td>
                    </tr>
"""

    html += """
                </tbody>
            </table>
        </div>
"""

    # Add performance stats section if available
    if results.get("perf_stats") and results["perf_stats"]["by_component"]:
        html += """
        <div class="component-stats">
            <h2>⚡ Performance Metrics (Inference Time)</h2>
            <table class="stats-table">
                <thead>
                    <tr>
                        <th>Component</th>
                        <th>Min (ms)</th>
                        <th>Mean (ms)</th>
                        <th>Average (ms)</th>
                        <th>95th Percentile (ms)</th>
                        <th>Max (ms)</th>
                    </tr>
                </thead>
                <tbody>
"""

        for (component, dataset_label), stats in sorted(
            results["perf_stats"]["by_component"].items()
        ):
            html += f"""
                    <tr>
                        <td><strong>{component}</strong> <span style="color: #7f8c8d; font-size: 12px;">({dataset_label})</span></td>
                        <td>{stats['min']}</td>
                        <td>{stats['mean']}</td>
                        <td>{stats['avg']}</td>
                        <td>{stats['perc95']}</td>
                        <td>{stats['max']}</td>
                    </tr>
"""

        html += """
                </tbody>
            </table>
            <p style="margin-top: 10px; color: #7f8c8d; font-size: 13px;">
                ⏱️ Performance times measured from LLM inference start to response completion.
                Times >30s excluded (API throttling).
            </p>
        </div>
"""

    html += """
        <div class="test-results">
            <h2>📝 Test Details</h2>
            <table>
                <thead>
                    <tr>
                        <th>Test ID</th>
                        <th>Prompt</th>
                        <th>Component</th>
                        <th>Dataset</th>
                        <th>Status</th>
                        <th>Error</th>
                    </tr>
                </thead>
                <tbody>
"""

    for test in results["test_details"]:
        status_class = "pass" if test["status"] == "PASS" else "fail"
        error_cell = (
            f'<td class="error">{test["error"]}</td>' if test["error"] else "<td>-</td>"
        )

        html += f"""
                    <tr>
                        <td>{test["id"]}</td>
                        <td class="prompt" title="{test["prompt"]}">{test["prompt"]}</td>
                        <td>{test["component"]}</td>
                        <td>{test["dataset"]}</td>
                        <td><span class="status {status_class}">{test["status"]}</span></td>
                        {error_cell}
                    </tr>
"""

    html += """
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

    return html


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate HTML report for evaluation results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # K8s tests only:
  python -m ai_eval_components.generate_report --datasets dataset_k8s --title "K8s Tests"

  # Velias's tests only:
  python -m ai_eval_components.generate_report --datasets dataset --title "Movies/Subscriptions"

  # Combined report:
  python -m ai_eval_components.generate_report \\
    --datasets dataset,dataset_k8s \\
    --title "Complete Evaluation" \\
    --labels "Movies/Subscriptions,Kubernetes" \\
    --error-dirs errors,errors_k8s
        """,
    )
    parser.add_argument(
        "--datasets",
        default="dataset_k8s",
        help="Comma-separated list of dataset directories (default: dataset_k8s)",
    )
    parser.add_argument(
        "--labels",
        default=None,
        help="Comma-separated list of dataset labels (default: use directory names)",
    )
    parser.add_argument(
        "--error-dirs",
        default=None,
        help="Comma-separated list of error directories (default: errors)",
    )
    parser.add_argument(
        "--title",
        default="Evaluation Report",
        help="Report title (default: Evaluation Report)",
    )
    parser.add_argument(
        "--output",
        default="tests/ai_eval_components/eval_report.html",
        help="Output HTML file path (default: tests/ai_eval_components/eval_report.html)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Model name to display in report (e.g., 'llama3.2:3b (Ollama)')",
    )

    args = parser.parse_args()

    # Parse datasets and labels
    dataset_dirs = [d.strip() for d in args.datasets.split(",")]
    dataset_labels = None
    if args.labels:
        dataset_labels = [label.strip() for label in args.labels.split(",")]
        if len(dataset_labels) != len(dataset_dirs):
            print(
                f"ERROR: Number of labels ({len(dataset_labels)}) must match number of datasets ({len(dataset_dirs)})"
            )
            exit(1)

    # Parse error directories
    error_dirs = None
    if args.error_dirs:
        error_dirs = [d.strip() for d in args.error_dirs.split(",")]

    print(f"Analyzing evaluation results from {len(dataset_dirs)} dataset(s)...")
    results = analyze_results(dataset_dirs, dataset_labels, error_dirs)

    print(f"\nTotal tests: {results['total_tests']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")

    if results["by_dataset"]:
        print("\nBy dataset:")
        for dataset, stats in results["by_dataset"].items():
            pass_rate = (
                (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            )
            print(
                f"  {dataset}: {stats['passed']}/{stats['total']} passed ({pass_rate:.1f}%)"
            )

    print("\nGenerating HTML report...")
    html = generate_html_report(results, title=args.title, model=args.model)

    output_path = Path(args.output)
    output_path.write_text(html)
    print(f"Report generated: {output_path}")
    print(f"\nOpen it with: open {output_path}")
