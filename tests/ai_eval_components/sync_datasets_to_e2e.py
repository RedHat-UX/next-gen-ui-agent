#!/usr/bin/env python3
"""
Sync datasets from tests/ai_eval_components to tests/ngui-e2e/client.

This script reads dataset files from:
- tests/ai_eval_components/dataset/
- tests/ai_eval_components/dataset_k8s/

And generates:
- tests/ngui-e2e/client/src/data/inlineDatasets.ts
- tests/ngui-e2e/client/src/quickPrompts.ts

Run this script after regenerating datasets with dataset_gen.py to keep
the e2e client in sync with the evaluation datasets.
"""

import json
import os
from pathlib import Path


def extract_inline_datasets(dataset_dirs):
    """Extract inline datasets from dataset JSON files, ensuring uniqueness by source data file.

    Returns:
        tuple: (list of datasets, mapping from (component_type, data_file) to dataset_id)
    """
    # Track unique datasets by (component_type, data_file) tuple
    # This matches how dataset_gen.py structures datasets - one entry per unique backend data file
    all_datasets = {}
    dataset_id_map = {}  # Map (component_type, data_file) -> dataset_id

    for base_dir, source in dataset_dirs:
        for root, _, files in os.walk(base_dir):
            for file in files:
                if file.endswith(".json"):
                    file_path = Path(root) / file
                    with open(file_path, "r") as f:
                        data = json.load(f)
                        for item in data:
                            component_type = item["expected_component"]

                            # Use src.data_file as the unique key (matches dataset_gen.py structure)
                            src = item.get("src", {})
                            data_file = src.get("data_file", "")

                            # Create unique key from component type and data file path
                            # This ensures one entry per unique backend data file per component type
                            unique_key = (component_type, data_file)

                            # Skip if we've already processed this data file for this component type
                            if unique_key in all_datasets:
                                continue

                            # Parse backend_data string into a JSON object
                            payload_obj = json.loads(item["backend_data"])

                            # Generate a dataset ID from the data file name
                            # Remove path and extension, make it a valid identifier
                            data_file_id = (
                                Path(data_file).stem.replace("-", "_").replace(".", "_")
                            )
                            dataset_id = f"{component_type}_{data_file_id}"

                            # Generate label from data file name (clean up for display)
                            # Convert snake_case or kebab-case to Title Case
                            label = (
                                Path(data_file)
                                .stem.replace("_", " ")
                                .replace("-", " ")
                                .title()
                            )

                            # Get first prompt as description
                            prompt_snippet = item["user_prompt"].split("\n")[0].strip()
                            description = f"Example: '{prompt_snippet}...'"
                            data_type = (
                                f"{component_type}.dataset" if component_type else None
                            )

                            all_datasets[unique_key] = {
                                "id": dataset_id,
                                "label": label,
                                "description": description,
                                "dataType": data_type,
                                "payload": payload_obj,
                            }
                            # Store mapping for quick prompts to reference
                            dataset_id_map[unique_key] = dataset_id

    return list(all_datasets.values()), dataset_id_map


def extract_quick_prompts(dataset_dirs, dataset_id_map):
    """Extract quick prompts from dataset JSON files, referencing datasets by ID."""
    all_prompts = []

    for base_dir, source in dataset_dirs:
        for root, _, files in os.walk(base_dir):
            for file in files:
                if file.endswith(".json"):
                    file_path = Path(root) / file
                    with open(file_path, "r") as f:
                        data = json.load(f)
                        for item in data:
                            prompt_id = item["id"].replace("-", "_")
                            user_prompt = item["user_prompt"]
                            expected_component = item["expected_component"]

                            # Determine category
                            if expected_component == "one-card":
                                category = "one-card"
                            elif expected_component == "set-of-cards":
                                category = "set-of-cards"
                            elif expected_component == "table":
                                category = "tables"
                            elif expected_component in [
                                "chart-bar",
                                "chart-line",
                                "chart-pie",
                                "chart-donut",
                                "chart-mirrored-bar",
                            ]:
                                category = "charts"
                            elif expected_component == "image":
                                category = "image"
                            elif expected_component == "video-player":
                                category = "video-player"
                            else:
                                category = "mixed"

                            # Get dataset ID from the mapping
                            src = item.get("src", {})
                            data_file = src.get("data_file", "")
                            unique_key = (expected_component, data_file)
                            dataset_id = dataset_id_map.get(unique_key)

                            prompt = {
                                "id": prompt_id,
                                "category": category,
                                "prompt": user_prompt,
                                "expectedComponent": expected_component,
                                "source": source,
                            }

                            # Only add dataset reference if we found a matching dataset ID
                            if dataset_id:
                                data_type = (
                                    f"{expected_component}.dataset"
                                    if expected_component
                                    else None
                                )
                                prompt["dataset"] = {
                                    "datasetId": dataset_id,
                                    "dataType": data_type,
                                }

                            all_prompts.append(prompt)

    return all_prompts


