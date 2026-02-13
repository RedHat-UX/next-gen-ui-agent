# Evaluations

To evaluate how well a particular LLM is performing on *UI Agent* component selection and configuration task, 
we provide [Evaluation tool and basic dataset](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/tests/ai_eval_components).

## Basic evaluations

This evaluation currently covers distinct shapes of the input data, and evaluates if LLM generates correct configuration from 
the "technical" point of view. It also verifies if expected UI component is selected. 
This evaluation does not cover relevance of the selected fields, as it can't be defined exactly in the dataset. So you have 
to do this evaluation by yourself from recorded evals results.

## LLM-as-a-judge evaluations

Evaluation tool also implements optional LLM-as-a-judge feature, which can check two aspects of the agent's decision:

* relevance of selected UI component - it goes behind the expected component defined in the dataset, as it can't catch all nuances in some cases
* relevance of fields selected for the visualization in generic components like `one-card` or `table`.  

## Evaluation results

Evaluation tool outputs different kinds of informations during the evaluation process, like:

* evaluation failures and their statistics per component
* LLM outputs
* LLM inference performance statistics
* used system prompts - usefull for [agent's system prompt customization/finetuning](prompt_tuning.md) process.

So you can look at the evaluation from different angles, study results in details or follow statistics only, make it part of the system prompt finetuning etc.

[Automated dashboard](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/tests/ai_eval_components/README_DASHBOARD.md) for comparing model performance across multiple evaluation runs is also available.

Evaluation results for some LLMs are available in `/results` sub-directory.

We regularly run evaluations against few LLMs internally to monitor agent's performance during the development.
