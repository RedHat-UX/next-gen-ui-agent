"""
K8s-specific evaluation script.
This script runs evaluations using the K8s dataset (dataset_k8s/).
Usage: python tests/ai_eval_components/eval_k8s.py [same args as eval.py]
"""
import os
import sys
import runpy

# Set the K8s dataset directory before running eval
os.environ["DATASET_DIR"] = "tests/ai_eval_components/dataset_k8s"
# Set separate errors directory for K8s to avoid conflicts with Velias's tests
os.environ["ERRORS_DIR"] = "tests/ai_eval_components/errors_k8s"

if __name__ == "__main__":
    # Run eval.py in this context (with DATASET_DIR set)
    runpy.run_module("ai_eval_components.eval", run_name="__main__")

