# Next Gen UI Agent – open-source engine for AI-generated UI

**UI Agent uses LLMs to generate safe UI components that visualize rich backend data shaped for user prompt.**

The problem UI Agent solves is: **how to intelligently visualize rich backend data in AI assistant GUIs?**

In upcoming releases, the agent will also maintain UI state and layouts to keep UI flow consistent across chats, and add other capabilities. Stay tuned ;-)

## Why use Next Gen UI Agent?

- `Rich user experience` – Extend text-based LLM chats with AI-generated GUI components such as cards, tables, charts, video players, and image galleries.
- `Secure UI rendering` – LLM doesn't generate UI code, but declarative component descriptions, rendered using secure native renderers
- `Framework agnostic` – Choose the AI framework/protocol and UI component framework you prefer.
- `AI framework integration` – Seamless integration with MCP and A2A and others.

Example of a rich card component that includes an image and values from structured data:

![Card UI Component](img/data_ui_block_card.png "Card UI Component")

## How to use Next Gen UI Agent

- Start with the [Architecture guide](guide/architecture.md) to see how to integrate the agent into your AI assistant.
- Check the [LangGraph & Web Components quickstart](quickstart/langgraph_web_components.md).
- Run the [LangGraph Movies assistant example](example/langgraph_movies.md) to see the UI agent in action.