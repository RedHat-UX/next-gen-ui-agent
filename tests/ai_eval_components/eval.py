import asyncio
import json
import os
import time
from traceback import print_exception

from ai_eval_components.eval_perfstats import (
    print_perf_stats,
    report_perf_stats,
    save_perf_stats_to_file,
)
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
    JudgeResult,
)
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
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
from next_gen_ui_agent.inference.inference_base import InferenceBase
from next_gen_ui_agent.inference.langchain_inference import LangChainModelInference
from next_gen_ui_agent.inference.proxied_anthropic_vertexai_inference import (
    ProxiedAnthropicVertexAIInference,
)
from next_gen_ui_agent.json_data_wrapper import wrap_json_data
from next_gen_ui_agent.types import InputData, UIComponentMetadata
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
    arg_selected_component_type_check_only: bool = False,
    judge_inference: InferenceBase | None = None,
):
    """Run agent evaluation for one dataset row"""
    errors: list[ComponentDataValidationError] = []
    judge_results_list: list[JudgeResult] | None = None
    input_data = InputData(id="myid", data=dsr["backend_data"])

    input_data_id = input_data["id"]
    json_data = json.loads(input_data["data"])

    input_data_type = dsr.get("input_data_type")
    # wrap parsed JSON data structure into data type field if provided and wrapping is necessary as in ComponentSelectionStrategy
    json_data, field_name = wrap_json_data(json_data, input_data_type)
    # we have to reduce arrays size to avoid LLM context window limit as in ComponentSelectionStrategy
    json_data_for_llm = reduce_arrays(json_data, MAX_ARRAY_SIZE_FOR_LLM)

    component_selection: ComponentSelectionStrategy
    if not TWO_STEP_COMPONENT_SELECTION:
        component_selection = OnestepLLMCallComponentSelectionStrategy()
    else:
        component_selection = TwostepLLMCallComponentSelectionStrategy(
            arg_selected_component_type_check_only
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
        component.json_wrapping_field_name = field_name
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

        if judge_inference:
            # Judge-only mode: Skip deterministic checks, use LLM judges for evaluation
            from ai_eval_components.eval_llm_judge import run_llm_judges

            judge_results_list = asyncio.run(
                run_llm_judges(
                    component, dsr["user_prompt"], json_data, judge_inference
                )
            )

            # Only judge failures determine test result
            if judge_results_list:
                for jr in judge_results_list:
                    if not jr["passed"]:
                        errors.append(
                            ComponentDataValidationError(
                                f"judge.{jr['judge_name']}",
                                f"Category: {jr['category']}, Score {jr['score']:.2f}: {jr['reasoning']}",
                            )
                        )
        else:
            # Deterministic mode: Traditional validation (no judges)
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

    return DatasetRowAgentEvalResult(
        llm_response["outputs"], errors, data, judge_results_list
    )


def init_direct_api_inference_from_env(
    default_model: str | None = None,
    override_model: str | None = None,
    override_api_url: str | None = None,
    override_api_key: str | None = None,
) -> InferenceBase | None:
    """
    Initialize OpenAI compatible API inference from environment variables if at least one `MODEL_API_xy` env variable is set.

    Parameters:
    * `default_model` - default model to use if `INFERENCE_MODEL` env variable is not set
    * `override_model` - if provided, use this model instead of env vars
    * `override_api_url` - if provided, use this URL instead of MODEL_API_URL
    * `override_api_key` - if provided, use this key instead of MODEL_API_KEY

    Environment variables:
    * `INFERENCE_MODEL` - LLM model to use - inference is not created if undefined, default value can be provided as method argument
    * `MODEL_API_URL` - OpenAI compatible API base URL - optional, if not defined then OpenAI API base URL is used
    * `MODEL_API_KEY` - api key - optional
    * `MODEL_API_TEMPERATURE` - temperature for the LLM - optional
    * `MODEL_API_PROVIDER` - model API provider to use - optional, currently supported: `openai` (default), `anthropic`, `anthropic-vertexai-proxied`
    """

    base_url = override_api_url if override_api_url else os.getenv("MODEL_API_URL")
    api_key = override_api_key if override_api_key else os.getenv("MODEL_API_KEY")
    temperature = os.getenv("MODEL_API_TEMPERATURE")

    if base_url or api_key or temperature or os.getenv("MODEL_API_PROVIDER"):
        model = override_model or os.getenv("INFERENCE_MODEL") or default_model
        if not model:
            return None

        provider = os.getenv("MODEL_API_PROVIDER", "openai")

        print(
            f"Creating UI Agent with {provider} API inference model={model} base_url={base_url} temperature={temperature}"
        )

        if provider == "anthropic":
            llm_model = ChatAnthropic(
                model=model,
                base_url=base_url,
                api_key=api_key,  # type: ignore
                temperature=float(temperature) if temperature else None,
            )
        elif provider == "anthropic-vertexai-proxied":
            return ProxiedAnthropicVertexAIInference(
                model=model,
                api_key=api_key,  # type: ignore
                temperature=float(temperature) if temperature else 0,
                base_url=base_url,  # type: ignore
            )
        else:
            llm_model = ChatOpenAI(
                model=model,
                base_url=base_url,
                api_key=api_key,  # type: ignore
                temperature=float(temperature) if temperature else None,
            )

        return LangChainModelInference(model=llm_model)

    return None


if __name__ == "__main__":
    (
        arg_ui_component,
        arg_write_llm_output,
        arg_dataset_file,
        arg_vague_component_check,
        arg_also_warn_only,
        arg_selected_component_type_check_only,
        arg_judge_enabled,
    ) = load_args()
    errors_dir_path = get_errors_dir()
    llm_output_dir_path = get_llm_output_dir(arg_write_llm_output)
    dataset_files = get_dataset_files(arg_dataset_file)

    inference = init_direct_api_inference_from_env(
        default_model=INFERENCE_MODEL_DEFAULT
    )

    if not inference:
        inference = init_inference_from_env(
            default_model=INFERENCE_MODEL_DEFAULT,
            default_config_file=LLAMASTACK_CONFIG_PATH_DEFAULT,
        )

    if not inference:
        print("Inference not initialized because not configured in env variables")
        exit(1)

    # Get agent model name for reporting
    agent_model_name = os.getenv("INFERENCE_MODEL", INFERENCE_MODEL_DEFAULT)

    # Initialize judge inference if judges are enabled
    judge_inference = None
    judge_enabled_env = os.getenv("JUDGE_ENABLED", "false").lower() == "true"
    judge_enabled = arg_judge_enabled or judge_enabled_env
    judge_model_name = None
    if judge_enabled:
        judge_model_name = os.getenv("JUDGE_MODEL")
        judge_api_url = os.getenv("JUDGE_API_URL")
        judge_api_key = os.getenv("JUDGE_API_KEY")

        if not judge_model_name or not judge_api_url or not judge_api_key:
            print(
                "Judge inference not initialized because not configured in env variables"
            )
            print("Required: JUDGE_MODEL, JUDGE_API_URL, JUDGE_API_KEY")
            exit(1)

        print(f"Initializing judge inference with model: {judge_model_name}")

        judge_inference = init_direct_api_inference_from_env(
            default_model=judge_model_name,
            override_model=judge_model_name,
            override_api_url=judge_api_url,
            override_api_key=judge_api_key,
        )
        if not judge_inference:
            # Temporarily set INFERENCE_MODEL to judge model for initialization
            original_inference_model = os.getenv("INFERENCE_MODEL")
            os.environ["INFERENCE_MODEL"] = judge_model_name
            try:
                judge_inference = init_inference_from_env(
                    default_model=judge_model_name,
                    default_config_file=LLAMASTACK_CONFIG_PATH_DEFAULT,
                )
            finally:
                # Restore original INFERENCE_MODEL
                if original_inference_model:
                    os.environ["INFERENCE_MODEL"] = original_inference_model
                else:
                    os.environ.pop("INFERENCE_MODEL", None)
        if not judge_inference:
            print(
                "Judge inference not initialized because not configured in env variables"
            )
            exit(1)

    run_components = select_run_components(arg_ui_component, arg_dataset_file)

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

                        eval_result = evaluate_agent_for_dataset_row(
                            dsr,
                            inference,
                            arg_vague_component_check,
                            arg_selected_component_type_check_only,
                            judge_inference,
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

    # Save performance stats to file for report generation
    perf_stats_file = errors_dir_path / "perf_stats.json"
    save_perf_stats_to_file(
        str(perf_stats_file), judge_enabled, judge_model_name, agent_model_name
    )
