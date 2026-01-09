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


def analyze_results(dataset_dirs, dataset_labels=None, error_dirs=None, llm_out_dirs=None):
    """Analyze dataset files and their error reports from one or more datasets."""
    results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "warnings": 0,  # Passed but selected different component
        "by_component": {},
        "by_dataset": {},
        "test_details": [],
        "warning_tests": [],  # List of tests with warnings
    }

    # Convert dataset_dirs to list of Path objects
    if isinstance(dataset_dirs, str):
        # Check if path already includes full path or is relative
        if dataset_dirs.startswith("tests/ai_eval_components/") or dataset_dirs.startswith("/"):
            dataset_dirs = [Path(dataset_dirs)]
        else:
            dataset_dirs = [Path(f"tests/ai_eval_components/{dataset_dirs}")]
    else:
        dataset_dirs = [
            Path(d) if (d.startswith("tests/ai_eval_components/") or d.startswith("/")) else Path(f"tests/ai_eval_components/{d}")
            for d in dataset_dirs
        ]

    # Default labels if not provided
    if dataset_labels is None:
        dataset_labels = [d.name for d in dataset_dirs]

    # Convert error_dirs to list of Path objects (default to single errors dir)
    if error_dirs is None:
        error_dirs = [Path("tests/ai_eval_components/errors")]
    elif isinstance(error_dirs, str):
        # Check if path already includes full path or is relative
        if error_dirs.startswith("tests/ai_eval_components/") or error_dirs.startswith("/"):
            error_dirs = [Path(error_dirs)]
        else:
            error_dirs = [Path(f"tests/ai_eval_components/{error_dirs}")]
    else:
        error_dirs = [
            Path(d) if (d.startswith("tests/ai_eval_components/") or d.startswith("/")) else Path(f"tests/ai_eval_components/{d}")
            for d in error_dirs
        ]

    # Convert llm_out_dirs to list of Path objects (default to llm_out sibling of errors)
    if llm_out_dirs is None:
        llm_out_dirs = [error_dir.parent / "llm_out" for error_dir in error_dirs]
    elif isinstance(llm_out_dirs, str):
        if llm_out_dirs.startswith("tests/ai_eval_components/") or llm_out_dirs.startswith("/"):
            llm_out_dirs = [Path(llm_out_dirs)]
        else:
            llm_out_dirs = [Path(f"tests/ai_eval_components/{llm_out_dirs}")]
    else:
        llm_out_dirs = [
            Path(d) if (d.startswith("tests/ai_eval_components/") or d.startswith("/")) else Path(f"tests/ai_eval_components/{d}")
            for d in llm_out_dirs
        ]

    # Map error directories to dataset directories (same index)
    # This assumes error_dirs[i] corresponds to dataset_dirs[i]
    dataset_to_error_dir = {}
    dataset_to_llm_out_dir = {}
    for i, dataset_dir in enumerate(dataset_dirs):
        if i < len(error_dirs):
            dataset_to_error_dir[dataset_dir] = error_dirs[i]
        else:
            dataset_to_error_dir[dataset_dir] = error_dirs[0]  # fallback to first
        if i < len(llm_out_dirs):
            dataset_to_llm_out_dir[dataset_dir] = llm_out_dirs[i]
        else:
            dataset_to_llm_out_dir[dataset_dir] = llm_out_dirs[0] if llm_out_dirs else None

    # Iterate through ALL dataset files (not just error files)
    for i, dataset_dir in enumerate(dataset_dirs):
        dataset_label = dataset_labels[i]
        error_dir = dataset_to_error_dir[dataset_dir]
        llm_out_dir = dataset_to_llm_out_dir.get(dataset_dir)

        for dataset_file in sorted(dataset_dir.glob("*.json")):
            # Check if corresponding error file exists
            error_filename = dataset_file.stem + "-errors.txt"
            error_file = error_dir / error_filename

            # Check if corresponding llm_out file exists
            llm_out_filename = dataset_file.stem + ".txt"
            llm_out_file = llm_out_dir / llm_out_filename if llm_out_dir else None

            dataset = load_dataset_file(dataset_file)
            error_lines = load_error_file(error_file) if error_file.exists() else []
            llm_out_lines = load_error_file(llm_out_file) if llm_out_file and llm_out_file.exists() else []

            # Parse errors to get failed test IDs (both AGENT and SYSTEM errors)
            failed_ids = set()
            for line in error_lines:
                if line.startswith("==== AGENT ") or line.startswith("==== SYSTEM "):
                    # Extract test ID from "==== AGENT test-id ====" or "==== SYSTEM test-id ===="
                    if "==== AGENT " in line:
                        test_id = line.split("==== AGENT ")[1].split(" ====")[0].strip()
                    else:
                        test_id = line.split("==== SYSTEM ")[1].split(" ====")[0].strip()
                    failed_ids.add(test_id)

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
                
                # Normalize component name (replace spaces with hyphens)
                expected_component = expected_component.replace(" ", "-")

                # Initialize component stats if needed (based on actual expected_component)
                if expected_component not in results["by_component"]:
                    results["by_component"][expected_component] = {
                        "total": 0,
                        "passed": 0,
                        "failed": 0,
                    }

                is_passed = test_id not in failed_ids

                # Update global stats
                results["total_tests"] += 1
                results["by_component"][expected_component]["total"] += 1
                results["by_dataset"][dataset_label]["total"] += 1

                # Extract LLM selected component from error file OR llm_out file
                llm_selected_component = None
                
                # Helper function to extract component from lines
                def extract_llm_component(lines, test_id):
                    in_test_section = False
                    in_llm_outputs = False
                    llm_json_lines = []
                    
                    for line in lines:
                        # Found the start of our specific test
                        if f"==== DATASET ID {test_id} ====" in line or f"==== AGENT {test_id} ====" in line:
                            in_test_section = True
                            in_llm_outputs = False
                            llm_json_lines = []
                            continue
                        
                        # If we're in our test section
                        if in_test_section:
                            # Hit the start of a different test - stop here
                            if line.startswith("==== DATASET ID") or line.startswith("==== AGENT"):
                                break
                            
                            # Found LLM outputs section
                            if "LLM outputs:" in line:
                                in_llm_outputs = True
                                llm_json_lines = []
                                continue
                            
                            # Collecting LLM output JSON
                            if in_llm_outputs:
                                if line.startswith("====") or line.startswith("===") or line.startswith("Data file"):
                                    # End of LLM outputs, try to parse what we have
                                    break
                                # Stop at blank line after we've started collecting JSON
                                if llm_json_lines and not line.strip():
                                    break
                                llm_json_lines.append(line)
                    
                    # Try to parse LLM JSON to extract component
                    if llm_json_lines:
                        try:
                            llm_json_str = "".join(llm_json_lines)
                            llm_output = json.loads(llm_json_str)
                            return llm_output.get("component")
                        except:
                            pass
                    return None
                
                # Try llm_out file first (for passed tests), then error file (for failed tests)
                llm_selected_component = extract_llm_component(llm_out_lines, test_id)
                if not llm_selected_component:
                    llm_selected_component = extract_llm_component(error_lines, test_id)
                
                # Normalize LLM selected component name (replace spaces with hyphens)
                if llm_selected_component:
                    llm_selected_component = llm_selected_component.replace(" ", "-")

                if is_passed:
                    results["passed"] += 1
                    results["by_component"][expected_component]["passed"] += 1
                    results["by_dataset"][dataset_label]["passed"] += 1
                    status = "PASS"
                    error_msg = None
                    
                    # Check for warning: passed but selected different component
                    has_warning = False
                    if llm_selected_component and llm_selected_component != expected_component:
                        has_warning = True
                        results["warnings"] += 1
                    
                    # For ALL passed tests, extract component_choice judge reasoning
                    if llm_selected_component:
                        # Extract component_choice judge feedback from llm_out file (for passed tests)
                        judge_feedback = []
                        in_test_section = False
                        in_component_choice = False
                        
                        for line in llm_out_lines:
                            # Start of this specific test
                            if f"==== DATASET ID {test_id} ====" in line:
                                in_test_section = True
                                in_component_choice = False
                                judge_feedback = []  # Reset for this test
                                continue
                            
                            # End of this test (start of another test)
                            if in_test_section and line.startswith("==== DATASET ID"):
                                break
                            
                            # Only process lines within this test's section
                            if in_test_section:
                                if "component_choice:" in line:
                                    in_component_choice = True
                                    judge_feedback.append(line.strip())
                                elif in_component_choice:
                                    # Continue collecting lines until we hit another judge category or section end
                                    if line.strip().startswith("field_relevance:") or line.startswith("====") or line.startswith("===") or not line.strip():
                                        break
                                    judge_feedback.append(line.strip())
                        
                        if judge_feedback:
                            # Join the component_choice feedback
                            error_msg = " ".join(judge_feedback)
                else:
                    results["failed"] += 1
                    results["by_component"][expected_component]["failed"] += 1
                    results["by_dataset"][dataset_label]["failed"] += 1
                    status = "FAIL"
                    has_warning = False  # Failed tests don't have warnings
                    # Extract error message from error file (AGENT or SYSTEM errors)
                    error_msg = "Unknown error"
                    in_errors_section = False
                    is_system_error = False
                    for line in error_lines:
                        if f"==== AGENT {test_id} ====" in line:
                            in_errors_section = True
                            is_system_error = False
                        elif f"==== SYSTEM {test_id} ====" in line:
                            in_errors_section = True
                            is_system_error = True
                        elif in_errors_section:
                            if is_system_error:
                                # For SYSTEM errors, the error is on the next line
                                if line.strip() and not line.startswith("===="):
                                    error_msg = f"SYSTEM ERROR: {line.strip()}"
                                    break
                            elif line.strip().startswith('"'):
                                # Found error message like "component.invalid: ..."
                                error_msg = line.strip().strip('"').strip(",")
                                break
                            elif line.startswith("===="):
                                break

                # Extract backend_data and LLM output for expandable sections
                backend_data = test.get("backend_data", "")
                
                # Extract full LLM output JSON
                llm_output_json = None
                in_test_section = False
                in_llm_outputs = False
                llm_json_lines = []
                
                # Search in llm_out first, then error files
                search_lines = llm_out_lines if is_passed else error_lines
                for line in search_lines:
                    if f"==== DATASET ID {test_id} ====" in line or f"==== AGENT {test_id} ====" in line:
                        in_test_section = True
                        in_llm_outputs = False
                        llm_json_lines = []
                        continue
                    
                    if in_test_section:
                        if line.startswith("==== DATASET ID") or line.startswith("==== AGENT"):
                            break
                        
                        if "LLM outputs:" in line:
                            in_llm_outputs = True
                            llm_json_lines = []
                            continue
                        
                        if in_llm_outputs:
                            if line.startswith("====") or line.startswith("===") or line.startswith("Data file"):
                                break
                            # Stop at blank line after we've started collecting JSON
                            if llm_json_lines and not line.strip():
                                break
                            llm_json_lines.append(line)
                
                if llm_json_lines:
                    try:
                        llm_output_json = json.loads("".join(llm_json_lines))
                    except:
                        llm_output_json = None
                
                test_detail = {
                    "id": test_id,
                    "prompt": user_prompt,
                    "component": expected_component,
                    "llm_selected": llm_selected_component if llm_selected_component else expected_component,
                    "dataset": dataset_label,
                    "dataset_file": dataset_file.name,
                    "status": status,
                    "error": error_msg,
                    "backend_data": backend_data,
                    "llm_output": llm_output_json,
                    "has_warning": has_warning,
                }
                
                results["test_details"].append(test_detail)
                
                # Add to warning list if it has a warning
                if has_warning:
                    results["warning_tests"].append(test_detail)

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
        tr:not(.details-row):hover {{
            background: #f8f9fa;
        }}
        .details-row:hover {{
            background: #f9f9f9 !important;
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
        .status.warning {{
            background: #fff3cd;
            color: #856404;
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
        
        /* Expandable row styles */
        .test-row {{
            cursor: pointer;
            transition: background-color 0.2s;
        }}
        .test-row:hover {{
            background-color: #f8f9fa;
        }}
        .test-row td {{
            border-bottom: 1px solid #ddd;
        }}
        .toggle-icon {{
            display: inline-block;
            width: 16px;
            font-size: 12px;
            transition: transform 0.3s;
            margin-right: 5px;
        }}
        .toggle-icon.expanded {{
            transform: rotate(90deg);
        }}
        .details-row {{
            background-color: #f9f9f9;
            border-top: none !important;
        }}
        .details-row td {{
            border-top: none !important;
            border-bottom: 2px solid #ddd !important;
            padding: 0 !important;
        }}
        .expandable-content {{
            padding: 12px;
            display: flex;
            gap: 12px;
            flex-wrap: nowrap;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            margin: 8px;
            background-color: #fafafa;
            max-width: calc(100% - 20px);
            overflow: hidden;
        }}
        .data-section {{
            flex: 1;
            min-width: 0;
            max-width: 50%;
            overflow: hidden;
        }}
        .data-section h4 {{
            color: #2c3e50;
            margin-bottom: 8px;
            font-size: 13px;
            font-weight: 600;
            display: flex;
            align-items: center;
        }}
        .json-data {{
            background-color: #282c34;
            color: #abb2bf;
            padding: 8px;
            border-radius: 3px;
            overflow-x: auto;
            overflow-y: auto;
            font-family: 'Courier New', Consolas, monospace;
            font-size: 10px;
            line-height: 1.4;
            max-height: 250px;
            max-width: 100%;
            border: 1px solid #3e4451;
            white-space: pre-wrap;
            word-break: break-word;
            box-sizing: border-box;
        }}
        .json-data::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}
        .json-data::-webkit-scrollbar-track {{
            background: #21252b;
        }}
        .json-data::-webkit-scrollbar-thumb {{
            background: #4b5263;
            border-radius: 3px;
        }}
        .json-data::-webkit-scrollbar-thumb:hover {{
            background: #5c6370;
        }}
        
        /* Responsive: Stack on smaller screens */
        @media (max-width: 1100px) {{
            .expandable-content {{
                flex-wrap: wrap;
            }}
            .data-section {{
                max-width: 100%;
                min-width: 100%;
            }}
        }}
    </style>
    <script>
        function toggleDetails(idx) {{
            const detailsRow = document.getElementById('details-' + idx);
            const toggleIcon = document.getElementById('toggle-' + idx);
            
            if (detailsRow.style.display === 'none') {{
                detailsRow.style.display = 'table-row';
                toggleIcon.classList.add('expanded');
            }} else {{
                detailsRow.style.display = 'none';
                toggleIcon.classList.remove('expanded');
            }}
        }}
    </script>
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
                        <td style="color: #27ae60;">{results["passed"]} tests</td>
                    </tr>
                    <tr>
                        <td><strong>Tests Failed</strong></td>
                        <td style="color: #e74c3c;">{results["failed"]} tests</td>
                    </tr>
                    <tr>
                        <td><strong>Warnings</strong></td>
                        <td style="color: #f39c12;">{results["warnings"]} tests (Passed but selected different component)</td>
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
                        <th>Expected Component</th>
                        <th>LLM Selected Component</th>
                        <th>Status</th>
                        <th>Judge Reasoning</th>
                    </tr>
                </thead>
                <tbody>
"""

    for idx, test in enumerate(results["test_details"]):
        status_class = "pass" if test["status"] == "PASS" else "fail"
        
        # Display status with warning indicator if applicable
        if test.get("has_warning"):
            status_display = 'WARNING'
            status_class = "warning"  # Orange color
        else:
            status_display = test["status"]
        
        # Handle error/feedback cell
        if test["error"]:
            if test["status"] == "PASS" and "component_choice:" in test["error"]:
                # Check if LLM selected the correct component
                if test["llm_selected"] == test["component"]:
                    # Show component choice judge explanation in green for correct selection
                    error_cell = f'<td style="color: #27ae60; font-size: 12px; font-style: italic;">{test["error"]}</td>'
                else:
                    # Show component choice judge explanation in blue for different but acceptable component
                    error_cell = f'<td style="color: #3498db; font-size: 12px; font-style: italic;">{test["error"]}</td>'
            else:
                # Show error in red for failed tests
                error_cell = f'<td class="error">{test["error"]}</td>'
        else:
            error_cell = "<td>-</td>"
        
        # Highlight LLM selected component if different from expected
        llm_selected = test["llm_selected"]
        if llm_selected != test["component"]:
            llm_cell = f'<td style="color: #e74c3c; font-weight: bold;">{llm_selected}</td>'
        else:
            llm_cell = f'<td style="color: #27ae60;">{llm_selected}</td>'
        
        # Prepare backend data and LLM output for expandable section
        backend_data_json = json.dumps(json.loads(test.get("backend_data", "{}")), indent=2) if test.get("backend_data") else "N/A"
        llm_output_json = json.dumps(test.get("llm_output", {}), indent=2) if test.get("llm_output") else "N/A"

        # Escape HTML in JSON to prevent rendering issues
        backend_data_json = backend_data_json.replace('<', '&lt;').replace('>', '&gt;')
        llm_output_json = llm_output_json.replace('<', '&lt;').replace('>', '&gt;')
        
        html += f"""
                    <tr class="test-row" onclick="toggleDetails({idx})">
                        <td><span class="toggle-icon" id="toggle-{idx}">▶</span> {test["id"]}</td>
                        <td class="prompt" title="{test["prompt"]}">{test["prompt"]}</td>
                        <td>{test["component"]}</td>
                        {llm_cell}
                        <td><span class="status {status_class}">{status_display}</span></td>
                        {error_cell}
                    </tr>
                    <tr id="details-{idx}" class="details-row" style="display: none;">
                        <td colspan="6" style="padding: 0;">
                            <div class="expandable-content">
                                <div class="data-section">
                                    <h4>Backend Data (Input)</h4>
                                    <pre class="json-data">{backend_data_json}</pre>
                                </div>
                                <div class="data-section">
                                    <h4>Component Metadata (LLM Output)</h4>
                                    <pre class="json-data">{llm_output_json}</pre>
                                </div>
                            </div>
                        </td>
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
        "--llm-out-dirs",
        default=None,
        help="Comma-separated list of LLM output directories (default: llm_out sibling to errors)",
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

    # Parse llm_out directories  
    llm_out_dirs = None
    if hasattr(args, 'llm_out_dirs') and args.llm_out_dirs:
        llm_out_dirs = [d.strip() for d in args.llm_out_dirs.split(",")]

    print(f"Analyzing evaluation results from {len(dataset_dirs)} dataset(s)...")
    results = analyze_results(dataset_dirs, dataset_labels, error_dirs, llm_out_dirs)

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
