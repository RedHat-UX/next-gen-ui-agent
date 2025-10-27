import asyncio
import json
import time
from traceback import print_exception

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
    SUPPORTED_COMPONENTS,
    get_dataset_files,
    load_args,
    load_dataset_file,
    select_run_components,
    validate_dataset_row,
)
from ai_eval_components.types import (
    DATASET_FILE_SUFFIX,
    DatasetRow,
    DatasetRowAgentEvalResult,
)
from next_gen_ui_agent import InputData
from next_gen_ui_agent.array_field_reducer import reduce_arrays
from next_gen_ui_agent.component_selection_llm_onestep import (
    OnestepLLMCallComponentSelectionStrategy,
)
from next_gen_ui_agent.component_selection_llm_strategy import (
    MAX_ARRAY_SIZE_FOR_LLM,
    ComponentSelectionStrategy,
)
from next_gen_ui_agent.component_selection_llm_twostep import (
    TwostepLLMCallComponentSelectionStrategy,
)
from next_gen_ui_agent.data_transform.set_of_cards import SetOfCardsDataTransformer
from next_gen_ui_agent.data_transform.table import TableDataTransformer
from next_gen_ui_agent.data_transform.types import ComponentDataBase
from next_gen_ui_agent.data_transform.validation.assertions import (
    assert_array_not_empty,
    assert_str_not_blank,
)
from next_gen_ui_agent.data_transform.validation.types import (
    ComponentDataValidationError,
)
from next_gen_ui_agent.data_transformation import get_data_transformer
from next_gen_ui_agent.json_data_wrapper import wrap_json_data
from next_gen_ui_agent.model import InferenceBase
from next_gen_ui_agent.types import UIComponentMetadata
from next_gen_ui_llama_stack_embedded import init_inference_from_env

# allows to print system error traces to the stderr
PRINT_SYS_ERR_TRACE = True

TWO_STEP_COMPONENT_SELECTION = False
""" Allows to switch between one and two step (LLM inference calls) component selection process """

INFERENCE_MODEL_DEFAULT = "granite3.3:2b"

# Ollama models:
# export INFERENCE_MODEL_DEFAULT=granite3.3:8b
# export INFERENCE_MODEL_DEFAULT=llama3.2:latest

# Gemini API models:
# export INFERENCE_MODEL_DEFAULT=gemini/gemini-2.0-flash
# export INFERENCE_MODEL_DEFAULT=gemini/gemini-2.5-flash

LLAMASTACK_CONFIG_PATH_DEFAULT = "tests/ai_eval_components/llamastack-ollama.yaml"


def check_result_explicit(
    component: UIComponentMetadata,
    errors: list[ComponentDataValidationError],
    dsr: DatasetRow,
    arg_vague_component_check: bool,
    arg_selected_component_type_check_only: bool = False,
):
    """
    Perform explicit checks on the LLM generated component JSON
    * all necessary attributes in the root and in `fields` are not empty
    * component is of the expected type

    Return list of errors or empty list if everything is OK.
    """

    componentDict = component.model_dump()
    assert_str_not_blank(componentDict, "title", "title.empty", errors)
    if assert_str_not_blank(componentDict, "component", "component.empty", errors):
        ds_expected_component = dsr["expected_component"]
        generated_component = component.component
        if generated_component != ds_expected_component:
            if arg_vague_component_check:
                # allow `table` and `set-of-cards` components to be interchanged
                if (
                    generated_component == TableDataTransformer.COMPONENT_NAME
                    and ds_expected_component
                    == SetOfCardsDataTransformer.COMPONENT_NAME
                ):
                    return
                if (
                    generated_component == SetOfCardsDataTransformer.COMPONENT_NAME
                    and ds_expected_component == TableDataTransformer.COMPONENT_NAME
                ):
                    return

            errors.append(
                ComponentDataValidationError(
                    "component.invalid",
                    f"{generated_component} instead of {ds_expected_component}",
                )
            )
    if not arg_selected_component_type_check_only:
        if assert_array_not_empty(componentDict, "fields", "fields.empty", errors):
            for i, field in enumerate(component.fields):
                fn = f"fields[{i}]."
                fieldDict = field.model_dump()
                assert_str_not_blank(fieldDict, "name", fn + "name.empty", errors)

                assert_str_not_blank(
                    fieldDict, "data_path", fn + "data_path.empty", errors
                )


