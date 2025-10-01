import json
import os
import sys
from io import TextIOWrapper
from pathlib import Path
from typing import Any

from ai_eval_components.types import (
    BASE_MODULE_PATH,
    DATASET_FILE_SUFFIX,
    DatasetRow,
    DatasetRowAgentEvalResult,
)
from next_gen_ui_agent.data_transform.validation.types import (
    ComponentDataValidationError,
)

ERR_FILE_SUFFIX = "-errors.txt"

eval_stats = {
    "num_evals": 0,
    "num_err_ds": 0,
    "num_err_agent": 0,
    "num_err_system": 0,
    "num_warn_agent": 0,
}
eval_stats_by_component: dict[str, Any] = {}


def report_success(
    f_out: TextIOWrapper,
    eval_result: DatasetRowAgentEvalResult,
    dsr: DatasetRow,
    arg_write_llm_output: bool,
):
    """Report successfull eval"""
    eval_stats["num_evals"] += 1
    stats_by_component_add_success(dsr["expected_component"])
    if arg_write_llm_output:
        id = dsr["id"]
        f_out.write(f"==== DATASET ID {id} ====\n")
        f_out.write("Prompt:\n")
        f_out.write(dsr["user_prompt"])
        if "input_data_type" in dsr and dsr["input_data_type"]:
            f_out.write("\nInput data type: ")
            f_out.write(dsr["input_data_type"])
        f_out.write("\nLLM outputs:\n")
        for llm_output in eval_result.llm_output:
            try:
                json.dump(
                    json.loads(llm_output), f_out, indent=2, separators=(",", ": ")
                )
                f_out.write("\n")
            except Exception:
                # write LLM output even if it is an invalid JSON
                f_out.write(llm_output + "\n")
        if eval_result.data:
            f_out.write(
                "\nComponent data:\n" + eval_result.data.model_dump_json(indent=2)
            )
        if "src" in dsr and "data_file" in dsr["src"]:
            ov = dsr["src"]["data_file"]
            f_out.write(f"\nData file in dataset_src: {ov}")
        f_out.write("\n\n")
        f_out.flush()


def report_err_dataset(
    f_err: TextIOWrapper,
    ds_errors: list[ComponentDataValidationError],
    dsr: DatasetRow,
    is_progress_dot: bool,
):
    """Report dataset error"""
    eval_stats["num_evals"] += 1
    eval_stats["num_err_ds"] += 1

    is_progress_dot = console_handle_progress_dot(is_progress_dot)
    id = dsr["id"]
    print(f"{id} - ERROR DATASET {ds_errors}")
    f_err.write(f"==== DATASET {id} ====\n")
    json.dump(json.loads(str(ds_errors)), f_err, indent=2, separators=(",", ": "))
    f_err.write("\n\n")
    f_err.flush()

    return is_progress_dot


def report_err_uiagent(
    f_err: TextIOWrapper,
    eval_result: DatasetRowAgentEvalResult,
    dsr: DatasetRow,
    is_progress_dot: bool,
):
    warn = False if "warn_only" not in dsr else dsr["warn_only"]

    """Report UI Agent error"""
    eval_stats["num_evals"] += 1
    if warn:
        stats_by_component_add_warn_agent(dsr["expected_component"])
        eval_stats["num_warn_agent"] += 1
    else:
        stats_by_component_add_err_agent(dsr["expected_component"])
        eval_stats["num_err_agent"] += 1

    is_progress_dot = console_handle_progress_dot(is_progress_dot)
    id = dsr["id"]
    if warn:
        print(f"{id} - WARN UIAGENT {eval_result.errors}")
    else:
        print(f"{id} - ERROR UIAGENT {eval_result.errors}")
    f_err.write(f"==== AGENT {id} ====\n")
    if warn:
        f_err.write("Warnings:\n")
    else:
        f_err.write("Errors:\n")
    json.dump(
        json.loads(str(eval_result.errors)), f_err, indent=2, separators=(",", ": ")
    )
    f_err.write("\nPrompt:\n")
    f_err.write(dsr["user_prompt"])
    if "input_data_type" in dsr and dsr["input_data_type"]:
        f_err.write("\nInput data type: ")
        f_err.write(dsr["input_data_type"])
    f_err.write("\nLLM outputs:\n")
    for llm_output in eval_result.llm_output:
        try:
            json.dump(json.loads(llm_output), f_err, indent=2, separators=(",", ": "))
            f_err.write("\n")
        except Exception:
            # write LLM output even if it is an invalid JSON
            f_err.write(llm_output + "\n")
    if eval_result.data:
        f_err.write("\nComponent data:\n" + eval_result.data.model_dump_json(indent=2))
    if "src" in dsr and "data_file" in dsr["src"]:
        ov = dsr["src"]["data_file"]
        f_err.write(f"\nData file in dataset_src: {ov}")
    f_err.write("\n\n")
    f_err.flush()

    return is_progress_dot


