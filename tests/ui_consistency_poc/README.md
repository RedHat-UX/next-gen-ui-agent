# Research/PoC of the UI component consistency during conversation

[![Module Category](https://img.shields.io/badge/Module%20Category-Testing/Evaluation-darkmagenta)](https://github.com/RedHat-UX/next-gen-ui-agent)
[![Module Status](https://img.shields.io/badge/Module%20Status-Tech%20Preview-orange)](https://github.com/RedHat-UX/next-gen-ui-agent)

This module contains code used for UI component consistency during conversation research/PoC and detailed results

## Provides

* `one_component.py` - runnable code for one component consistency research PoC - you can select LLM at the begining (uses embedded Llama Stack). Writes out to console and files in `one_component_results/` directory
* `one_component_results/` - directory with results from `one_component.py`. Files names are LLM used for the run.
