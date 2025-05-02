import getopt
import json
import os
import sys
from pathlib import Path

from ai_eval_components.types import (
    BASE_DATASET_PATH,
    DATASET_FILE_SUFFIX,
    DatasetRow,
    EvalError,
)


def load_args():
    """Load commandline arguments for the eval tool"""
    arg_ui_component = None
    arg_dataset_file = None
    arg_write_llm_output = False
    opts, args = getopt.getopt(sys.argv[1:], "hwc:f:")
    for opt, arg in opts:
        if opt == "-h":
            print("eval.py <arguments>")
            print("\nArguments:")
            print(" -c <ui-component-name> - evaluate only named UI component")
            print(
                " -f <dataset-file-name> - run only evaluations from the named dataset file"
            )
            print(
                " -w - if present then LLM outputs with successful checks are written into files in 'llm_out' directory"
            )
            print(" -h - help")
            sys.exit()
        elif opt in ("-c"):
            arg_ui_component = arg
        elif opt in ("-w"):
            arg_write_llm_output = True
        elif opt in ("-f"):
            arg_dataset_file = arg

    if arg_ui_component:
        print(f"Running evaluations for UI component '{arg_ui_component}' ...")
    else:
        print("Running evaluations for all UI components ...")

    return arg_ui_component, arg_write_llm_output, arg_dataset_file


def assert_array_not_empty(
    value_object,
    value_name: str,
    error_code: str,
    errors: list[EvalError],
    err_msg=None,
):
    """Assert that array value expected under `value_name` in the `value_object` is not empty, add `error_code` into `errors` if it is empty and return `False`"""
    try:
        if isinstance(value_object, dict):
            value = value_object[value_name]
        else:
            value = getattr(value_object, value_name)

        if not value or value is None or len(value) == 0:
            errors.append(
                EvalError(error_code, err_msg if err_msg else f"array is '{value}'")
            )
            return False
        else:
            return True
    except KeyError:
        errors.append(EvalError(error_code, err_msg if err_msg else "array is missing"))
        return False


def assert_str_not_blank(
    value_object,
    value_name: str,
    error_code: str,
    errors: list[EvalError],
    err_msg=None,
):
    """Assert that string value expected under `value_name` in the `value_object` is not a blank string, add `error_code` into `errors` if it is blank and return `False`"""
    try:
        if isinstance(value_object, dict):
            value = value_object[value_name]
        else:
            value = getattr(value_object, value_name)

        if not value or value is None or len(value.strip()) == 0:
            errors.append(
                EvalError(
                    error_code, err_msg if err_msg else f"string value is '{value}'"
                )
            )
            return False
        else:
            return True
    except KeyError:
        errors.append(
            EvalError(error_code, err_msg if err_msg else "string is missing")
        )
        return False


def validate_dataset_row(dsr: DatasetRow):
    """Make sure Dataset row contains everything we need to run evaluation"""
    errors: list[EvalError] = []
    assert_str_not_blank(dsr, "id", "id.missing", errors)
    assert_str_not_blank(
        dsr, "expected_component", "expected_component.missing", errors
    )
    assert_str_not_blank(dsr, "user_prompt", "user_prompt.missing", errors)
    if assert_str_not_blank(dsr, "backend_data", "backend_data.missing", errors):
        try:
            json.loads(dsr["backend_data"])
        except json.JSONDecodeError as e:
            errors.append(EvalError("backend_data.invalid_json", str(e)))
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
