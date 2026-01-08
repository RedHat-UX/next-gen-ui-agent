#!/usr/bin/env python3
"""
Generate interactive HTML dashboard from aggregated report data.

Usage:
    python generate_dashboard.py --input public/ --output public/index.html
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime


def generate_dashboard_html(aggregated_data: dict, reports: list) -> str:
    """Generate comprehensive HTML dashboard from aggregated data."""
    
    summary = aggregated_data.get("summary", {})
    components = aggregated_data.get("components", {})
    models = aggregated_data.get("models", {})
    trends = aggregated_data.get("trends", [])
    failed_tests = aggregated_data.get("failed_tests", [])
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Start building HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Next Gen UI Agent Evaluation Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            color: #2c3e50;
            line-height: 1.6;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 36px;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            font-size: 16px;
            opacity: 0.9;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px 20px;
        }}
        
        .nav-tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            border-bottom: 2px solid #e0e0e0;
            flex-wrap: wrap;
        }}
        
        .nav-tab {{
            padding: 12px 24px;
            background: white;
            border: none;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
            color: #666;
            border-radius: 8px 8px 0 0;
            transition: all 0.3s;
            border: 2px solid transparent;
            border-bottom: none;
        }}
        
        .nav-tab:hover {{
            background: #f8f9fa;
            color: #667eea;
        }}
        
        .nav-tab.active {{
            background: white;
            color: #667eea;
            border-color: #e0e0e0;
            border-bottom-color: white;
            position: relative;
            bottom: -2px;
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border-left: 4px solid;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .stat-card.blue {{ border-left-color: #3498db; }}
        .stat-card.green {{ border-left-color: #2ecc71; }}
        .stat-card.red {{ border-left-color: #e74c3c; }}
        .stat-card.purple {{ border-left-color: #9b59b6; }}
        .stat-card.orange {{ border-left-color: #f39c12; }}
        
        .stat-card .label {{
            font-size: 14px;
            color: #7f8c8d;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .stat-card .value {{
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .stat-card .subvalue {{
            font-size: 14px;
            color: #95a5a6;
            margin-top: 5px;
        }}
        
        .section {{
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            margin-bottom: 30px;
        }}
        
        .section h2 {{
            font-size: 24px;
            margin-bottom: 20px;
            color: #2c3e50;
            padding-bottom: 10px;
            border-bottom: 2px solid #ecf0f1;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        th {{
            background: #34495e;
            color: white;
            padding: 14px;
            text-align: left;
            font-weight: 600;
            position: sticky;
            top: 0;
        }}
        
        td {{
            padding: 14px;
            border-bottom: 1px solid #ecf0f1;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }}
        
        .badge.success {{ background: #d4edda; color: #155724; }}
        .badge.warning {{ background: #fff3cd; color: #856404; }}
        .badge.danger {{ background: #f8d7da; color: #721c24; }}
        .badge.info {{ background: #d1ecf1; color: #0c5460; }}
        
        .progress-bar {{
            height: 8px;
            background: #ecf0f1;
            border-radius: 4px;
            overflow: hidden;
            margin: 10px 0;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s;
        }}
        
        .model-badge {{
            background: #667eea;
            color: white;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
        }}
        
        .grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }}
        
        .chart-container {{
            position: relative;
            height: 400px;
            margin: 20px 0;
        }}
        
        @media (max-width: 768px) {{
            .grid-2 {{
                grid-template-columns: 1fr;
            }}
            
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Next Gen UI Agent Evaluation - Ask Red Hat</h1>
        <div class="subtitle">Comprehensive Analysis Across {summary.get('total_pipelines', 0)} Pipeline Runs | Generated: {timestamp}</div>
    </div>
    
    <div class="container">
        <!-- Navigation Tabs -->
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="switchTab(event, 'overview')">Overview</button>
            <button class="nav-tab" onclick="switchTab(event, 'components')">Components</button>
            <button class="nav-tab" onclick="switchTab(event, 'models')">Models</button>
            <button class="nav-tab" onclick="switchTab(event, 'trends')">Trends</button>
            <button class="nav-tab" onclick="switchTab(event, 'warnings')">Warnings</button>
            <button class="nav-tab" onclick="switchTab(event, 'failures')">Failures</button>
            <button class="nav-tab" onclick="switchTab(event, 'pipelines')">History</button>
        </div>
        
        <!-- Overview Tab -->
        <div id="overview" class="tab-content active">
            <div class="stats-grid">
                <div class="stat-card blue">
                    <div class="label">Total Pipelines</div>
                    <div class="value">{summary.get('total_pipelines', 0)}</div>
                    <div class="subvalue">Aggregated runs</div>
                </div>
                
                <div class="stat-card green">
                    <div class="label">Total Tests</div>
                    <div class="value">{summary.get('total_tests', 0)}</div>
                    <div class="subvalue">{summary.get('total_passed', 0)} passed ({summary.get('total_warnings', 0)} warnings), {summary.get('total_failed', 0)} failed</div>
                </div>
                
                <div class="stat-card purple">
                    <div class="label">Overall Pass Rate</div>
                    <div class="value">{summary.get('overall_pass_rate', 0):.1f}%</div>
                    <div class="subvalue">Avg: {summary.get('avg_pass_rate', 0):.1f}%</div>
                </div>
                
                <div class="stat-card orange">
                    <div class="label">Components Tested</div>
                    <div class="value">{summary.get('unique_components', 0)}</div>
                    <div class="subvalue">{len(summary.get('models_tested', []))} models used</div>
                </div>
            </div>
            
            <div class="grid-2">
                <div class="section">
                    <h2>Best Performing Run</h2>
                    <div style="padding: 20px;">
                        <div style="font-size: 48px; font-weight: bold; color: #27ae60; margin-bottom: 10px;">
                            {summary.get('best_run', {}).get('pass_rate', 0):.1f}%
                        </div>
                        <div style="font-size: 16px; color: #7f8c8d; margin-bottom: 5px;">
                            <strong>Pipeline:</strong> #{summary.get('best_run', {}).get('pipeline_id', '?')}
                        </div>
                        <div style="font-size: 16px; color: #7f8c8d; margin-bottom: 15px;">
                            <strong>Model:</strong> <span class="model-badge">{summary.get('best_run', {}).get('model', 'Unknown')}</span>
                        </div>
                        <a href="reports/pipeline_{summary.get('best_run', {}).get('pipeline_id', 'unknown')}.html" target="_blank">View Report →</a>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Worst Performing Run</h2>
                    <div style="padding: 20px;">
                        <div style="font-size: 48px; font-weight: bold; color: #e74c3c; margin-bottom: 10px;">
                            {summary.get('worst_run', {}).get('pass_rate', 0):.1f}%
                        </div>
                        <div style="font-size: 16px; color: #7f8c8d; margin-bottom: 5px;">
                            <strong>Pipeline:</strong> #{summary.get('worst_run', {}).get('pipeline_id', '?')}
                        </div>
                        <div style="font-size: 16px; color: #7f8c8d; margin-bottom: 15px;">
                            <strong>Model:</strong> <span class="model-badge">{summary.get('worst_run', {}).get('model', 'Unknown')}</span>
                        </div>
                        <a href="reports/pipeline_{summary.get('worst_run', {}).get('pipeline_id', 'unknown')}.html" target="_blank">View Report →</a>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>Models Tested</h2>
                <div style="display: flex; gap: 15px; flex-wrap: wrap; padding: 20px;">
"""
    
    for model in summary.get('models_tested', []):
        html += f'                    <span class="model-badge" style="padding: 8px 16px; font-size: 14px;">{model}</span>\n'
    
    html += """                </div>
            </div>
        </div>
        
        <!-- Components Tab -->
        <div id="components" class="tab-content">
            <div class="section">
                <h2>Component-Level Analysis</h2>
                
                <table>
                    <thead>
                        <tr>
                            <th>Component</th>
                            <th>Total Tests</th>
                            <th>Accuracy</th>
                            <th>Best Model</th>
                        </tr>
                    </thead>
                    <tbody>
"""
    
    # Sort components by accuracy
    sorted_components = sorted(components.items(), key=lambda x: x[1].get('overall_accuracy', 0), reverse=True)
    
    for component, stats in sorted_components:
        accuracy = stats.get('overall_accuracy', 0)
        accuracy_class = 'success' if accuracy >= 80 else ('warning' if accuracy >= 60 else 'danger')
        
        best_model = stats.get('best_model', ['N/A', 0])
        best_model_name = best_model[0] if isinstance(best_model, (tuple, list)) and len(best_model) >= 2 else 'N/A'
        best_model_acc = best_model[1] if isinstance(best_model, (tuple, list)) and len(best_model) >= 2 else 0
        
        html += f"""                        <tr>
                            <td><strong>{component}</strong></td>
                            <td>{stats.get('total_tests', 0)} <span style="color: #95a5a6;">({stats.get('total_passed', 0)} passed, {stats.get('total_failed', 0)} failed)</span></td>
                            <td>
                                <span class="badge {accuracy_class}">{accuracy:.1f}%</span>
                                <div class="progress-bar" style="width: 150px;">
                                    <div class="progress-fill" style="width: {accuracy}%;"></div>
                                </div>
                            </td>
                            <td><span class="model-badge" style="font-size: 11px;">{best_model_name}</span> ({best_model_acc:.1f}%)</td>
                        </tr>
"""
    
    html += """                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Models Tab -->
        <div id="models" class="tab-content">
            <div class="section">
                <h2>Model Comparison</h2>
                
                <table>
                    <thead>
                        <tr>
                            <th>Model</th>
                            <th>Total Tests</th>
                            <th>Pass Rate</th>
                            <th>Total Runs</th>
                            <th>Best Component</th>
                            <th>Worst Component</th>
                        </tr>
                    </thead>
                    <tbody>
"""
    
    # Sort models by pass rate
    sorted_models = sorted(models.items(), key=lambda x: x[1].get('overall_pass_rate', 0), reverse=True)
    
    for model, stats in sorted_models:
        pass_rate = stats.get('overall_pass_rate', 0)
        pass_rate_class = 'success' if pass_rate >= 80 else ('warning' if pass_rate >= 60 else 'danger')
        
        best_comp = stats.get('best_component', ['N/A', 0])
        worst_comp = stats.get('worst_component', ['N/A', 0])
        
        best_comp_name = best_comp[0] if isinstance(best_comp, (tuple, list)) and len(best_comp) >= 2 else 'N/A'
        best_comp_acc = best_comp[1] if isinstance(best_comp, (tuple, list)) and len(best_comp) >= 2 else 0
        
        worst_comp_name = worst_comp[0] if isinstance(worst_comp, (tuple, list)) and len(worst_comp) >= 2 else 'N/A'
        worst_comp_acc = worst_comp[1] if isinstance(worst_comp, (tuple, list)) and len(worst_comp) >= 2 else 0
        
        html += f"""                        <tr>
                            <td><span class="model-badge">{model}</span></td>
                            <td>{stats.get('total_tests', 0)} <span style="color: #95a5a6;">({stats.get('total_passed', 0)} passed, {stats.get('total_failed', 0)} failed)</span></td>
                            <td>
                                <span class="badge {pass_rate_class}">{pass_rate:.1f}%</span>
                                <div class="progress-bar" style="width: 150px;">
                                    <div class="progress-fill" style="width: {pass_rate}%;"></div>
                                </div>
                            </td>
                            <td>{stats.get('total_runs', 0)}</td>
                            <td>{best_comp_name} <span style="color: #27ae60;">({best_comp_acc:.1f}%)</span></td>
                            <td>{worst_comp_name} <span style="color: #e74c3c;">({worst_comp_acc:.1f}%)</span></td>
                        </tr>
"""
    
    html += """                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Trends Tab -->
        <div id="trends" class="tab-content">
            <div class="section">
                <h2>Pass Rate Trends Over Time</h2>
                <div class="chart-container">
                    <canvas id="trendsChart"></canvas>
                </div>
            </div>
            
            <div class="section">
                <h2>Component Accuracy</h2>
                <div class="chart-container">
                    <canvas id="componentChart"></canvas>
                </div>
            </div>
        </div>
        
        <!-- Warnings Tab -->
        <div id="warnings" class="tab-content">
            <div class="section">
                <h2>Warning Tests Analysis</h2>
                <p style="margin-bottom: 20px; color: #7f8c8d;">
                    Tests that passed but selected a different component than expected. These indicate potential improvements in component selection logic.
                </p>
                
                <table>
                    <thead>
                        <tr>
                            <th style="width: 100px;">Test ID</th>
                            <th style="width: 120px;">Expected</th>
                            <th style="width: 120px;">LLM Selected</th>
                            <th style="width: 80px;">Warning Rate</th>
                            <th>Prompt</th>
                            <th style="width: 50px;"></th>
                        </tr>
                    </thead>
                    <tbody>
"""
    
    warning_tests = aggregated_data.get('warning_tests', [])
    for idx, warning_test in enumerate(warning_tests[:50]):  # Top 50
        warning_rate = warning_test.get('warning_rate', 0)
        prompt_short = warning_test.get('prompt', '')[:60] + '...' if len(warning_test.get('prompt', '')) > 60 else warning_test.get('prompt', '')
        
        # Check if models selected different components
        pipelines = warning_test.get('pipelines', [])
        llm_selected_display = warning_test.get('llm_selected', '?')
        if pipelines:
            selections = [p.get('llm_selected', 'Unknown') for p in pipelines]
            unique_selections = list(set(selections))
            if len(unique_selections) > 1:
                llm_selected_display = f"{len(unique_selections)} different"
        
        html += f"""                        <tr onclick="toggleWarningDetails({idx})" style="cursor: pointer;">
                            <td><code>{warning_test.get('test_id', '?')}</code></td>
                            <td><span style="color: #3498db; font-weight: bold;">{warning_test.get('component', '?')}</span></td>
                            <td><span style="color: #f39c12; font-weight: bold;">{llm_selected_display}</span></td>
                            <td><span class="badge warning">{warning_rate:.0f}%</span></td>
                            <td title="{warning_test.get('prompt', '')}">{prompt_short}</td>
                            <td><span id="warning-toggle-{idx}">▼</span></td>
                        </tr>
                        <tr id="warning-details-{idx}" style="display: none;">
                            <td colspan="6" style="background: #f8f9fa; padding: 15px;">
                                <div style="margin-bottom: 10px;"><strong>Full Prompt:</strong> {warning_test.get('prompt', '')}</div>
                                <div style="margin-bottom: 10px;"><strong>Warning Count:</strong> {warning_test.get('warning_count', 0)} out of {warning_test.get('total_runs', 0)} runs</div>
                                <div style="margin-bottom: 15px;"><strong>Judge Reasoning (from each model):</strong></div>
"""
        
        # Add each model's reasoning with selection + Component Metadata
        pipelines = warning_test.get('pipelines', [])
        for p_idx, pipeline in enumerate(pipelines):
            model = pipeline.get('model', 'Unknown')
            llm_selected_comp = pipeline.get('llm_selected', 'Unknown')
            reason = pipeline.get('judge_reasoning', pipeline.get('reason', 'No reason provided'))[:600]
            llm_output = pipeline.get('llm_output', 'N/A')
            
            html += f"""                                <div style="margin-bottom: 15px; padding: 10px; background: white; border-left: 3px solid #f39c12;">
                                    <div style="font-weight: bold; color: #2c3e50; margin-bottom: 5px;">
                                        Model: {model} <span style="color: #7f8c8d; font-weight: normal; font-size: 0.9em;">→ selected: <span style="color: #f39c12; font-weight: bold;">{llm_selected_comp}</span></span>
                                    </div>
                                    <div style="font-size: 0.9em; color: #555; margin-bottom: 10px;">{reason}{'...' if len(pipeline.get('judge_reasoning', pipeline.get('reason', ''))) > 600 else ''}</div>
                                    
                                    <!-- Component Metadata for this model -->
                                    <div style="margin-top: 10px; padding: 10px; background: #f8f9fa; border-radius: 4px;">
                                        <h4 onclick="toggleSection('warning-llm-{idx}-{p_idx}')" style="color: #2c3e50; margin: 0 0 5px 0; font-size: 0.9em; cursor: pointer; user-select: none;">
                                            <span id="warning-llm-{idx}-{p_idx}-icon">▶</span> Component Metadata (LLM Output)
                                        </h4>
                                        <pre id="warning-llm-{idx}-{p_idx}" style="background: white; padding: 10px; border-radius: 4px; overflow-x: auto; font-size: 0.8em; margin: 0; display: none; max-height: 300px; overflow-y: auto;">{llm_output}</pre>
                                    </div>
                                </div>
"""
        
        # Add Backend Data (ONCE - same for all models) - Collapsible
        backend_data = pipelines[0].get('backend_data', 'N/A') if pipelines else 'N/A'
        
        html += f"""                                <div style="margin-top: 20px; padding: 15px; background: white; border: 1px solid #ddd; border-radius: 4px;">
                                    <h4 onclick="toggleSection('warning-backend-{idx}')" style="color: #2c3e50; margin: 0 0 10px 0; font-size: 1em; cursor: pointer; user-select: none;">
                                        <span id="warning-backend-{idx}-icon">▶</span> Backend Data (Input)
                                    </h4>
                                    <pre id="warning-backend-{idx}" style="background: #f8f9fa; padding: 12px; border-radius: 4px; overflow-x: auto; font-size: 0.85em; margin: 0; display: none; max-height: 400px; overflow-y: auto;">{backend_data}</pre>
                                </div>
                            </td>
                        </tr>
"""
    
    html += """                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Failures Tab -->
        <div id="failures" class="tab-content">
            <div class="section">
                <h2>Failed Tests Analysis</h2>
                <p style="margin-bottom: 20px; color: #7f8c8d;">
                    Tests that failed across multiple runs. Click any row to see detailed information.
                </p>
                
                <table>
                    <thead>
                        <tr>
                            <th style="width: 100px;">Test ID</th>
                            <th style="width: 120px;">Expected</th>
                            <th style="width: 120px;">LLM Selected</th>
                            <th style="width: 80px;">Failure Rate</th>
                            <th>Prompt</th>
                            <th style="width: 50px;"></th>
                        </tr>
                    </thead>
                    <tbody>
"""
    
    for idx, failed_test in enumerate(failed_tests[:50]):  # Top 50
        failure_rate = failed_test.get('failure_rate', 0)
        failure_class = 'danger' if failure_rate > 50 else 'warning'
        
        prompt_short = failed_test.get('prompt', '')[:60] + '...' if len(failed_test.get('prompt', '')) > 60 else failed_test.get('prompt', '')
        
        # Get LLM selected components - show if they differ
        pipelines = failed_test.get('pipelines', [])
        llm_selected = "Unknown"
        
        if pipelines:
            # Collect all unique selections
            selections = [p.get('llm_selected', 'Unknown') for p in pipelines]
            unique_selections = list(set(selections))
            
            if len(unique_selections) == 1:
                # All models selected the same
                llm_selected = unique_selections[0]
            else:
                # Models disagreed - show count
                llm_selected = f"{len(unique_selections)} different"
        
        html += f"""                        <tr onclick="toggleFailureDetails({idx})" style="cursor: pointer;">
                            <td><code>{failed_test.get('test_id', '?')}</code></td>
                            <td><span style="color: #3498db; font-weight: bold;">{failed_test.get('component', '?')}</span></td>
                            <td><span style="color: #e74c3c; font-weight: bold;">{llm_selected}</span></td>
                            <td><span class="badge {failure_class}">{failure_rate:.0f}%</span></td>
                            <td title="{failed_test.get('prompt', '')}">{prompt_short}</td>
                            <td><span id="failure-toggle-{idx}">▼</span></td>
                        </tr>
                        <tr id="failure-details-{idx}" style="display: none;">
                            <td colspan="6" style="background: #f8f9fa; padding: 15px;">
                                <div style="margin-bottom: 10px;"><strong>Full Prompt:</strong> {failed_test.get('prompt', '')}</div>
                                <div style="margin-bottom: 10px;"><strong>Failure Count:</strong> {failed_test.get('failure_count', 0)} out of {failed_test.get('total_runs', 0)} runs</div>
                                <div style="margin-bottom: 15px;"><strong>Error Details (from each model):</strong></div>
"""
        
        # Add each model's error with selection + Component Metadata
        fail_pipelines = failed_test.get('pipelines', [])
        for p_idx, pipeline in enumerate(fail_pipelines):
            model = pipeline.get('model', 'Unknown')
            llm_selected_comp = pipeline.get('llm_selected', 'Unknown')
            error = pipeline.get('error', 'No error message')[:600]
            llm_output = pipeline.get('llm_output', 'N/A')
            
            html += f"""                                <div style="margin-bottom: 15px; padding: 10px; background: white; border-left: 3px solid #e74c3c;">
                                    <div style="font-weight: bold; color: #2c3e50; margin-bottom: 5px;">
                                        Model: {model} <span style="color: #7f8c8d; font-weight: normal; font-size: 0.9em;">→ selected: <span style="color: #e74c3c; font-weight: bold;">{llm_selected_comp}</span></span>
                                    </div>
                                    <div style="font-size: 0.9em; color: #555; margin-bottom: 10px;">{error}{'...' if len(pipeline.get('error', '')) > 600 else ''}</div>
                                    
                                    <!-- Component Metadata for this model -->
                                    <div style="margin-top: 10px; padding: 10px; background: #f8f9fa; border-radius: 4px;">
                                        <h4 onclick="toggleSection('failure-llm-{idx}-{p_idx}')" style="color: #2c3e50; margin: 0 0 5px 0; font-size: 0.9em; cursor: pointer; user-select: none;">
                                            <span id="failure-llm-{idx}-{p_idx}-icon">▶</span> Component Metadata (LLM Output)
                                        </h4>
                                        <pre id="failure-llm-{idx}-{p_idx}" style="background: white; padding: 10px; border-radius: 4px; overflow-x: auto; font-size: 0.8em; margin: 0; display: none; max-height: 300px; overflow-y: auto;">{llm_output}</pre>
                                    </div>
                                </div>
"""
        
        # Add Backend Data (ONCE - same for all models) - Collapsible
        backend_data = fail_pipelines[0].get('backend_data', 'N/A') if fail_pipelines else 'N/A'
        
        html += f"""                                <div style="margin-top: 20px; padding: 15px; background: white; border: 1px solid #ddd; border-radius: 4px;">
                                    <h4 onclick="toggleSection('backend-{idx}')" style="color: #2c3e50; margin: 0 0 10px 0; font-size: 1em; cursor: pointer; user-select: none;">
                                        <span id="backend-{idx}-icon">▶</span> Backend Data (Input)
                                    </h4>
                                    <pre id="backend-{idx}" style="background: #f8f9fa; padding: 12px; border-radius: 4px; overflow-x: auto; font-size: 0.85em; margin: 0; display: none; max-height: 400px; overflow-y: auto;">{backend_data}</pre>
                                </div>
                            </td>
                        </tr>
"""
    
    html += """                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Pipelines Tab -->
        <div id="pipelines" class="tab-content">
            <div class="section">
                <h2>Pipeline History</h2>
                
                <table>
                    <thead>
                        <tr>
                            <th>Pipeline ID</th>
                            <th>Date</th>
                            <th>Model</th>
                            <th>Judge</th>
                            <th>Total Tests</th>
                            <th>Pass Rate</th>
                            <th>Link</th>
                        </tr>
                    </thead>
                    <tbody>
"""
    
    for report in reports:
        pass_rate = report.get('summary', {}).get('pass_rate', 0)
        pass_rate_class = 'success' if pass_rate >= 80 else ('warning' if pass_rate >= 60 else 'danger')
        
        date = report.get('timestamp', '')[:10] if 'timestamp' in report else 'N/A'
        judge = report.get('judge_model', 'None')
        judge_badge = f'<span class="badge info">{judge}</span>' if judge and judge != 'None' else '<span style="color: #95a5a6;">-</span>'
        
        pipeline_id = report.get('pipeline_id', '?')
        
        html += f"""                        <tr>
                            <td><strong>#{pipeline_id}</strong></td>
                            <td>{date}</td>
                            <td><span class="model-badge">{report.get('model', 'Unknown')}</span></td>
                            <td>{judge_badge}</td>
                            <td>{report.get('summary', {}).get('total_tests', 0)}</td>
                            <td><span class="badge {pass_rate_class}">{pass_rate:.1f}%</span></td>
                            <td>
                                <a href="reports/pipeline_{pipeline_id}.html" target="_blank">Report →</a>
                            </td>
                        </tr>
"""
    
    html += f"""                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <script>
        // Tab switching
        function switchTab(event, tabName) {{
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // Remove active from all nav tabs
            document.querySelectorAll('.nav-tab').forEach(navTab => {{
                navTab.classList.remove('active');
            }});
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            
            // Set active nav tab
            event.target.classList.add('active');
        }}
        
        // Toggle expand/collapse for Backend Data and Component Metadata
        function toggleSection(sectionId) {{
            const section = document.getElementById(sectionId);
            const icon = document.getElementById(sectionId + '-icon');
            
            if (section.style.display === 'none') {{
                section.style.display = 'block';
                icon.textContent = '▼';
            }} else {{
                section.style.display = 'none';
                icon.textContent = '▶';
            }}
        }}
        
        // Initialize charts
        const trendsData = {json.dumps(trends)};
        const componentsData = {json.dumps([(name, stats.get('overall_accuracy', 0)) for name, stats in sorted_components])};
        
        // Trends chart - separate line per model
        if (document.getElementById('trendsChart') && trendsData.length > 0) {{
            // Group trends by model (keep all data points, including multiple runs per day)
            const modelTrends = {{}};
            
            trendsData.forEach(d => {{
                const model = d.model || 'Unknown';
                if (!modelTrends[model]) {{
                    modelTrends[model] = [];
                }}
                modelTrends[model].push({{
                    timestamp: d.timestamp,
                    pass_rate: d.pass_rate,
                    pipeline_id: d.pipeline_id
                }});
            }});
            
            // Sort each model's data by timestamp
            Object.values(modelTrends).forEach(runs => {{
                runs.sort((a, b) => a.timestamp.localeCompare(b.timestamp));
            }});
            
            // Color palette for different models
            const colors = [
                {{ border: '#667eea', bg: 'rgba(102, 126, 234, 0.1)' }},   // Purple
                {{ border: '#27ae60', bg: 'rgba(39, 174, 96, 0.1)' }},     // Green
                {{ border: '#e74c3c', bg: 'rgba(231, 76, 60, 0.1)' }},     // Red
                {{ border: '#f39c12', bg: 'rgba(243, 156, 18, 0.1)' }},    // Orange
                {{ border: '#3498db', bg: 'rgba(52, 152, 219, 0.1)' }}     // Blue
            ];
            
            // Create one dataset per model
            const datasets = Object.entries(modelTrends).map(([model, runs], idx) => {{
                const color = colors[idx % colors.length];
                return {{
                    label: model,
                    data: runs.map(r => ({{ x: r.timestamp.substring(0, 16), y: r.pass_rate }})),
                    borderColor: color.border,
                    backgroundColor: color.bg,
                    tension: 0.4,
                    fill: false
                }};
            }});
            
            const ctx = document.getElementById('trendsChart').getContext('2d');
            new Chart(ctx, {{
                type: 'line',
                data: {{
                    datasets: datasets
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            display: true,
                            position: 'top'
                        }},
                        tooltip: {{
                            callbacks: {{
                                title: function(context) {{
                                    return 'Time: ' + context[0].parsed.x;
                                }},
                                label: function(context) {{
                                    return context.dataset.label + ': ' + context.parsed.y.toFixed(1) + '%';
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            max: 100,
                            title: {{
                                display: true,
                                text: 'Pass Rate (%)'
                            }}
                        }},
                        x: {{
                            type: 'category',
                            title: {{
                                display: true,
                                text: 'Date & Time'
                            }}
                        }}
                    }}
                }}
            }});
        }}
        
        // Component chart
        if (document.getElementById('componentChart') && componentsData.length > 0) {{
            const ctx2 = document.getElementById('componentChart').getContext('2d');
            new Chart(ctx2, {{
                type: 'bar',
                data: {{
                    labels: componentsData.map(d => d[0]),
                    datasets: [{{
                        label: 'Accuracy (%)',
                        data: componentsData.map(d => d[1]),
                        backgroundColor: 'rgba(102, 126, 234, 0.6)',
                        borderColor: '#667eea',
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            display: false
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            max: 100
                        }}
                    }}
                }}
            }});
        }}
        
        function toggleWarningDetails(idx) {{
            const detailsRow = document.getElementById('warning-details-' + idx);
            const toggle = document.getElementById('warning-toggle-' + idx);
            if (detailsRow.style.display === 'none') {{
                detailsRow.style.display = 'table-row';
                toggle.textContent = '▲';
            }} else {{
                detailsRow.style.display = 'none';
                toggle.textContent = '▼';
            }}
        }}
        
        function toggleFailureDetails(idx) {{
            const detailsRow = document.getElementById('failure-details-' + idx);
            const toggle = document.getElementById('failure-toggle-' + idx);
            if (detailsRow.style.display === 'none') {{
                detailsRow.style.display = 'table-row';
                toggle.textContent = '▲';
            }} else {{
                detailsRow.style.display = 'none';
                toggle.textContent = '▼';
            }}
        }}
    </script>
</body>
</html>
"""
    
    return html


def main():
    parser = argparse.ArgumentParser(description="Generate dashboard HTML from aggregated data")
    parser.add_argument(
        "--input",
        default="public",
        help="Input directory with aggregated_data.json (default: public)"
    )
    parser.add_argument(
        "--output",
        default="public/index.html",
        help="Output HTML file path (default: public/index.html)"
    )
    
    args = parser.parse_args()
    
    input_dir = Path(args.input)
    
    # Load aggregated data
    data_file = input_dir / "aggregated_data.json"
    reports_file = input_dir / "all_reports.json"
    
    if not data_file.exists():
        print(f"ERROR: {data_file} not found")
        print(f"Run aggregate_reports.py first to generate aggregated data.")
        return 1
    
    print(f"Loading aggregated data from {data_file}...")
    
    with data_file.open("r") as f:
        aggregated_data = json.load(f)
    
    with reports_file.open("r") as f:
        reports = json.load(f)
    
    print(f"Found {len(reports)} report(s)")
    print(f"Generating dashboard...")
    
    # Generate HTML
    html = generate_dashboard_html(aggregated_data, reports)
    
    # Save HTML
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html)
    
    print(f"SUCCESS: Dashboard generated: {output_path.absolute()}")
    print(f"\nOpen it with: open {output_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

