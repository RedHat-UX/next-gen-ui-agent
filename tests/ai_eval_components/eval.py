import asyncio
import getopt
import json
import os
import sys
from io import TextIOWrapper
from pathlib import Path

from ai_eval_components.types import DatasetRow, DatasetRowAgentEvalResult, EvalError
from llama_stack_client import LlamaStackClient
from next_gen_ui_agent import AgentInput, InputData, NextGenUIAgent
from next_gen_ui_agent.types import UIComponentMetadata
from next_gen_ui_llama_stack.llama_stack_inference import LlamaStackAgentInference

INFERENCE_MODEL_DEFAULT = "llama3.2:latest"
# INFERENCE_MODEL='granite3.1-dense:2b'
LLAMA_STACK_HOST_DEFAULT = "localhost"
LLAMA_STACK_PORT_DEFAULT = "5001"

ERR_FILE_SUFFIX = "-errors.txt"
DATASET_FILE_SUFFIX = ".json"


def init_infrastructure():
    host = os.getenv("LLAMA_STACK_HOST", default=LLAMA_STACK_HOST_DEFAULT)
    port = os.getenv("LLAMA_STACK_PORT", default=LLAMA_STACK_PORT_DEFAULT)
    base_url = f"http://{host}:{port}"

    model = os.getenv("INFERENCE_MODEL", default=INFERENCE_MODEL_DEFAULT)

    print(f"Creating UI Agent with LlamaStack host={base_url} and LLM={model}")

    client = LlamaStackClient(
        base_url=base_url,
    )
    global inference, ngui_agent
    inference = LlamaStackAgentInference(client, model)
    ngui_agent = NextGenUIAgent()


def call_agent(user_prompt: str, data: str):
    """Call UI agent to generate component JSON"""

    input_data = InputData(id="myid", data=data)

    input = AgentInput(user_prompt=user_prompt, input_data=[input_data])
    components = asyncio.run(
        ngui_agent.component_selection(  # type: ignore
            inference=inference,  # type: ignore
            input=input,
        )
    )
    # load data so we can evaluate that pointers are correct
    components = ngui_agent.data_transformation([input_data], components)  # type: ignore
    return components[0]


def check_result_explicit(
    component: UIComponentMetadata, errors: list[EvalError], dsr: DatasetRow
):
    """
    Perform explicit checks on the component JSON
    * attributes are not empty
    * component is of the expected type
    * data pointers point to the fields existing in the data and are of expected type (array of values or simple value)

    Return list of errors or empty list if everything is OK.
    """

    assert_str_not_blank(component, "title", "title.empty", errors)
    if assert_str_not_blank(component, "component", "component.empty", errors):
        ds_expected_component = dsr["expected_component"]
        generated_component = component["component"]
        if generated_component != ds_expected_component:
            errors.append(
                EvalError(
                    "component.invalid",
                    f"{generated_component} instead of {ds_expected_component}",
                )
            )

    if assert_array_not_empty(component, "fields", "fields.empty", errors):
        for i, field in enumerate(component["fields"]):
            fn = f"fields[{i}]."
            assert_str_not_blank(field, "name", fn + "name.empty", errors)

            if assert_str_not_blank(field, "data_path", fn + "data_path.empty", errors):
                data_path = field["data_path"]
                assert_array_not_empty(
                    field,
                    "data",
                    fn + "data_path.points_no_data",
                    errors,
                    err_msg=f"No value found in data for data_path='{data_path}'",
                )


def assert_array_not_empty(
    value_object,
    value_name: str,
    error_code: str,
    errors: list[EvalError],
    err_msg=None,
):
    """Assert that array value expected under `value_name` in the `value_object` is not empty, add `error_code` into `errors` if it is empty and return `False`"""
    try:
        value = value_object[value_name]

        if not value or len(value) == 0:
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
        value = value_object[value_name]
        if not value or len(value.strip()) == 0:
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


def evaluate_agent_for_dataset_row(dsr: DatasetRow):
    errors: list[EvalError] = []
    try:
        component = call_agent(dsr["user_prompt"], dsr["backend_data"])

        check_result_explicit(component, errors, dsr)

        # TODO NGUI-116 LLM-as-a-judge AI check

    except json.JSONDecodeError as e:
        errors.append(EvalError("invalid_json", "LLM produced invalid JSON: " + str(e)))

    return DatasetRowAgentEvalResult(component, errors)


def validate_dataset_row(dsr: DatasetRow):
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


def console_handle_progress_dot(is_dot: bool):
    if is_dot:
        print()
    return False


def get_dataset_dir():
    dataset_dir_path_config = os.getenv("DATASET_DIR")
    if dataset_dir_path_config:
        dataset_dir_path = Path(dataset_dir_path_config)
    else:
        dataset_dir_path = Path.cwd() / "tests/ai_eval_components/dataset/"
    print(f"Loading dataset from folder: {dataset_dir_path}")
    return dataset_dir_path


