# Release Notes

---

## Release Notes - Version 0.4.0

This release marks a significant milestone in expanding Next Gen UI's integration capabilities and evaluation framework. The highlight is the **developer preview of Agent-to-Agent (A2A) protocol support**, enabling seamless agent interoperability. We've also introduced powerful LLM fine-tuning capabilities, enhanced our evaluation framework with LLM-as-a-Judge functionality and multi-provider support, and significantly improved configuration flexibility. This release continues our commitment to production readiness with Python 3.14 support, comprehensive configuration options, and streamlined component handling.

### Key Features and Benefits

* **Agent-to-Agent (A2A) Protocol Support (Developer Preview)**:
    * **A2A Server Implementation**: Introduced comprehensive A2A protocol support with standalone server, package, and container image, enabling agents to communicate and collaborate with each other (NGUI-223).
    * **Enhanced A2A Configuration**: A2A agent card and skill information can now be fine-tuned directly in YAML config files for better discoverability and documentation (NGUI-497).
    * **Improved Input Processing**: Enhanced A2A agent input processing with comprehensive documentation for easier integration (NGUI-518).
    * **Unified Configuration**: MCP and A2A server configurations have been unified for consistent deployment and management experience (NGUI-496).

* **LLM Fine-tuning and Evaluation Framework**:
    * **Fine-tuning Pipeline**: Added Google Colab notebook with comprehensive LLM LoRA fine-tuning pipeline, enabling model customization for specific use cases (NGUI-507).
    * **LLM-as-a-Judge Evaluation**: Introduced LLM-as-a-Judge evaluation methodology with categorical outputs and CLI flag support for automated quality assessment.
    * **Multi-Provider Support**: Added Anthropic/Claude API support in both JUDGE_API_PROVIDER for evaluation and general agent operations, expanding model choice flexibility.
    * **GitLab CI/CD Integration**: Implemented GitLab CI/CD pipeline for automated LLM evaluation tests, ensuring continuous quality monitoring.

* **Enhanced Configuration and Customization**:
    * **MCP Tools Fine-tuning**: Added ability to fine-tune MCP tool descriptions in agent config files, improving LLM tool selection accuracy (NGUI-509).
    * **Component Configuration Enhancement**: Input data types now included in component JSON for better frontend customization support (NGUI-526).
    * **Session Management**: Added `session_id` argument support in MCP tools for better session tracking and state management (NGUI-501).
    * **Available Fields Metadata**: Agent output now includes list of all available fields for table and set-of-cards components, improving dynamic UI rendering (NGUI-446).

* **Technology Stack Modernization**:
    * **Python 3.14 Support**: Added official support for Python 3.14, staying current with the latest language features and improvements (NGUI-465).
    * **FastMCP 2.13 Upgrade**: Updated to FastMCP version 2.13 for enhanced MCP functionality and performance (NGUI-463).
    * **Dependency Management**: Updated Commitizen version with pinned GitHub actions for more reliable CI/CD operations (NGUI-490).

* **Streamlined Architecture**:
    * **Removed Deprecated Features**: 
        - Removed deprecated ACP agent as the ACP protocol itself has been deprecated (NGUI-467).
        - Removed supported-only components configuration, simplifying component management (NGUI-499).
    * **Dependency Cleanup**: Cleaned up Pants dependencies for e2e-server, improving build performance and maintainability.

### Known Issues or Limitations

* **A2A Protocol Status**: The Agent-to-Agent (A2A) protocol support is currently in **Developer Preview** status. While functional, the API may evolve based on community feedback and real-world usage patterns. Production deployments should carefully evaluate stability requirements.

* **LLM Fine-tuning Requirements**: The LLM fine-tuning pipeline requires Google Colab or equivalent environment with GPU support. Local execution may require significant computational resources.

* **Multi-Provider Configuration**: When using multiple AI providers (e.g., different providers for agent operations vs. evaluation), ensure proper API key configuration for each provider to avoid authentication issues.

---

## Release Notes - Version 0.3.0

This release represents a major advancement for Next Gen UI, focusing on robustness, reliability, and production readiness. We've improved the core agent API to provide better error handling and parallel processing capabilities, migrated to FastMCP for enhanced MCP functionality, and introduced a comprehensive input data transformation framework. This release also brings significant improvements to all AI framework/protocol implementations, better configuration management, and production deployment support.

### Key Features and Benefits

* **Model Context Protocol (MCP) Enhancements**:
    * **MCP Server Status change**: MCP server matured from TechPreview and is Supported (NGUI-472)
    * **MCP Server Refactoring**: Refactored to use the new agent API with improved error handling and parallel processing (NGUI-453)
    * **MCP SDK update**: Migrated to FastMCP version 2.12.5 (NGUI-396).
    * **Component Configuration Return**: MCP tools now return component configuration, providing better context for UI rendering (NGUI-426).
    * **Structured Data Support**: Added comprehensive support for structured data and LLM-handled data in MCP operations (NGUI-432).
    * **Improved Tool Descriptions**: Enhanced MCP tool descriptions for better LLM understanding and more accurate tool selection (NGUI-374).
    * **YAML Configuration**: Added support for YAML file configuration in MCP with ability to handle multiple YAML files (NGUI-362).
    * **Better Error Handling**: Configured MCP to raise exceptions on errors for faster debugging and more reliable operation (NGUI-387).

* **Input Data Transformation Framework**:
    * **Extensible Architecture**: Introduced a comprehensive pluggable input data transformation framework, allowing flexible data processing (NGUI-355).
    * **Multiple Data Formats Supported OOTB**:
        - **JSON Transformer**: JSON data support
        - **YAML Transformer**: YAML data support (NGUI-355).
        - **CSV Transformers**: Added CSV input data transformers for tabular data processing (NGUI-391).
        - **Fixed Width Columns Table Transformer**: Specialized transformer for fixed-width columnar data formats (NGUI-356).
        - **No-op Transformer**: Added `noop` transformer for pass-through scenarios (NGUI-407).
    * Added ability to configure default input data transformer, but also transformers for individual input data types (NGUI-405).
    * **Smart Data Wrapping**: Implemented automatic wrapping of JSON input data with problematic structures for improved LLM inference (NGUI-354).

* **Core Agent Improvements**:
    * **Improved Error Handling**: Redesigned core agent API with robust error handling mechanisms, ensuring graceful failure recovery and better error reporting across all AI framework/protocol implementations.
    * **Parallel Processing with Immediate Results**: Architecture now supports parallel processing with immediate result return, improving performance for concurrent operations.
    * **Enhanced Schema**: Improved configuration schema with better support for "enum-like" options, providing clearer configuration validation (NGUI-394).
    * **Pre-configured Components**: Introduced ability to use dynamic components with pre-defined configuration per input data type (NGUI-364).
    * **Enhanced Component Specs**: Exported and documented table and set-of-cards JSON specifications (NGUI-380).
    * **Test App Split Architecture**: Redesigned NGUI e2e test app architecture with updated deployment strategy for better scalability (NGUI-330).
    * **Improved Testing**: Enhanced pytest configuration to fail on unknown markers and fixed missing dependencies (NGUI-386).

* **AI framework/protocol Implementation Updates**:
    * **LangGraph Agent Enhancement**: Updated to use the new core agent API with improved error handling and parallel processing flow (NGUI-451).
    * **LlamaStack Agent Improvements**: Leverages new core agent API for better error handling and parallel processing with immediate result return (NGUI-452).
    * **ACP Agent Deprecation**: ACP Agent is now officially deprecated as ACP protocol itself is deprecated (NGUI-455).

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
