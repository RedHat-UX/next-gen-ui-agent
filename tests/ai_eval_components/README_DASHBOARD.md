## Overview

Automated dashboard for comparing model performance across multiple GitLab CI runs.

### Features

- Multi-model comparison
- Trend analysis with Chart.js
- Auto-discovery of recent evaluations
- GitLab Pages integration
- Judge mode support

## How It Works

1. **Run eval.py** → Generate test results
2. **Generate report** → Create `complete_eval_report.html`
3. **Extract metadata** → `save_report_metadata.py` creates `report_metadata.json`
4. **Aggregate** → Fetch reports from multiple CI runs via GitLab API
5. **Dashboard** → Interactive comparison view with charts

## Usage

### Option A: Manual Mode (Specific Job IDs)

```bash
# In GitLab CI/CD Variables, set:
AGGREGATE_JOB_IDS=12345,12346,12347

# Trigger pipeline → Dashboard deployed to GitLab Pages
```

### Option B: Auto Mode (Last N Jobs)

```bash
# Optional: Set limit (default: 10)
AGGREGATE_LIMIT=20

# Run scheduled or manual pipeline
```

## Required Output Files

Your evaluation must produce:

- **`complete_eval_report.html`** - Full HTML evaluation report
- **`report_metadata.json`** - Extracted statistics (auto-generated)

## Scripts Reference

| Script                    | Purpose                                                  |
| ------------------------- | -------------------------------------------------------- |
| `aggregate_reports.py`    | Fetches reports from GitLab API, supports auto-discovery |
| `generate_dashboard.py`   | Creates interactive HTML dashboard with Chart.js         |
| `save_report_metadata.py` | Extracts metadata from HTML reports                      |

## Dashboard Features

- **Overview**: Summary stats, best/worst runs
- **Models**: Per-model performance comparison
- **Trends**: Pass rate over time (separate line per model)
- **Components**: Component-level accuracy breakdown
- **Failures**: Detailed failure analysis with collapsible sections
- **Warnings**: Tests with warnings (Judge mode)
- **Pipeline History**: Clickable links to individual reports

## Configuration Variables

Set in GitLab: **Settings → CI/CD → Variables**

| Variable            | Required | Default      | Description                                    |
| ------------------- | -------- | ------------ | ---------------------------------------------- |
| `AGGREGATE_JOB_IDS` | No       | -            | Comma-separated job IDs for manual mode        |
| `AGGREGATE_LIMIT`   | No       | 10           | Number of recent jobs for auto mode            |
| `AGGREGATION_TOKEN` | No       | CI_JOB_TOKEN | Project access token for cross-pipeline access |

## View Dashboard

After aggregation completes:

```
https://<your-gitlab-instance>/<your-project>/pages/
```

## Troubleshooting

### No jobs found in auto mode

- Verify `generate_report` job creates artifacts
- Ensure at least one successful evaluation run exists

### 401 Unauthorized error

- For cross-project aggregation, create **Project Access Token**
- Set as `AGGREGATION_TOKEN` CI/CD variable with `read_api` scope