def get_dataset_files(DATASET_FILE_SUFFIX, get_dataset_dir):
    dataset_dir_path = get_dataset_dir()
    dataset_files = [
        f
        for f in dataset_dir_path.iterdir()
        if f.is_file() and f.match("*" + DATASET_FILE_SUFFIX)
    ]
    dataset_files.sort()
    return dataset_files


def get_errors_dir():
    errors_dir_path_config = os.getenv("ERRORS_DIR")
    if errors_dir_path_config:
        errors_dir_path = Path(errors_dir_path_config)
    else:
        errors_dir_path = Path.cwd() / "tests/ai_eval_components/errors/"
    if not errors_dir_path.exists():
        errors_dir_path.mkdir(parents=True)
    else:
        [
            f.unlink()
            for f in errors_dir_path.iterdir()
            if f.is_file() and f.match("*" + ERR_FILE_SUFFIX)
        ]
    print(f"Writing errors into folder: {errors_dir_path}")
    return errors_dir_path


def get_component_to_test():
    arg_ui_component = None
    opts, args = getopt.getopt(sys.argv[1:], "hc:")
    for opt, arg in opts:
        if opt == "-h":
            print("test.py -c <ui-component-to-test>")
            sys.exit()
        elif opt in ("-c"):
            arg_ui_component = arg

    if arg_ui_component:
        print(f"Running evaluations for UI component '{arg_ui_component}' ...")
    else:
        print("Running evaluations for all UI components ...")
    return arg_ui_component


def report_err_sys(f_err: TextIOWrapper, id: str, e: Exception):
    print(f"{id} - ERROR SYSTEM {type(e).__name__} - {e}")
    f_err.write(f"==== SYSTEM {id} ====\n")
    f_err.write(f"{type(e).__name__} - {e}\n")
    f_err.write("\n\n")
    f_err.flush()


def report_err_uiagent(
    f_err: TextIOWrapper, id: str, eval_result: DatasetRowAgentEvalResult
):
    print(f"{id} - ERROR UIAGENT {eval_result.errors}")
    f_err.write(f"==== AGENT {id} ====\n")
    json.dump(
        json.loads(str(eval_result.errors)), f_err, indent=2, separators=(",", ": ")
    )
    f_err.write("\nAgent output:\n")
    json.dump(eval_result.component, f_err, indent=2, separators=(",", ": "))
    f_err.write("\n\n")
    f_err.flush()


def report_err_dataset(f_err: TextIOWrapper, id: str, ds_errors: list[EvalError]):
    print(f"{id} - ERROR DATASET {ds_errors}")
    f_err.write(f"==== DATASET {id} ====\n")
    json.dump(json.loads(str(ds_errors)), f_err, indent=2, separators=(",", ": "))
    f_err.write("\n\n")
    f_err.flush()


if __name__ == "__main__":
    arg_ui_component = get_component_to_test()
    errors_dir_path = get_errors_dir()

    dataset_files = get_dataset_files(DATASET_FILE_SUFFIX, get_dataset_dir)

    init_infrastructure()

    num_evals = 0
    num_err_ds = 0
    num_err_agent = 0
    num_err_system = 0

    for dataset_file in dataset_files:
        dataset = load_dataset_file(dataset_file)

        if arg_ui_component:
            dataset = [
                f for f in dataset if f["expected_component"] == arg_ui_component
            ]
        # skip dataset files not containing any record
        if len(dataset) == 0:
            break

        print(f"\n==== Processing {dataset_file.name} ====")
        f_err = (
            errors_dir_path
            / dataset_file.name.replace(DATASET_FILE_SUFFIX, ERR_FILE_SUFFIX)
        ).open("a")
        try:
            i = 0
            is_progress_dot = False
            for dsr in dataset:
                num_evals += 1
                id = dsr["id"]

                # show progress
                i += 1
                if i % 5 == 0:
                    print(".", end="", flush=True)
                    is_progress_dot = True

                try:
                    ds_errors = validate_dataset_row(dsr)

                    if len(ds_errors) > 0:
                        is_progress_dot = console_handle_progress_dot(is_progress_dot)
                        report_err_dataset(f_err, id, ds_errors)
                        num_err_ds += 1
                    else:
                        eval_result = evaluate_agent_for_dataset_row(dsr)
                        if len(eval_result.errors) > 0:
                            is_progress_dot = console_handle_progress_dot(
                                is_progress_dot
                            )
                            report_err_uiagent(f_err, id, eval_result)
                            num_err_agent += 1

                except Exception as e:
                    report_err_sys(f_err, id, e)
                    num_err_system += 1
        finally:
            f_err.close()

    print("\nEvaluations finished:")
    print(f"Dataset items evalueated: {num_evals}")
    print(f"Agent errors: {num_err_agent}")
    print(f"System errors: {num_err_system}")
    print(f"Dataset errors: {num_err_ds}")
