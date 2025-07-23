# Release Notes

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