def report_err_sys(
    f_err: TextIOWrapper, e: Exception, dsr: DatasetRow, is_progress_dot: bool
):
    """Report system error/exception"""
    eval_stats["num_evals"] += 1
    stats_by_component_add_err_system(dsr["expected_component"])
    eval_stats["num_err_system"] += 1

    is_progress_dot = console_handle_progress_dot(is_progress_dot)
    id = dsr["id"]
    print(f"{id} - ERROR SYSTEM {type(e).__name__} - {e}")
    f_err.write(f"==== SYSTEM {id} ====\n")
    f_err.write(f"{type(e).__name__} - {e}\n")
    f_err.write("\n\n")
    f_err.flush()

    return is_progress_dot


def print_stats():
    """Print eval stats to the stdout"""
    print(f"Dataset items evalueated: {eval_stats['num_evals']}")
    print(f"Agent errors: {eval_stats['num_err_agent']}")
    print(f"Agent warnings: {eval_stats['num_warn_agent']}")
    print(f"System errors: {eval_stats['num_err_system']}")
    print(f"Dataset errors: {eval_stats['num_err_ds']}")
    print("Results by component:")
    json.dump(eval_stats_by_component, sys.stdout, indent=2, separators=(",", ": "))
    print("")


def init_agent_out_stream(
    arg_write_llm_output: bool, llm_output_dir_path: Path, dataset_file: Path
):
    if arg_write_llm_output:
        return (
            llm_output_dir_path / dataset_file.name.replace(DATASET_FILE_SUFFIX, ".txt")
        ).open("a")
    else:
        return None


def get_stats_by_component(component: str):
    if component not in eval_stats_by_component:
        eval_stats_by_component[component] = {
            "num_evals": 0,
            "num_err_agent": 0,
            "num_err_system": 0,
            "num_warn_agent": 0,
        }
    return eval_stats_by_component[component]


def stats_by_component_add_success(component: str):
    sbc = get_stats_by_component(component)
    sbc["num_evals"] += 1
    return sbc


def stats_by_component_add_err_agent(component: str):
    sbc = stats_by_component_add_success(component)
    sbc["num_err_agent"] += 1


def stats_by_component_add_warn_agent(component: str):
    sbc = stats_by_component_add_success(component)
    sbc["num_warn_agent"] += 1


def stats_by_component_add_err_system(component: str):
    sbc = stats_by_component_add_success(component)
    sbc["num_err_system"] += 1


def console_print_progress_dot(i: int, is_dot: bool):
    i += 1
    if i % 2 == 0:
        print(".", end="", flush=True)
        is_dot = True
    return i, is_dot


def console_handle_progress_dot(is_dot: bool):
    if is_dot:
        print()
    return False


def get_llm_output_dir(arg_write_llm_output: bool):
    if not arg_write_llm_output:
        return None

    llm_output_dir_path = Path.cwd() / (BASE_MODULE_PATH + "llm_out/")
    if not llm_output_dir_path.exists():
        llm_output_dir_path.mkdir(parents=True)
    else:
        for f in llm_output_dir_path.iterdir():
            if f.is_file():
                f.unlink()
    print(f"Writing successfull LLM outputs into folder: {llm_output_dir_path}")
    return llm_output_dir_path


def get_errors_dir():
    errors_dir_path_config = os.getenv("ERRORS_DIR")
    if errors_dir_path_config:
        errors_dir_path = Path(errors_dir_path_config)
    else:
        errors_dir_path = Path.cwd() / (BASE_MODULE_PATH + "errors/")
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
