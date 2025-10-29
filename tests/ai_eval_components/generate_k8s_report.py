"""
Generate HTML report for K8s evaluation results.
Usage: python tests/ai_eval_components/generate_k8s_report.py
"""
import json
from pathlib import Path
from datetime import datetime

DATASET_K8S_DIR = Path("tests/ai_eval_components/dataset_k8s")
ERRORS_DIR = Path("tests/ai_eval_components/errors")
REPORT_OUTPUT = Path("tests/ai_eval_components/k8s_eval_report.html")


def load_dataset_file(filepath: Path):
    """Load a dataset JSON file."""
    with filepath.open("r") as f:
        return json.load(f)


def load_error_file(filepath: Path):
    """Load error file if it exists."""
    if filepath.exists():
        with filepath.open("r") as f:
            return f.readlines()
    return []


def analyze_results():
    """Analyze all K8s dataset files and their error reports."""
    results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "by_component": {},
        "test_details": []
    }
    
    # Get all K8s error files (only analyze tests that were actually run)
    error_files = sorted(ERRORS_DIR.glob("*-errors.txt"))
    
    for error_file in error_files:
        # Get corresponding dataset file
        dataset_filename = error_file.name.replace("-errors.txt", ".json")
        dataset_file = DATASET_K8S_DIR / dataset_filename
        
        if not dataset_file.exists():
            continue
            
        dataset = load_dataset_file(dataset_file)
        error_lines = load_error_file(error_file)
        
        # Parse errors to get failed test IDs
        failed_ids = set()
        for line in error_lines:
            if line.startswith("==== AGENT "):
                # Extract test ID from "==== AGENT set-of-cards-000017 ===="
                test_id = line.split("==== AGENT ")[1].split(" ====")[0].strip()
                failed_ids.add(test_id)
        
        component = dataset_file.stem.rsplit("-", 1)[0]  # e.g., "set-of-cards" from "set-of-cards-5"
        
        if component not in results["by_component"]:
            results["by_component"][component] = {
                "total": 0,
                "passed": 0,
                "failed": 0
            }
        
        for test in dataset:
            test_id = test["id"]
            user_prompt = test["user_prompt"]
            expected_component = test["expected_component"]
            
            is_passed = test_id not in failed_ids
            
            results["total_tests"] += 1
            results["by_component"][component]["total"] += 1
            
            if is_passed:
                results["passed"] += 1
                results["by_component"][component]["passed"] += 1
                status = "PASS"
                error_msg = None
            else:
                results["failed"] += 1
                results["by_component"][component]["failed"] += 1
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
                            error_msg = line.strip().strip('"').strip(',')
                            break
                        elif line.startswith("===="):
                            break
            
            results["test_details"].append({
                "id": test_id,
                "prompt": user_prompt,
                "component": expected_component,
                "dataset_file": dataset_file.name,
                "status": status,
                "error": error_msg
            })
    
    return results


def generate_html_report(results):
    """Generate HTML report from results."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    pass_rate = (results["passed"] / results["total_tests"] * 100) if results["total_tests"] > 0 else 0
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>K8s Evaluation Report</title>
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
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 K8s Evaluation Report</h1>
        <div class="timestamp">Generated: {timestamp}</div>
        
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
        
        <div class="component-stats">
            <h2>📊 Results by Component</h2>
            <div class="component-grid">
"""
    
    for component, stats in results["by_component"].items():
        comp_pass_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
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
        
        <div class="test-results">
            <h2>📝 Test Details</h2>
            <table>
                <thead>
                    <tr>
                        <th>Test ID</th>
                        <th>Prompt</th>
                        <th>Component</th>
                        <th>Dataset File</th>
                        <th>Status</th>
                        <th>Error</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    for test in results["test_details"]:
        status_class = "pass" if test["status"] == "PASS" else "fail"
        error_cell = f'<td class="error">{test["error"]}</td>' if test["error"] else '<td>-</td>'
        
        html += f"""
                    <tr>
                        <td>{test["id"]}</td>
                        <td class="prompt" title="{test["prompt"]}">{test["prompt"]}</td>
                        <td>{test["component"]}</td>
                        <td>{test["dataset_file"]}</td>
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
    print("Analyzing K8s evaluation results...")
    results = analyze_results()
    
    print(f"Total tests: {results['total_tests']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    
    print("\nGenerating HTML report...")
    html = generate_html_report(results)
    
    REPORT_OUTPUT.write_text(html)
    print(f"✅ Report generated: {REPORT_OUTPUT}")
    print(f"\nOpen it with: open {REPORT_OUTPUT}")

