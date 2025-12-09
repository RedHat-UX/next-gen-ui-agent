import getopt
import json
import os
import sys
from pathlib import Path

from ai_eval_components.types import BASE_DATASET_PATH, DATASET_FILE_SUFFIX, DatasetRow
from next_gen_ui_agent.data_transform.validation.assertions import assert_str_not_blank
from next_gen_ui_agent.data_transform.validation.types import (
    ComponentDataValidationError,
)


def load_args():
    """Load commandline arguments for the eval tool"""
    arg_ui_component = None
    arg_dataset_file = None
    arg_write_llm_output = False
    arg_vague_component_check = False
    arg_also_warn_only = False
    arg_selected_component_type_check_only = False
    opts, args = getopt.getopt(sys.argv[1:], "hwvosc:f:")
    for opt, arg in opts:
        if opt == "-h":
            print("eval.py <arguments>")
            print("\nArguments:")
            print(" -c <ui-component-name> - evaluate only named UI component")
            print(
                " -f <dataset-file-name> - run only evaluations from the named dataset file"
            )
            print(" -o - if present then `warn_only` dataset items are evaluated also")
            print(
                " -w - if present then LLM outputs with successful checks are written into files in 'llm_out' directory"
            )
            print(
                " -s - if present then only selected component type is checked, not it's configuration - usefull for component selection development/tuning"
            )
            print(
                " -v - if present then component type check is vague, allowing `table` and `set-of-cards` components to be interchanged"
            )
            print(" -h - help")
            sys.exit()
        elif opt in ("-c"):
            arg_ui_component = arg
        elif opt in ("-w"):
            arg_write_llm_output = True
        elif opt in ("-o"):
            arg_also_warn_only = True
        elif opt in ("-s"):
            arg_selected_component_type_check_only = True
        elif opt in ("-v"):
            arg_vague_component_check = True
        elif opt in ("-f"):
            arg_dataset_file = arg

    if not arg_also_warn_only:
        print("Skipping `warn_only` dataset items ...")
    else:
        print("Evaluating `warn_only` dataset items also ...")

    return (
        arg_ui_component,
        arg_write_llm_output,
        arg_dataset_file,
        arg_vague_component_check,
        arg_also_warn_only,
        arg_selected_component_type_check_only,
    )


def select_run_components(arg_ui_component, arg_dataset_file):
    """Select UI components to run for based on configuration"""

    run_components = None
    if arg_ui_component:
        if arg_ui_component != "all":
            run_components = [arg_ui_component]
            print(f"Running evaluations for defined UI component {run_components} ...")
        else:
            print(
                "Running evaluations for all UI components present in the dataset ..."
            )
    elif arg_dataset_file:
        print(
            f"Running evaluations for all UI components from the dataset file '{arg_dataset_file}' ..."
        )
    else:
        print("Running evaluations for all UI components present in the dataset ...")

    return run_components


def validate_dataset_row(dsr: DatasetRow):
    """Make sure Dataset row contains everything we need to run evaluation"""
    errors: list[ComponentDataValidationError] = []
    assert_str_not_blank(dsr, "id", "id.missing", errors)
    assert_str_not_blank(
        dsr, "expected_component", "expected_component.missing", errors
    )
    assert_str_not_blank(dsr, "user_prompt", "user_prompt.missing", errors)
    if assert_str_not_blank(dsr, "backend_data", "backend_data.missing", errors):
        try:
            json.loads(dsr["backend_data"])
        except json.JSONDecodeError as e:
            errors.append(
                ComponentDataValidationError("backend_data.invalid_json", str(e))
            )
    return errors


def load_dataset_file(filepath: Path):
    dataset: list[DatasetRow]

    with filepath.open("r") as f:
        dataset = json.load(f)

    return dataset


def get_dataset_dir():
    dataset_dir_path_config = os.getenv("DATASET_DIR")
    if dataset_dir_path_config:
        dataset_dir_path = Path(dataset_dir_path_config)
    else:
        dataset_dir_path = Path.cwd() / BASE_DATASET_PATH
    print(f"Loading dataset from folder: {dataset_dir_path}")
    return dataset_dir_path


def get_dataset_files(filename: str):
    dataset_dir_path = get_dataset_dir()
    if filename:
        dataset_files = [dataset_dir_path / filename]
    else:
        dataset_files = [
            f
            for f in dataset_dir_path.iterdir()
            if f.is_file() and f.match("*" + DATASET_FILE_SUFFIX)
        ]
        dataset_files.sort()
    return dataset_files
