#!/usr/bin/env python3
"""
Save report metadata after generating report.
This creates the metadata JSON needed for aggregation.

Run this after generate_report.py completes.
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


def extract_full_metadata_from_html(html_path):
    """Extract complete test statistics from the generated HTML report including components, failures, warnings."""

    try:
        with open(html_path, "r") as f:
            html_content = f.read()

        result = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "by_component": {},
            "failed_tests": [],
            "warning_tests": [],
        }

        # Extract summary stats
        total_match = re.search(
            r"<td><strong>Total Tests Executed</strong></td>\s*<td>(\d+) tests</td>",
            html_content,
        )
        passed_match = re.search(
            r"<td><strong>Tests Passed</strong></td>\s*<td[^>]*>(\d+) tests</td>",
            html_content,
        )
        failed_match = re.search(
            r"<td><strong>Tests Failed</strong></td>\s*<td[^>]*>(\d+) tests</td>",
            html_content,
        )
        warnings_match = re.search(
            r"<td><strong>Warnings</strong></td>\s*<td[^>]*>(\d+) tests", html_content
        )

        if total_match:
            result["total_tests"] = int(total_match.group(1))
        if passed_match:
            result["passed"] = int(passed_match.group(1))
        if failed_match:
            result["failed"] = int(failed_match.group(1))
        if warnings_match:
            result["warnings"] = int(warnings_match.group(1))

        # Extract component-level stats
        component_pattern = r"<td><strong>([^<]+)</strong></td>\s*<td>(\d+)</td>\s*<td[^>]*>(\d+)</td>\s*<td[^>]*>(\d+)</td>\s*<td><span[^>]*>([\d.]+)%</span></td>"
        for match in re.finditer(component_pattern, html_content):
            comp_name, total, passed, failed, accuracy = match.groups()
            result["by_component"][comp_name] = {
                "total": int(total),
                "passed": int(passed),
                "failed": int(failed),
                "accuracy": float(accuracy),
            }

        # Extract test rows with their details sections
        # Match each test row and find its corresponding backend_data section
        test_row_pattern = r'<tr class="test-row"[^>]*>.*?<span class="toggle-icon"[^>]*>▶</span>\s*([^<]+)</td>.*?</tr>\s*<tr[^>]*class="details-row"[^>]*>.*?<h4>Backend Data \(Input\)</h4>\s*<pre class="json-data">([^<]*)</pre>.*?<h4>Component Metadata \(LLM Output\)</h4>\s*<pre class="json-data">([^<]*)</pre>'

        # Build a map of test_id -> (backend_data, llm_output)
        test_data_map = {}
        for match in re.finditer(test_row_pattern, html_content, re.DOTALL):
            test_id = match.group(1).strip()
            backend_data = match.group(2).strip() if match.group(2) else ""
            llm_output = match.group(3).strip() if match.group(3) else ""
            test_data_map[test_id] = (backend_data, llm_output)

        # Extract failed tests
        fail_pattern = r'<td><span class="toggle-icon"[^>]*>▶</span>\s*([^<]+)</td>\s*<td class="prompt"[^>]*>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td[^>]*>([^<]+)</td>\s*<td><span class="status fail">FAIL</span></td>\s*<td class="error">([^<]+)</td>'
        for match in re.finditer(fail_pattern, html_content):
            test_id, prompt, expected, llm_selected, error = match.groups()
            test_id = test_id.strip()

            # Get backend_data and llm_output from map
            backend_data, llm_output = test_data_map.get(test_id, ("", ""))

            result["failed_tests"].append(
                {
                    "id": test_id,
                    "prompt": prompt.strip(),
                    "component": expected.strip(),
                    "llm_selected": llm_selected.strip(),
                    "error": error.strip(),
                    "backend_data": backend_data,
                    "llm_output": llm_output,
                }
            )

        # Extract warning tests (status = WARNING in HTML)
        warning_pattern = r'<td><span class="toggle-icon"[^>]*>▶</span>\s*([^<]+)</td>\s*<td class="prompt"[^>]*>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td[^>]*>([^<]+)</td>\s*<td><span class="status warning">WARNING</span></td>\s*<td[^>]*>([^<]+)</td>'
        for match in re.finditer(warning_pattern, html_content):
            test_id, prompt, expected, llm_selected, reason = match.groups()
            test_id = test_id.strip()

            # Get backend_data and llm_output from map
            backend_data, llm_output = test_data_map.get(test_id, ("", ""))

            result["warning_tests"].append(
                {
                    "id": test_id,
                    "prompt": prompt.strip(),
                    "component": expected.strip(),
                    "llm_selected": llm_selected.strip(),
                    "judge_reasoning": reason.strip(),
                    "backend_data": backend_data,
                    "llm_output": llm_output,
                }
            )

        # Extract model names from HTML
        model_match = re.search(
            r"<strong>.*?Agent Model.*?</strong></td>\s*<td>([^<]+)</td>",
            html_content,
            re.IGNORECASE,
        )
        judge_match = re.search(
            r"<strong>.*?Judge Model.*?</strong></td>\s*<td>([^<]+)</td>",
            html_content,
            re.IGNORECASE,
        )

        if model_match:
            result["model"] = model_match.group(1).strip()
        if judge_match:
            result["judge_model"] = judge_match.group(1).strip()

        return result
    except Exception as e:
        print(f"Warning: Could not extract full metadata from HTML: {e}")
        import traceback

        traceback.print_exc()
        return None


def create_metadata():
    """Create metadata JSON from environment variables and generated report."""

    # Get environment variables
    pipeline_id = os.getenv("CI_PIPELINE_ID", "unknown")
    job_id = os.getenv("CI_JOB_ID", "unknown")
    commit_sha = os.getenv("CI_COMMIT_SHA", "unknown")
    model = os.getenv("INFERENCE_MODEL", "Unknown")
    judge_enabled = os.getenv("JUDGE_ENABLED", "false") == "true"
    judge_model = os.getenv("JUDGE_MODEL") if judge_enabled else None

    # Try to extract full statistics from generated HTML report
    html_path = Path("tests/ai_eval_components/gitlab_eval_report.html")
    extracted = (
        extract_full_metadata_from_html(html_path) if html_path.exists() else None
    )

    if extracted:
        # Use extracted model names if available (more accurate than env vars)
        if "model" in extracted:
            model = extracted["model"]
        if "judge_model" in extracted:
            judge_model = extracted["judge_model"]
            judge_enabled = True

        summary = {
            "total_tests": extracted["total_tests"],
            "passed": extracted["passed"],
            "failed": extracted["failed"],
            "warnings": extracted["warnings"],
            "pass_rate": (
                (extracted["passed"] / extracted["total_tests"] * 100)
                if extracted["total_tests"] > 0
                else 0.0
            ),
        }
        by_component = extracted.get("by_component", {})
        failed_tests = extracted.get("failed_tests", [])
        warning_tests = extracted.get("warning_tests", [])
    else:
        summary = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "pass_rate": 0.0,
        }
        by_component = {}
        failed_tests = []
        warning_tests = []

    metadata = {
        "timestamp": datetime.now().isoformat(),
        "pipeline_id": pipeline_id,
        "job_id": job_id,
        "commit_sha": commit_sha,
        "model": model,
        "judge_enabled": judge_enabled,
        "judge_model": judge_model,
        "summary": summary,
        "by_component": by_component,
        "failed_tests": failed_tests,
        "warning_tests": warning_tests,
        "by_dataset": {},
    }

    return metadata


def main():
    print("=" * 70)
    print("Next Gen UI Agent - Saving Report Metadata")
    print("=" * 70)

    # Create metadata
    metadata = create_metadata()

    # Save to file in tests/ai_eval_components/ directory
    metadata_file = Path("tests/ai_eval_components/report_metadata.json")

    with metadata_file.open("w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nMetadata saved: {metadata_file.resolve()}")
    print(f"  Pipeline ID: {metadata['pipeline_id']}")
    print(f"  Job ID: {metadata['job_id']}")
    print(f"  Model: {metadata['model']}")
    print(
        f"  Judge: {('Enabled (' + str(metadata['judge_model']) + ')') if metadata['judge_enabled'] and metadata['judge_model'] else 'Disabled'}"
    )
    print(f"  Components: {len(metadata['by_component'])}")
    print(f"  Failed Tests: {len(metadata['failed_tests'])}")
    print(f"  Warning Tests: {len(metadata['warning_tests'])}")
    print(
        f"  Summary: {metadata['summary']['passed']}/{metadata['summary']['total_tests']} passed"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
