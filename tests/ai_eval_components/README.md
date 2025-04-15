# Evaluations of the UI component selection and configuration AI functionality

This module contains Dataset and code to generate the dataset and to run the UI Component selection AI functionality evaluations.

## Setup Evaluation Environment

Evaluation code requires running LlamaStack server. How to run local instance see [LLAMASTACK_DEV.md](../../LLAMASTACK_DEV.md).

Evaluation code accepts these environment variables:
* `LLAMA_STACK_HOST` - defaults to `localhost`
* `LLAMA_STACK_PORT` - defaults to `5001`
* `INFERENCE_MODEL` - LLM used by the UI Agent, defaults to `granite3.1-dense:2b` - this model must be available in the LlamaStack instance, see [LLAMASTACK_DEV.md](../../LLAMASTACK_DEV.md)!
* `DATASET_DIR` - directory with the dataset used for evaluations. Defaults to the `dataset` subdirectory in this project.
* `ERRORS_DIR` - directory where detailed error info files are written. Defaults to `errors` subdirectory in this project.

## Run Evaluation

```sh
pants run tests/ai_eval_components/eval.py
```

You can use these commandline argument:
* `-c <ui-component-name>` to run evaluation for one UI component only named
* `-w` to write Agent ouput with passed checks into files in the `/llm_out/` directory - usefull during the LLM functionality development to see all results
* `-h` to get help

```sh
pants run tests/ai_eval_components/eval.py -- -c one-card
```

During the run, basic info about running process and errors is written to the console. At the end, aggregated results are provided.

Detailed error info is written to the files in the specified directory (see above).
Separate error file is created for each dataset file, `.json` suffix is replaced by `-errors.txt` suffix. 
Files are deleted at the begining of each evaluation run.

For each error, line is added in the format `==== <err_type> <dataset_item_id> ====`. 

Where `err_type` is one of:
* `AGENT` - UI agent evaluation error 
* `DATASET` - error in dataset file (missing field etc)
* `SYSTEM` - system error like problem with LLM call, unexpected error from the Agent etc
  
`dataset_item_id` is unique identifier of the dataset item to find it easier.

Next lines contain detailed description of errors. For `AGENT` error, UI Agent output is also provided.

## Evaluation dataset

Dataset for the evaluation is stored in the `dataset` subdirectory.

It contains items for each UI component the UI Agent is able to generate. All inputs are in the dataset, together with info necessary for the response evaluation.

It is better to provide smaller files, grouped together by some common aspect (eg. the same expected UI component).

Dataset files itself must be `.json` containing JSON array of objects representing individual dataset items with fields:
* `id` unique identifier of the dataset item, used in error reporting
* `user_prompt` input for UI Agent
* `backend_data` input for UI Agent, must be JSON stored as a string
* `expected_component` checked in UI Agent output during evaluation

Example:
```json
[
    {
        "id": "one-card-000001",
        "user_prompt": "Show me my RHEL subscription.",
        "backend_data": "{\n    \"id\": \"EUS-101\",\n    \"name\": \"RHEL\",\n    \"endDate\": \"2024-12-24\",\n    \"supported\": true,\n    \"numOfItems\": 2,\n    \"viewUrl\": \"https:\/\/access.redhat.com\/sub\/EUS-101\"\n}",
        "expected_component": "one-card"
    },
    {
        "id": "one-card-000002",
        "user_prompt": "When does my RHEL subscription end?",
        "backend_data": "{\n    \"id\": \"EUS-101\",\n    \"name\": \"RHEL\",\n    \"endDate\": \"2024-12-24\",\n    \"supported\": true,\n    \"numOfItems\": 2,\n    \"viewUrl\": \"https:\/\/access.redhat.com\/sub\/EUS-101\"\n}",
        "expected_component": "one-card"
    },
    {
        "id": "one-card-000003",
        "user_prompt": "Where can I find details about my RHEL subscription?",
        "backend_data": "{\n    \"id\": \"EUS-101\",\n    \"name\": \"RHEL\",\n    \"endDate\": \"2024-12-24\",\n    \"supported\": true,\n    \"numOfItems\": 2,\n    \"viewUrl\": \"https:\/\/access.redhat.com\/sub\/EUS-101\"\n}",
        "expected_component": ""
    }
]
```

### Regenerating dataset from the source files

Dataset is generated from source files, it allows to automatically combine data files with prompts to get more examples.

Source files for the dataset are stored in `dataset_src` directory. It contains:
* `backend_data_shared/` directory with backend data files shared for more component evaluations. Contains individual JSON files with the backend data.
* `components/` directory with the dataset sources for each UI component selection evaluation. Subdirectories are named by these components.

Component dataset source directory then contains:
* `items_generate.json` configuration used for the dataset generation. Defines prompts and backend data files combined together during the generation. 
  Contains array of objects with attributes:
  * `prompts_file` with name of the file to load prompts from. Prompts are defined in json files in this directory with `prompts_` prefix. It is JSON array containing individual prompts as string.
  * `backend_data_files` array with names of the backend data files. Backend data files are searched in local `backend_data/` subdirectory, if not found here then in `backend_data_shared/` directory.
* `backend_data/` directory with backend data JSON files
* `items/` directory allows to add individual items into the dataset. Usefull for exceptions, edge case test items etc.
  * Each item is defined in two separate files with the same name, but different extension. `.txt` file contains promp text, and `.json` file contains the JSON backend data. Eg. `item1.txt` and `item1.json`. 

To run regeneration process use:
```sh
pants run tests/ai_eval_components/dataset_gen.py
```
See console output for info about the process and results.

Result of the generation is stored in the `dataset` subdirectory in this module, which is used for the evaluation itself. You have to commit change here after the regeneration.
