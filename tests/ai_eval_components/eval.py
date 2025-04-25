import asyncio
import json
import os
import time

from ai_eval_components.eval_perfstats import print_perf_stats, report_perf_stats
from ai_eval_components.eval_reporting import (
    ERR_FILE_SUFFIX,
    console_print_progress_dot,
    get_errors_dir,
    get_llm_output_dir,
    init_agent_out_stream,
    print_stats,
    report_err_dataset,
    report_err_sys,
    report_err_uiagent,
    report_success,
)
from ai_eval_components.eval_utils import (
    assert_array_not_empty,
    assert_str_not_blank,
    get_dataset_files,
    load_args,
    load_dataset_file,
    validate_dataset_row,
)
from ai_eval_components.types import (
    DATASET_FILE_SUFFIX,
    DatasetRow,
    DatasetRowAgentEvalResult,
    EvalError,
)
from llama_stack_client import LlamaStackClient
from next_gen_ui_agent import InputData
from next_gen_ui_agent.component_selection import component_selection_inference
from next_gen_ui_agent.data_transformation import enhance_component_by_input_data
from next_gen_ui_agent.model import InferenceBase
from next_gen_ui_agent.types import UIComponentMetadata
from next_gen_ui_llama_stack.llama_stack_inference import LlamaStackAgentInference

# INFERENCE_MODEL_DEFAULT = "llama3.2:latest"
INFERENCE_MODEL_DEFAULT = "granite3.2:2b"
LLAMA_STACK_HOST_DEFAULT = "localhost"
LLAMA_STACK_PORT_DEFAULT = "5001"


def init_inference() -> InferenceBase:
    host = os.getenv("LLAMA_STACK_HOST", default=LLAMA_STACK_HOST_DEFAULT)
    port = os.getenv("LLAMA_STACK_PORT", default=LLAMA_STACK_PORT_DEFAULT)
    base_url = f"http://{host}:{port}"

    model = os.getenv("INFERENCE_MODEL", default=INFERENCE_MODEL_DEFAULT)

    print(f"Creating UI Agent with LlamaStack host={base_url} and LLM={model}")

    client = LlamaStackClient(
        base_url=base_url,
    )
    return LlamaStackAgentInference(client, model)


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

            # TODO component specific evals where fields have to be of some type, eg link to image for image component, link to video etc


def evaluate_agent_for_dataset_row(dsr: DatasetRow, inference: InferenceBase):
    """Run agent evaluation for one dataset row"""
    errors: list[EvalError] = []
    input_data = InputData(id="myid", data=dsr["backend_data"])

    # separate steps so we can see LLM response even if it is invalid JSON
    time_start = round(time.time() * 1000)
    llm_response = asyncio.run(
        component_selection_inference(dsr["user_prompt"], inference, input_data)
    )
    report_perf_stats(time_start, round(time.time() * 1000), dsr["expected_component"])

    try:
        component: UIComponentMetadata = json.loads(llm_response)

        # load data so we can evaluate that pointers to data are correct
        component["id"] = input_data["id"]
        components = [component]
        enhance_component_by_input_data([input_data], components)

        check_result_explicit(component, errors, dsr)

        # TODO NGUI-116 LLM-as-a-judge AI check

    except json.JSONDecodeError as e:
        errors.append(EvalError("invalid_json", "LLM produced invalid JSON: " + str(e)))
    except json.decoder.JSONDecodeError as e:
        errors.append(EvalError("invalid_json", "LLM produced invalid JSON: " + str(e)))

    return DatasetRowAgentEvalResult(llm_response, errors)


if __name__ == "__main__":
    arg_ui_component, arg_write_llm_output, arg_dataset_file = load_args()
    errors_dir_path = get_errors_dir()
    if arg_write_llm_output:
        llm_output_dir_path = get_llm_output_dir()
    dataset_files = get_dataset_files(arg_dataset_file)
    inference = init_inference()

    for dataset_file in dataset_files:
        dataset = load_dataset_file(dataset_file)

        if arg_ui_component:
            dataset = [
                f for f in dataset if f["expected_component"] == arg_ui_component
            ]
        # skip dataset files not containing any record
        if len(dataset) == 0:
            continue

        print(f"\n==== Processing {dataset_file.name} ====")
        with (
            errors_dir_path
            / dataset_file.name.replace(DATASET_FILE_SUFFIX, ERR_FILE_SUFFIX)
        ).open("a") as f_err:
            f_out = init_agent_out_stream(
                arg_write_llm_output, llm_output_dir_path, dataset_file
            )
            i = 0
            is_progress_dot = False
            for dsr in dataset:
                i, is_progress_dot = console_print_progress_dot(i, is_progress_dot)
                try:
                    ds_errors = validate_dataset_row(dsr)

                    if len(ds_errors) > 0:
                        is_progress_dot = report_err_dataset(
                            f_err, ds_errors, dsr, is_progress_dot
                        )
                    else:
                        eval_result = evaluate_agent_for_dataset_row(dsr, inference)
                        if len(eval_result.errors) > 0:
                            is_progress_dot = report_err_uiagent(
                                f_err, eval_result, dsr, is_progress_dot
                            )
                        else:
                            report_success(
                                f_out, eval_result, dsr, arg_write_llm_output
                            )

                except Exception as e:
                    is_progress_dot = report_err_sys(f_err, e, dsr, is_progress_dot)

            if arg_write_llm_output:
                f_out.close()

    print("\n\nEvaluations finished:")
    print_stats()
    print("")
    print_perf_stats()
