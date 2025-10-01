# Release Notes

---

## Release Notes - Version 0.2.0

This release significantly enhances the Next Gen UI agent with advanced configuration capabilities, Model Context Protocol (MCP) integration, and improved component handling. We've modernized the technology stack by upgrading to LlamaStack 0.2.20, introduced flexible agent configuration through YAML files, and expanded the system with new component types and better data handling mechanisms.

### Key Features and Benefits

* **Model Context Protocol (MCP) Integration**:
    * **MCP Server Implementation**: Added comprehensive MCP integration with a standalone MCP server, enabling better communication and interaction with external model services.

* **Hand Built Components Support**:
    * **Hand Built Components (HBC)**: Introduced a new HBC system to use hand built UI components to render defined input data types in a fully controlled way, without AI involvement.

* **Documentation Improvements**:
    * **Guides**: Several guides added how to bind Next Gen UI into AI applications and their UI.
    * **Core Concepts:**: New chapters `Data UI Blocks` and `Configuration`, `Architecture` chapter improved.

* **Other Improvements**:
    * **YAML-based Agent Configuration**: Introduced flexible YAML file configuration, enabling easier deployment and customization of agent behavior and settings.
    * **Configurable Embedded LlamaStack**: Added configurable embedded LlamaStack Inference module `next_gen_ui_llama_stack_embedded` for easier integration and deployment flexibility. Used in the evaluation framework.
    * **Better Data Path Handling**: Improved data path sanitization and value pickup from input data, including better handling of boolean values and complex nested structures.
    * **Improved Dependency Management**: Enhanced dependency management through Pants dependency inference, providing better build and development workflows.
    * **Enhanced Data Validation**: Improved evaluations reporting for insufficient data in array components, better indicating invalid data paths.
    * **Evaluation Performance Statistics Optimization**: Long model response times from API throttling are now omitted from performance statistics in evaluation framework for more accurate metrics.

* **Technology Stack Modernization**:
    * **LlamaStack 0.2.20 Upgrade**: Updated to the latest LlamaStack version (0.2.20) for improved performance and new capabilities.
    * **Python Version Support Update**: **Dropped Python 3.11 support** and now officially support  **Python 3.12 and 3.13**, focusing on the latest language features and performance improvements.


### Known Issues or Limitations

* **Python 3.11 Compatibility**: **Python 3.11 support has been dropped** in this release. Users must upgrade to Python 3.12 or 3.13 to use this version.

---

## Release Notes - Version 0.1.0

This initial release establishes the foundation for Next Gen UI, a powerful AI-driven UI agent. It introduces core capablities including component rendering, data transformation, and robust evaluation mechanisms. We've introduced support for multiple Python versions, integrated with Red Hat Design System (RHDS) for enhanced UI consistency, and provided a developer console for improved testing and debugging.

### Key Features and Benefits

* **Expanded Python Version Support**: We now officially support **Python versions 3.11, 3.12, and 3.13**, ensuring broader compatibility and allowing you to leverage the latest language features and performance improvements.
* **Enhanced UI Component Handling**:
    * **Red Hat Design System (RHDS) Integration**: Initial components like **One-Card, Image, and Video** now utilize RHDS for consistent and modern rendering. This ensures a cohesive visual experience across applications.
    * **Modular Data Transformation**: The data transformation process has been fully updated to use a new componentized system, making it more robust, testable, and easier to manage.
    * **Improved LLM Prompting**: The system now allows for switching between supported and all components in the LLM system prompt, offering more control over the AI's component selection.
* **Robust Evaluation Framework**:
    * **Comprehensive Evaluation Dataset Generation**: We've implemented the generation of evaluation datasets to rigorously test the AI component selection functionality.
    * **"Warn Only" Evaluation Items**: A new feature allows for "warn only" items in evaluation datasets. These items run when requested and report problems as warnings instead of errors, providing more granular feedback during testing.
    * **Default Evaluation Scope**: Evaluations now run by default only for implemented and supported UI components, streamlining the testing process and focusing on relevant areas.
* **Developer Experience Improvements**:
    * **Streamlit-based Developer Console**: A new and improved **Streamlit GUI app** serves as a **Developer Console**, allowing you to visualize input and mocked LLM data, and providing a powerful environment for testing and debugging agent behavior.
    * **Updated Documentation**: New chapters have been added to the User Guide, including detailed sections on **Architecture** and **Input Data**, to help you get started and understand the system better.
    * **Improved VS Code Integration**: Enhancements to VS Code settings provide better auto-completion and default interpreter support, along with improved Pytest integration.
* **Agent Core Enhancements**:
    * **ACP Agent PoC & BeeAI Inference**: This release includes a Proof of Concept for the ACP Agent with BeeAI inference, demonstrating advanced agent capabilities.
    * **LLM Response JSON Validation**: Robust JSON validation has been implemented for LLM responses, ensuring data integrity and consistency.
    * **Llama Stack Integration**: The Llama Stack integration has been updated to use the inference API, improving performance and reliability.

### Known Issues or Limitations

* **Firefox Compatibility with Streamlit GUI**: The auto-height feature in the Streamlit GUI application may experience display issues when viewed in Firefox. A workaround has been implemented, but full compatibility is still under review.
* **Chart Components**: Unimplemented chart components have been removed from the LLM system prompt. Full support for chart rendering will be addressed in future releases.
* **Llama-stack-client Dependency**: While the `llama-stack-client` dependency has been relaxed to `>=0.1.9`, the current lock file pins the version to `0.1.9`. Users might need to manually adjust their dependencies if they encounter conflicts with other libraries requiring a different `llama-stack-client` version.

---