def evaluate_agent_for_dataset_row(
    dsr: DatasetRow,
    inference: InferenceBase,
    arg_vague_component_check: bool,
    unsupported_components: bool = False,
    arg_selected_component_type_check_only: bool = False,
):
    """Run agent evaluation for one dataset row"""
    errors: list[ComponentDataValidationError] = []
    input_data = InputData(id="myid", data=dsr["backend_data"])

    input_data_id = input_data["id"]
    json_data = json.loads(input_data["data"])

    input_data_type = dsr.get("input_data_type")
    # wrap parsed JSON data structure into data type field if allowed and necessary as in ComponentSelectionStrategy
    json_data = wrap_json_data(json_data, input_data_type)
    # we have to reduce arrays size to avoid LLM context window limit as in ComponentSelectionStrategy
    json_data_for_llm = reduce_arrays(json_data, MAX_ARRAY_SIZE_FOR_LLM)

    component_selection: ComponentSelectionStrategy
    if not TWO_STEP_COMPONENT_SELECTION:
        component_selection = OnestepLLMCallComponentSelectionStrategy(
            unsupported_components
        )
    else:
        component_selection = TwostepLLMCallComponentSelectionStrategy(
            unsupported_components, arg_selected_component_type_check_only
        )

    # separate steps so we can see LLM response even if it is invalid JSON
    time_start = round(time.time() * 1000)

    llm_response = asyncio.run(
        component_selection.perform_inference(
            inference, dsr["user_prompt"], json_data_for_llm, input_data_id
        )
    )
    report_perf_stats(time_start, round(time.time() * 1000), dsr["expected_component"])

    component: UIComponentMetadata | None = None
    try:
        component = component_selection.parse_infernce_output(
            llm_response, input_data_id
        )
        component.json_data = json_data
    except Exception as e:
        errors.append(
            ComponentDataValidationError(
                "invalid_json",
                "LLM produced invalid JSON: " + str(e).replace("\n", ": "),
            )
        )

    # print("\nComponent data:\n" + component.model_dump_json(indent=2))

    data: ComponentDataBase | None = None
    if component:
        # load data so we can evaluate that pointers to data are correct
        # any exception from this code is "SYS" error
        component.id = input_data_id

        check_result_explicit(
            component,
            errors,
            dsr,
            arg_vague_component_check,
            arg_selected_component_type_check_only,
        )

        if not arg_selected_component_type_check_only:
            # if not any error so far, validate the component data_paths and overal structure of data for given component
            if len(errors) == 0:
                data_transformer = get_data_transformer(component.component)
                data = data_transformer.validate(component, input_data, errors)

            # TODO NGUI-116 LLM-as-a-judge AI check to evaluate if fields are relevant to the user prompt and data

    return DatasetRowAgentEvalResult(llm_response, errors, data)


if __name__ == "__main__":
    (
        arg_ui_component,
        arg_write_llm_output,
        arg_dataset_file,
        arg_vague_component_check,
        arg_also_warn_only,
        arg_selected_component_type_check_only,
    ) = load_args()
    errors_dir_path = get_errors_dir()
    llm_output_dir_path = get_llm_output_dir(arg_write_llm_output)
    dataset_files = get_dataset_files(arg_dataset_file)
    inference = init_inference_from_env(
        default_model=INFERENCE_MODEL_DEFAULT,
        default_config_file=LLAMASTACK_CONFIG_PATH_DEFAULT,
    )
    if not inference:
        print("Inference not initialized because not configured in env variables")
        exit(1)

    run_components, unsupported_components = select_run_components(
        arg_ui_component, arg_dataset_file
    )

    for dataset_file in dataset_files:
        dataset = load_dataset_file(dataset_file)

        # filter dataset by UI components to run for
        if run_components:
            dataset = [f for f in dataset if f["expected_component"] in run_components]

        # filter dataset by warn_only flag
        if not arg_also_warn_only:
            dataset = [f for f in dataset if not f.get("warn_only", False)]

        # skip dataset files not containing any record after filtering
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
                        # automatically switch to unsupported_components mode if any found in the dataset
                        if not unsupported_components:
                            unsupported_components = (
                                dsr["expected_component"] not in SUPPORTED_COMPONENTS
                            )
                            if unsupported_components:
                                print(
                                    "\nUI Agent switched to 'all UI components' mode as unsupported one was found in the dataset file\n"
                                )

                        eval_result = evaluate_agent_for_dataset_row(
                            dsr,
                            inference,
                            arg_vague_component_check,
                            unsupported_components,
                            arg_selected_component_type_check_only,
                        )
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
                    if PRINT_SYS_ERR_TRACE:
                        print_exception(e)

            if arg_write_llm_output:
                f_out.close()

    print("\n\nEvaluations finished:")
    print_stats()
    print("")
    print_perf_stats()
