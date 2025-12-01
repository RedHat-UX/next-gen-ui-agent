# Server Architecture

## Request Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Request                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         main.py                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  FastAPI App + CORS Middleware                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │
                             ▼
┌──────────────────────────┐
│   routes/health.py       │
│                          │
│  GET /health             │
│  GET /model-info         │
└──────────────────────────┘

                      ┌──────────────────────────────────┐
                      │     routes/generate.py           │
                      │                                  │
                      │  POST /generate                  │
                      └────────┬─────────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
          ┌──────────────────┐  ┌──────────────────────┐
          │  Inline Data     │  │  Movies Agent        │
          │  Path            │  │  Path                │
          └──────┬───────────┘  └──────┬───────────────┘
                 │                     │
                 │  ┌──────────────────┘
                 │  │
                 ▼  ▼
          ┌─────────────────────────────────┐
          │      NGUI Agent                 │
          │  (one-step or two-step)         │
          └──────────────┬──────────────────┘
                         │
                         ▼
          ┌─────────────────────────────────┐
          │   Validation & Metadata         │
          │   Extraction                    │
          └──────────────┬──────────────────┘
                         │
                         ▼
          ┌─────────────────────────────────┐
          │      JSON Response              │
          │  { response, metadata }         │
          └─────────────────────────────────┘
```

## Module Dependencies

```
main.py
  └─▶ routes/
       ├─▶ health.py
       │    ├─▶ config (MODEL, BASE_URL)
       │    └─▶ llm (llm)
       │
       └─▶ generate.py
            ├─▶ config (MODEL, BASE_URL, NGUI_CONFIG)
            ├─▶ models (GenerateRequest)
            ├─▶ agents (movies_agent, ngui_agents)
            └─▶ utils (inline_data, validation, response)

config.py
  └─▶ dotenv, logging, os

llm.py
  ├─▶ config (MODEL, BASE_URL, API_KEY)
  ├─▶ httpx (sync_client, async_client)
  └─▶ ChatOpenAI

agents/
  ├─▶ movies.py
  │    ├─▶ llm (llm)
  │    ├─▶ langgraph (create_react_agent)
  │    └─▶ next_gen_ui_testing (search_movie, get_all_movies)
  │
  └─▶ ngui.py
       ├─▶ llm (llm)
       ├─▶ next_gen_ui_agent (AgentConfig, AgentConfigDataType)
       └─▶ next_gen_ui_langgraph (NextGenUILangGraphAgent)

utils/
  ├─▶ inline_data.py
  │    └─▶ langchain_core.messages
  │
  ├─▶ response.py
  │    (no dependencies)
  │
  └─▶ validation.py
       └─▶ utils.response (create_error_response)
```

## Data Flow: Generate Endpoint

### Step 1: Request Validation
```
GenerateRequest
  ├─▶ prompt: str (required)
  ├─▶ strategy: "one-step" | "two-step"
  ├─▶ data: Optional[Any]
  └─▶ data_type: Optional[str]
```

### Step 2: Data Source Selection
```
if request.data is not None:
  ┌──────────────────────────────────┐
  │  Inline Data Path                │
  │                                  │
  │  1. Validate JSON                │
  │  2. build_inline_messages()      │
  │  3. Create mock movie_response   │
  └──────────────┬───────────────────┘
                 │
else:            │
  ┌──────────────┴───────────────────┐
  │  Movies Agent Path               │
  │                                  │
  │  1. Invoke movies_agent          │
  │  2. Extract tool calls           │
  │  3. Serialize agent_messages     │
  └──────────────┬───────────────────┘
                 │
                 ▼
  ┌──────────────────────────────────┐
  │  movie_response: dict            │
  │  { messages: [Human, AI, Tool] } │
  └──────────────┬───────────────────┘
```

### Step 3: NGUI Agent Invocation
```
movie_response
  │
  ▼
┌───────────────────────────────────────┐
│  selected_agent["graph"].ainvoke()    │
│                                       │
│  Strategy: one-step | two-step        │
│  Config: NGUI_CONFIG                  │
└──────────────┬────────────────────────┘
               │
               ▼
┌───────────────────────────────────────┐
│  ngui_response: dict                  │
│  {                                    │
│    renditions: [Rendition],           │
│    components: [ComponentSelection],  │
│    ...                                │
│  }                                    │
└──────────────┬────────────────────────┘
```

### Step 4: Validation & Extraction
```
ngui_response
  │
  ▼
