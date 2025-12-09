# Next Gen UI Agent Testing

This module is part of the [Next Gen UI Agent project](https://github.com/RedHat-UX/next-gen-ui-agent).

[![Module Category](https://img.shields.io/badge/Module%20Category-Testing/Evaluation-darkmagenta)](https://github.com/RedHat-UX/next-gen-ui-agent)
[![Module Status](https://img.shields.io/badge/Module%20Status-Supported-green)](https://github.com/RedHat-UX/next-gen-ui-agent)

Library for testing support

## Components

* `model.py` - `MockedInference` to mock agent's `InferenceBase` in unit tests
* `agent_testing.py` - Test setup for renderer testing with mock agents
* `data_set_movies.py` - Comprehensive movie database with tool functions for E2E testing
  - `MOVIES_DB`: Rich dataset with 6 movies including box office data, ratings, awards, and weekly performance
  - `search_movie(title)`: Search for a specific movie by title
  - `get_all_movies(**filters)`: Get movies with optional filtering by director, genre, actor, year, rating
  - `find_movie(title)`: Legacy function for backward compatibility
* `movies_agent_example.py` - E2E testing agent demonstrating LangGraph ReAct agent with movie tools
  - `create_movies_agent(llm, system_prompt)`: Factory function to create a movies agent
  - `run_example()`: Runnable example demonstrating the agent in action
* `data_after_transformation` - Distinct types of `ComponentData` based on movies data for use in tests

## Usage

### For Renderer Testing
```python
from next_gen_ui_testing.agent_testing import create_mock_agent
```

### For E2E Testing
```python
from next_gen_ui_testing.data_set_movies import get_all_movies, search_movie
from next_gen_ui_testing.movies_agent_example import create_movies_agent

# Create agent
movies_agent = create_movies_agent(llm)
agent_graph = movies_agent.build_graph()

# Run query
result = await agent_graph.ainvoke({"messages": [("user", "Show me sci-fi movies")]})
```

### Running the Example
```bash
cd libs/next_gen_ui_testing
export LLM_MODEL="your-model"
export LLM_BASE_URL="http://your-api/v1"
export LLM_API_KEY="your-key"
python -m next_gen_ui_testing.movies_agent_example
```
