# Evaluations of the UI component selection and configuration AI functionality

[![Module Category](https://img.shields.io/badge/Module%20Category-Testing/Evaluation-darkmagenta)](https://github.com/RedHat-UX/next-gen-ui-agent)
[![Module Status](https://img.shields.io/badge/Module%20Status-Supported-green)](https://github.com/RedHat-UX/next-gen-ui-agent)

This module contains Dataset and code to generate the dataset and to run the UI Component selection AI functionality evaluations.

## Setup Evaluation Environment

Evaluation code requires LlamaStack server or one of common AI provider API compatible LLM serving.

Embedded LlamaStack is used by default, with configuration from `tests/ai_eval_components/llamastack-ollama.yaml`. It expects localhost [`ollama` (at port `11434`)](https://ollama.com/) running, hosting LLM model.
Other config file may be used thanks to `LLAMA_STACK_CONFIG_FILE`.

Remote/external LlamaStack can be also used if configured using either `http://{LLAMA_STACK_HOST}:{LLAMA_STACK_PORT}` pair, or `LLAMA_STACK_URL`. How to run external LlamaStack on localhost see [LLAMASTACK_DEV.md](../../LLAMASTACK_DEV.md).

If any of `MODEL_API_xy` env variable is set, then OpenAI/Antrropic API compatible LLM serving is used through [LangChain model](https://docs.langchain.com/oss/python/langchain/models#initialize-a-model).

Evaluation code accepts these environment variables:

- `INFERENCE_MODEL` - LLM used by the UI Agent, defaults to `granite3.3:2b` - this model must be available in used LlamaStack instance!
- `LLAMA_STACK_HOST` - remote/external LlamaStack server `http` host.
- `LLAMA_STACK_PORT` - remote/external LlamaStack server port, defaults to `5001`
- `LLAMA_STACK_URL` - remote/external LlamaStack server url. Allows to define whole url instead of use `LLAMA_STACK_HOST` and `LLAMA_STACK_PORT`.
- `LLAMA_STACK_CONFIG_FILE` - path of the embedded LlamaStack config file. Defaults to `tests/ai_eval_components/llamastack-ollama.yaml`.
- `MODEL_API_PROVIDER` - model API provider to use - optional, currently supported: `openai` (default), `anthropic`, `anthropic-vertexai-proxied`
- `MODEL_API_URL` - OpenAI/Anthropic compatible API base URL - optional, if not defined then default main URL of the API of given provider is used
- `MODEL_API_KEY` - OpenAI/Anthropic compatible API api_key - optional
- `MODEL_API_TEMPERATURE` - OpenAI/Anthropic compatible API LLM temperature - optional, use `0` if model is capable to run with it
- `DATASET_DIR` - directory with the dataset used for evaluations. Defaults to the `dataset` subdirectory in this project.
- `ERRORS_DIR` - directory where detailed error info files are written. Defaults to `errors` subdirectory in this project.
- `JUDGE_MODEL` - LLM model name for judge evaluation (required if `-j` flag is used)
- `JUDGE_API_URL` - API endpoint for judge model (required if `-j` flag is used)
- `JUDGE_API_KEY` - API key for judge model (required if `-j` flag is used)

If your API uses ssl certificate not signd by commonly trusted CA, you have to configure it for python `httpx` package used by `openai`/`anthropic` provider:

```sh
export SSL_CERT_FILE=/path/to/cert/your-CA-cert.pem
```

`anthropic-vertexai-proxied` is a custom inference provider created to
call [Anthropic models from Google Vertex AI](https://console.cloud.google.com/vertex-ai/publishers/anthropic/model-garden/claude-3-5-haiku)
proxied on different URL.
It calls url constructed as `"{MODEL_API_URL}/models/{INFERENCE_MODEL}:streamRawPredict"`.
In case of HTTP error `429`, indicating API throttling, it retries call after 10s for max 10 times.
It is stored in [`proxied_claude_inference.py`](proxied_claude_inference.py).

### Create missing directories if needed

```sh
mkdir ~/.llama/providers.d
```

## Run Evaluation

```sh
pants run tests/ai_eval_components/eval.py
```

You can use these commandline argument:

- `-c <ui-component-name>` to run evaluation for one named UI component only. If `all` is used then evaluation runs for all the components present in the evaluation dataset.
- `-f <dataset-file-name>` to run only evaluations from the named dataset file (for any UI component present in the file)
- `-o` to also evaluate `warn_only` dataset items
- `-w` to write Agent ouputs (LLM and Component data) with passed checks into files in the `/llm_out/` directory - usefull during the LLM functionality development to see all results
- `-s` evaluate only selected component type, not it's configuration - usefull for component selection development/tuning
- `-v` to enable vague component type check, allowing `table` and `set-of-cards` components to be interchanged
- `-j` to enable LLM-as-a-Judge evaluation (requires `JUDGE_MODEL`, `JUDGE_API_URL`, `JUDGE_API_KEY` env vars)
- `-h` to get help

```sh
pants run tests/ai_eval_components/eval.py -- -c one-card
```

### LLM-as-a-Judge Evaluation

Judge evaluation mode (`-j` flag) uses LLM to semantically evaluate if component choice and field selections are appropriate for the user's request.

```sh
export JUDGE_MODEL="Llama-3.3-70B-Instruct-FP8-dynamic"
export JUDGE_API_URL="https://..."
export JUDGE_API_KEY="..."
python -m ai_eval_components.eval -c all -j
```

Judges output predefined categories for consistency: `perfectly_relevant` (1.0), `relevant_with_supporting_detail` (0.85), `partially_relevant` (0.5), `irrelevant` (0.2) for field relevance; `perfect_choice` (1.0), `good_choice` (0.85), `reasonable_choice` (0.65), `wrong_choice` (0.3) for component choice.

If no `-c` nor `-f` argument is used, evaluation runs for all the components present in the evaluation dataset.
If args are used, evaluation script automatically switches UI Agent to the mode with all UI components if necessary,
message `UI Agent switched to 'all UI components' mode` is provided in this case.

During the run, basic info about running process and errors is written to the console. At the end, aggregated results
are provided, together with basic AI inference performance statistics. Inference times over 30s are not added to
the performance statistics, as they are mostly result of API throttling.

Detailed error info is written to the files in the specified directory (see above).
Separate error file is created for each dataset file, `.json` suffix is replaced by `-errors.txt` suffix.
Files are deleted at the begining of each evaluation run.

For each error, line is added in the format `==== <err_type> <dataset_item_id> ====`.

Where `err_type` is one of:

- `AGENT` - UI agent evaluation error
- `DATASET` - error in dataset file (missing field etc)
- `SYSTEM` - system error like problem with LLM call, unexpected error from the Agent etc

`dataset_item_id` is unique identifier of the dataset item to find it easier.

Next lines contain detailed description of errors. For `AGENT` error, prompt, LLM output, Component data, and location of the data file in `dataset_src` is also provided for easier debugging.

Results of some eval runs are stored in `/results` folder so we can compare them in time to see changes.
Each file stored here contains description info like:

```
* Date: 2025-06-09
* Components: all with vague component type check
* LLM: granite 3.2 2B
* Env: velias localhost (ollama on accelerated AMD)
```

and then results printed by eval script, including performance stats.

## Evaluation dataset

Dataset for the evaluation is stored in the `dataset` subdirectory.

It contains items for each UI component the UI Agent is able to generate. All inputs are in the dataset, together with info necessary for the response evaluation.

Some items may be marked as `warn_only`. They are not evaluated by default (see `eval.py` script params), and if evaluated, they only lead to evaluation warning, not to error.
Usefull for evaluation of optional/unimportant features, which we would like to see how they perform still at some cases. Eg. some more exotic shapes of backend data etc.

It is better to provide smaller files, grouped together by some common aspect (eg. the same expected UI component).

**DO NOT EDIT DATASET MANUALLY, SEE NEXT CHAPTER HOW TO GENERATE IT**

Dataset files itself must be `.json` containing JSON array of objects representing individual dataset items with fields:

- `id` unique identifier of the dataset item, used in error reporting
- `user_prompt` input for UI Agent
- `backend_data` input for UI Agent, must be JSON stored as a string
- `input_data_type` optional `type` of InputData - if defined and JSON wrapping is necessary due to data structure shape, then it is applied before the LLM call
- `expected_component` checked in UI Agent output during evaluation
- `warn_only` optional boolean with `true` if this item results only in evaluation warning, not error - used for evaluation of optional features which we would like to see how they perform in evals still
- `src` optional info about prompt and data source files in `dataset_src` directory for easier location

Example:

```json
[
  {
    "id": "one-card-000001",
    "user_prompt": "Show me my RHEL subscription.",
    "backend_data": "{\n    \"id\": \"EUS-101\",\n    \"name\": \"RHEL\",\n    \"endDate\": \"2024-12-24\",\n    \"supported\": true,\n    \"numOfItems\": 2,\n    \"viewUrl\": \"https://access.redhat.com/sub/EUS-101\"\n}",
    "expected_component": "one-card"
  },
  {
    "id": "one-card-000002",
    "user_prompt": "When does my RHEL subscription end?",
    "backend_data": "{\n    \"id\": \"EUS-101\",\n    \"name\": \"RHEL\",\n    \"endDate\": \"2024-12-24\",\n    \"supported\": true,\n    \"numOfItems\": 2,\n    \"viewUrl\": \"https://access.redhat.com/sub/EUS-101\"\n}",
    "expected_component": "one-card"
  },
  {
    "id": "one-card-000003",
    "user_prompt": "Where can I find details about my RHEL subscription?",
    "backend_data": "{\n    \"id\": \"EUS-101\",\n    \"name\": \"RHEL\",\n    \"endDate\": \"2024-12-24\",\n    \"supported\": true,\n    \"numOfItems\": 2,\n    \"viewUrl\": \"https://access.redhat.com/sub/EUS-101\"\n}",
    "expected_component": "",
    "warn_only": true
  }
]
```

### Generating dataset from the source files

Dataset is generated from source files, it allows to automatically combine data files with prompts to get more examples.

Source files for the dataset are stored in `dataset_src` directory. It contains:

- `backend_data_shared/` directory with backend data files shared for more component evaluations. Contains individual JSON files with the backend data.
- `components/` directory with the dataset sources for each UI component selection evaluation. Subdirectories are named by these components.

Component dataset source directory then contains:

- `items_generate.json` configuration used for the dataset generation. Defines prompts and backend data files combined together during the generation, together with optionl `warn_only` flag.
  Contains array of objects with attributes:
  - `prompts_file` with name of the file to load prompts from. Prompts are defined in json files in this directory with `prompts_` prefix. It is JSON array containing individual prompts as string.
  - `backend_data_files` array with names of the backend data files. Backend data files are searched in local `backend_data/` subdirectory, if not found here then in `backend_data_shared/` directory.
  - `input_data_type` optional `type` of InputData - used for JSON wrapping feature
  - `comment` optional comment to descrive meaning of this part of the generation
- `backend_data/` directory with backend data JSON files
- `items/` directory allows to add individual items into the dataset. Usefull for exceptions, edge case test items etc.
  - Each item is defined in two separate files with the same name, but different extension. `.txt` file contains promp text, and `.json` file contains the JSON backend data. Eg. `item1.txt` and `item1.json`.

To run regeneration process use:

```sh
pants run tests/ai_eval_components/dataset_gen.py
```

You can use these commandline argument:

- `-s <path>` or `--src <path>` - source directory (default: `tests/ai_eval_components/dataset_src/`)
- `-d <path>` or `--dest <path>` - destination directory (default: `tests/ai_eval_components/dataset/`)
- `-h` - help

```sh
# Generate Movies/Subscriptions dataset (default)
pants run tests/ai_eval_components/dataset_gen.py

# Generate K8s dataset
pants run tests/ai_eval_components/dataset_gen.py -- -s tests/ai_eval_components/dataset_src_k8s/ -d tests/ai_eval_components/dataset_k8s/
```

See console output for info about the process and results.

Result of the generation is stored in the `dataset` subdirectory in this module, which is used for the evaluation itself. You have to commit change here after the regeneration.

## Syncing Datasets to E2E Client

After regenerating datasets, you should sync them to the e2e test client to keep the UI in sync:

```sh
# Sync datasets to e2e client (generates inlineDatasets.ts and quickPrompts.ts)
pants run tests/ai_eval_components/sync_datasets_to_e2e.py
```

This script reads from both `dataset/` and `dataset_k8s/` directories and generates:
- `tests/ngui-e2e/client/src/data/inlineDatasets.ts` - Inline datasets for testing
- `tests/ngui-e2e/client/src/quickPrompts.ts` - Quick prompt suggestions with attached data

**Recommended workflow:**
1. Regenerate datasets: `pants run tests/ai_eval_components/dataset_gen.py`
2. Regenerate K8s datasets: `pants run tests/ai_eval_components/dataset_gen.py -- -s tests/ai_eval_components/dataset_src_k8s/ -d tests/ai_eval_components/dataset_k8s/`
3. Sync to e2e client: `pants run tests/ai_eval_components/sync_datasets_to_e2e.py`
4. Review and commit changes