┌───────────────────────────────────────┐
│  validate_ngui_response()             │
│                                       │
│  1. Check response is dict            │
│  2. Validate renditions exist         │
│  3. Extract rendition.content         │
│  4. Parse JSON                        │
│                                       │
│  Returns: (component_json_str, error) │
└──────────────┬────────────────────────┘
               │
               ▼
┌───────────────────────────────────────┐
│  extract_component_metadata()         │
│                                       │
│  Extracts:                            │
│  - componentType                      │
│  - reason, confidence                 │
│  - strategy                           │
│  - model info                         │
│  - dataTransform (transformer, fields)│
│  - llmInteractions                    │
│  - agentMessages                      │
└──────────────┬────────────────────────┘
```

### Step 5: Response
```
{
  "response": {
    // Component configuration (parsed JSON)
    "componentType": "card" | "chart" | ...,
    "fields": [...],
    ...
  },
  "metadata": {
    "reason": "User wants to visualize...",
    "confidence": 0.95,
    "componentType": "card",
    "strategy": "one-step",
    "model": {
      "name": "llama3.2:3b",
      "baseUrl": "http://localhost:11434/v1"
    },
    "dataTransform": {
      "transformerName": "default",
      "jsonWrappingField": null,
      "fieldCount": 5,
      "fields": [...]
    },
    "llmInteractions": [...],
    "agentMessages": [...]
  }
}
```

## Configuration Flow

```
Environment Variables (.env)
  ├─▶ LLM_MODEL
  ├─▶ LLM_BASE_URL
  └─▶ LLM_API_KEY

       │
       ▼
   config.py
       │
       ├─▶ Validates required vars
       ├─▶ Sets up logging
       ├─▶ Exports constants
       │     ├─▶ MODEL
       │     ├─▶ BASE_URL
       │     ├─▶ API_KEY
       │     └─▶ NGUI_CONFIG
       │
       ▼
    llm.py
       │
       ├─▶ Creates httpx clients
       ├─▶ Initializes ChatOpenAI
       ├─▶ Tests connection
       └─▶ Exports llm instance
              │
              ├─▶ agents/movies.py
              ├─▶ agents/ngui.py
              └─▶ routes/health.py
```

## Error Handling Flow

```
Exception occurs
  │
  ▼
┌───────────────────────────────────────┐
│  create_error_response()              │
│                                       │
│  Parameters:                          │
│  - error: str (category)              │
│  - details: str (message)             │
│  - raw_response: Optional[Any]        │
│  - suggestion: Optional[str]          │
│  - agent_messages: Optional[list]     │
└──────────────┬────────────────────────┘
               │
               ▼
{
  "error": "Invalid JSON configuration",
  "details": "JSON parse error: ...",
  "raw_response": "...",
  "suggestion": "The component configuration...",
  "metadata": {
    "agentMessages": [...]
  }
}
```

## Component Selection Strategies

### One-Step Strategy
```
┌────────────────────────────────────────┐
│  Single LLM Call                       │
│                                        │
│  Input: User prompt + data             │
│  Output: Component type + config       │
│                                        │
│  Faster, less accurate                 │
└────────────────────────────────────────┘
```

### Two-Step Strategy
```
┌────────────────────────────────────────┐
│  Step 1: Component Selection           │
│                                        │
│  LLM Call 1:                           │
│  Input: User prompt + data             │
│  Output: Component type + reasoning    │
└──────────────┬─────────────────────────┘
               │
               ▼
┌────────────────────────────────────────┐
│  Step 2: Component Configuration       │
│                                        │
│  LLM Call 2:                           │
│  Input: Component type + data          │
│  Output: Component config              │
│                                        │
│  Slower, more accurate                 │
└────────────────────────────────────────┘
```

## Key Design Principles

1. **Single Responsibility**: Each module has one clear purpose
2. **Dependency Injection**: Agents and utilities are imported, not created inline
3. **Error Handling**: Standardized error responses with debugging metadata
4. **Separation of Layers**:
   - Routes: HTTP layer (request/response)
   - Agents: Business logic (LangGraph workflows)
   - Utils: Cross-cutting concerns (validation, formatting)
   - Config: Configuration and initialization
5. **Testability**: Pure functions where possible, easy to mock dependencies
6. **Extensibility**: Easy to add new routes, agents, or utilities

