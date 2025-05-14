# Next Gen UI Agent

The goal of this AI agent is to generate personalised and rich UI components based on 
the user prompt, chat history and backend data provided by other agent in your assistant.

## Why use Next Gen UI?

* `Rich UI experience` - Extends simple text based LLM applications output by UI components like card, table, chart, 
video-player, image gallery etc.

* `Extensions architecture` - Developer's choice to which AI framwork to choose and which UI component framework.


TODO: Image with text + UI component chat

## Example

Simple example below of how to integrate a ReAct LangGraph agent with Next Gen UI Agent. For other frameworks see below.

```py
from langgraph.prebuilt import create_react_agent
# This code depends on pip install langchain[anthropic]

def search(query: str):
    """Call to surf the web."""
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."

agent = create_react_agent("anthropic:claude-3-7-sonnet-latest", tools=[search])
agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
)


# TODO LangGraph simple example

ngui_agent = NextGenUILangGraphAgent("anthropic:claude-3-7-sonnet-latest")
graph = agent.build_graph()
```

## AI Frameworks

For seamless integration with your AI application following frameworks are supported. 

1. [LangGraph](./libs/next_gen_ui_langgraph/)
2. [Llama-stack](./libs/next_gen_ui_llama_stack/)
3. BeeAI - TBD

Missing framework?
[Create an issue](https://github.com/RedHat-UX/next-gen-ui-agent/issues/new) please.

Other option is to use the "core" agent directly like this:

```py
from next_gen_ui_agent import NextGenUIAgent
agent = NextGenUIAgent()

# TODO Add example how to use the agent directly
```

## Running Tests

Below are detailed instructions for running your tests.

`Install Dependencies`
npm install
-Installs all project dependencies, including the internal test setup package.

1. Run All Tests (Watch Mode)
npm test
-Starts Jest in watch mode, re-running relevant tests as you save changes.

2. Run Tests Once (CI Mode)
npm run test:ci
-Executes the entire test suite a single time without watching.

3. Run a Specific Test File
You can target a single test file like so:

npm test -- src/test/components/ComponentName.test.tsx 

Or using the run keyword:

npm run test -- src/test/components/ComponentName.test.tsx 

Replace ComponentName with the actual file name you wish to test.

`NPM Scripts`
The following scripts are available via package.json:

{
  "scripts": {
    "test": "jest",
  }
}
npm test → Runs all tests in watch mode.
npm run test:ci → Runs all tests once, useful for CI pipelines.

`Test Setup Details`
Global config (e.g., @testing-library/jest-dom) is handled by setupTests.ts via our internal npm package.
Test files follow the pattern *.test.tsx or *.test.js and are placed in: tests folders

## Rendering & UI Frameworks

1. React
2. Web Components
3. PatternFly
4. Hat Design System System
5. Text - TBD

## Contributing

Follow the [CONTRIBUTING.md](./CONTRIBUTING.md)
