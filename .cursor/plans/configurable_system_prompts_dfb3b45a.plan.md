---
name: Configurable System Prompts
overview: Add configuration fields to `AgentConfigPrompt` that allow overriding the initial parts of system prompts for both one-step and two-step strategies (step1 and step2), while keeping the dynamically generated sections (component descriptions, examples) unchanged.
todos:
  - id: update_types
    content: Add system_prompt_* fields to AgentConfigPrompt in types.py
    status: completed
  - id: update_chart_instructions
    content: Add template parameter to build_chart_instructions() in component_selection_common.py
    status: completed
  - id: update_onestep
    content: Modify _build_system_prompt() in component_selection_llm_onestep.py to use config overrides
    status: completed
  - id: update_twostep_step1
    content: Modify _build_step1select_system_prompt() in component_selection_llm_twostep.py to use config override
    status: completed
  - id: validate_step2_placeholder
    content: Add validation in TwostepLLMCallComponentSelectionStrategy.__init__() to check {component} placeholder
    status: completed
  - id: update_twostep_step2
    content: Modify inference_step2configure() in component_selection_llm_twostep.py to use config override
    status: completed
  - id: add_tests
    content: Create comprehensive tests for custom system prompts
    status: completed
  - id: update_docs_configuration
    content: Add basic reference description of new prompt fields to configuration.md
    status: completed
  - id: update_docs_llm
    content: Add detailed prompt tuning chapter to llm.md
    status: completed
  - id: run_tests
    content: Run test suite and verify all tests pass
    status: completed
isProject: false
---