def generate_inline_datasets_ts(datasets):
    """Generate TypeScript code for inlineDatasets.ts"""

    header = """// Inline datasets for testing the UI Agent
// This file is auto-generated from tests/ai_eval_components/dataset/ and dataset_k8s/
// To regenerate, run: pants run tests/ai_eval_components/sync_datasets_to_e2e.py

export interface InlineDataset {
  id: string;
  label: string;
  description: string;
  dataType: string;
  payload: any;
}

export const INLINE_DATASETS: InlineDataset[] = [
"""

    entries = []
    for ds in datasets:
        payload_json_str = json.dumps(ds["payload"], indent=6)
        entry = f"""  {{
    id: "{ds["id"]}",
    label: "{ds["label"]}",
    description: "{ds["description"]}",
    dataType: "{ds["dataType"]}",
    payload: {payload_json_str},
  }}"""
        entries.append(entry)

    footer = "];\n"

    return header + ",\n".join(entries) + footer


def generate_quick_prompts_ts(prompts):
    """Generate TypeScript code for quickPrompts.ts"""

    # Sort prompts by category, then by ID
    prompts.sort(key=lambda p: (p["category"], p["id"]))

    # Generate type definitions
    type_def = """// Quick prompt suggestions for testing different component types through the LLM
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
"""

    # Generate prompts array
    current_category = None
    prompts_ts = ""

    for prompt in prompts:
        # Add comment for category changes
        if prompt["category"] != current_category:
            category_names = {
                "one-card": "One Card",
                "set-of-cards": "Set Of Cards",
                "tables": "Tables",
                "charts": "Charts",
                "image": "Image",
                "video-player": "Video Player",
                "mixed": "Mixed",
            }
            prompts_ts += f"  // {category_names[prompt['category']]}\n"
            current_category = prompt["category"]

        # Format prompt entry
        source_value = prompt["source"]
        prompts_ts += f"""  {{
    id: "{prompt["id"]}",
    category: "{prompt["category"]}",
    prompt: {json.dumps(prompt["prompt"])},
    expectedComponent: "{prompt["expectedComponent"]}",
    source: "{source_value}\""""

        # Add dataset reference if present
        if "dataset" in prompt and prompt["dataset"]:
            dataset_id = prompt["dataset"]["datasetId"]
            data_type = prompt["dataset"]["dataType"]
            prompts_ts += f""",
    dataset: {{
      datasetId: "{dataset_id}",
      dataType: {json.dumps(data_type)},
    }}"""
        else:
            # No dataset, just close the object
            prompts_ts += ""

        prompts_ts += "\n  },\n"

    prompts_ts += "];\n\n"

    # Generate grouped prompts by category and source
    grouped_ts = """// Group prompts by category and source, sorted by ID
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
"""

    # Generate helper function
    helper_ts = """
// Get a random prompt from a category
export const getRandomPrompt = (category?: QuickPromptCategory): QuickPrompt => {
  const prompts = category ? quickPrompts.filter(p => p.category === category) : quickPrompts;
  return prompts[Math.floor(Math.random() * prompts.length)];
};
"""

    return type_def + prompts_ts + grouped_ts + helper_ts


if __name__ == "__main__":
    # Define dataset directories with their source labels
    dataset_dirs = [
        ("tests/ai_eval_components/dataset/", "general"),
        ("tests/ai_eval_components/dataset_k8s/", "k8s"),
    ]

    print("=== Syncing datasets to e2e client ===\n")

    # Extract inline datasets
    print("Extracting inline datasets...")
    datasets, dataset_id_map = extract_inline_datasets(dataset_dirs)
    print(f"Found {len(datasets)} inline datasets")

    # Extract quick prompts
    print("Extracting quick prompts...")
    prompts = extract_quick_prompts(dataset_dirs, dataset_id_map)
    print(f"Found {len(prompts)} quick prompts")

    # Generate TypeScript files
    print("\nGenerating TypeScript files...")

    # Generate inlineDatasets.ts
    inline_datasets_ts = generate_inline_datasets_ts(datasets)
    inline_datasets_path = Path("tests/ngui-e2e/client/src/data/inlineDatasets.ts")
    inline_datasets_path.parent.mkdir(parents=True, exist_ok=True)
    with open(inline_datasets_path, "w") as f:
        f.write(inline_datasets_ts)
    print(f"✓ Generated {inline_datasets_path}")

    # Generate quickPrompts.ts
    quick_prompts_ts = generate_quick_prompts_ts(prompts)
    quick_prompts_path = Path("tests/ngui-e2e/client/src/quickPrompts.ts")
    quick_prompts_path.parent.mkdir(parents=True, exist_ok=True)
    with open(quick_prompts_path, "w") as f:
        f.write(quick_prompts_ts)
    print(f"✓ Generated {quick_prompts_path}")

    print("\n=== Sync complete ===")
    print("\nNext steps:")
    print("1. Review the generated files")
    print("2. Commit the changes if they look good")
    print("\nTo regenerate datasets first, run:")
    print("  pants run tests/ai_eval_components/dataset_gen.py")
    print(
        "  pants run tests/ai_eval_components/dataset_gen.py -- -s tests/ai_eval_components/dataset_src_k8s/ -d tests/ai_eval_components/dataset_k8s/"
    )
