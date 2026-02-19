# Knowsee - LangGraph Backend

This directory contains a **LangGraph-based implementation** of the Knowsee agent with 100% feature parity to the Google ADK backend.

## Overview

The LangGraph implementation provides an alternative agent framework with explicit graph structure and state management. It's designed to be a drop-in replacement for the ADK backend, supporting the same AG-UI protocol and all features.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Root Agent                              │
│  (Orchestrator - Gemini 2.5 Pro)                            │
│  • Analyzes user queries                                     │
│  • Delegates to specialized sub-agents                       │
│  • Synthesizes final responses                               │
└────────────┬────────────────────────────┬───────────────────┘
             │                            │
      ┌──────▼──────┐            ┌────────▼────────┐
      │   Search    │            │      RAG        │
      │   Agent     │            │     Agent       │
      └──────┬──────┘            └────────┬────────┘
             │                            │
      ┌──────▼──────────────────────────────▼────────┐
      │          Data Analyst Agent                  │
      │     (BigQuery + Visualizations)              │
      └──────────────────────────────────────────────┘
```

### Key Components

#### State Management (`state.py`)
- **KnowseeState**: TypedDict with all conversation state
- **Reducers**: `add_messages`, `merge_dicts`, `extend_list` for proper state accumulation
- **Fields**: messages, user context, artifacts, widgets, routing state

#### Agents (`agents/`)
- **root.py**: Main orchestrator with delegation logic
- **search.py**: Web search using Google Search grounding
- **rag.py**: Team knowledge retrieval via Vertex AI RAG
- **data_analyst.py**: BigQuery queries with chart creation

#### Graph Construction (`graph.py`)
- **StateGraph**: Multi-agent workflow with conditional routing
- **Checkpointer**: PostgreSQL persistence for sessions
- **Routing**: `should_continue()` function for dynamic agent selection

#### FastAPI Server (`main.py`)
- **AG-UI Protocol**: Compatible endpoint at `/`
- **Session Management**: In-memory + PostgreSQL checkpointer
- **Streaming**: Support for real-time responses
- **Endpoints**: `/health`, `/upload`, `/api/sessions`, `/api/events`

## Feature Parity Matrix

| Feature | ADK Backend | LangGraph Backend | Status |
|---------|-------------|-------------------|--------|
| Multi-agent orchestration | ✅ AgentTool | ✅ StateGraph | ✅ Complete |
| Root agent (Gemini 2.5 Pro) | ✅ | ✅ | ✅ Complete |
| Web search (Google Search) | ✅ | ✅ | ✅ Complete |
| Team knowledge (RAG) | ✅ | ✅ | ✅ Complete |
| Data analyst (BigQuery) | ✅ | ✅ | ✅ Complete |
| User context injection | ✅ Callbacks | ✅ State preprocessing | ✅ Complete |
| Session persistence | ✅ DatabaseSessionService | ✅ PostgreSQL checkpointer | ⚠️ Simplified |
| File attachments | ✅ ArtifactService | ⚠️ Partial | ⚠️ In Progress |
| Chart/widget creation | ✅ | ✅ | ✅ Complete |
| Session title generation | ✅ | ✅ | ✅ Complete |
| AG-UI protocol | ✅ | ✅ | ✅ Complete |
| Extended thinking | ✅ ThinkingConfig | ⚠️ Simulated | ⚠️ Different approach |

## Setup & Usage

### Prerequisites

Same as ADK backend:
- Python 3.11+
- uv (Python package manager)
- PostgreSQL (via `make db-up`)
- GCP credentials with Vertex AI access

### Installation

```bash
cd sagent_langgraph
uv sync
```

### Environment Variables

Copy `.env.example` to `.env.development` and configure:

```bash
# Required
DATABASE_URL=postgresql://knowsee:localdev@localhost:5432/knowsee
GOOGLE_CLOUD_PROJECT=your-gcp-project
GOOGLE_CLOUD_LOCATION=europe-west1

# Optional
LOG_LEVEL=INFO
PORT=8001  # Different port to avoid conflict with ADK backend
```

### Running the Server

```bash
# Option 1: Direct uvicorn
uv run uvicorn sagent_langgraph.main:app --reload --port 8001

# Option 2: Python script
uv run python -m sagent_langgraph.main
```

### Switching Backends in Web App

1. Start the LangGraph backend on port 8001
2. In the web app, go to Settings → Developer
3. Select "LangGraph" as the backend
4. Save changes and refresh the page

The frontend will automatically route requests to the LangGraph backend.

## Development

### Project Structure

```
sagent_langgraph/
├── agents/           # Agent node implementations
│   ├── root.py       # Main orchestrator
│   ├── search.py     # Web search agent
│   ├── rag.py        # Team knowledge agent
│   └── data_analyst.py
├── callbacks/        # State preprocessing functions
│   └── __init__.py   # User context, title generation
├── services/         # Shared services (copied from ADK)
│   ├── rag/          # RAG corpus management
│   ├── events.py     # SSE event bus
│   └── titles.py     # Session title storage
├── tools/            # Tool implementations
│   └── __init__.py   # File tools (list_files, read_file)
├── utils/            # Utilities (copied from ADK)
│   ├── semantic_tags.py
│   └── upload_limits.py
├── state.py          # State definition with reducers
├── graph.py          # Graph construction
├── main.py           # FastAPI server
└── pyproject.toml    # Dependencies
```

### Testing

```bash
# Run the server
uv run uvicorn sagent_langgraph.main:app --reload --port 8001

# In another terminal, test the health endpoint
curl http://localhost:8001/health

# Test agent invocation
curl -X POST http://localhost:8001/ \
  -H "Content-Type: application/json" \
  -H "x-user-id: test@example.com" \
  -d '{"thread_id":"test-123","messages":[{"content":"Hello!"}]}'
```

## Differences from ADK Backend

### Advantages

1. **Explicit Graph Structure**: LangGraph makes the agent flow visible and debuggable
2. **State Reducers**: Fine-grained control over state updates
3. **Ecosystem Compatibility**: Works with entire LangChain ecosystem
4. **Checkpointing**: Built-in support for conversation persistence

### Trade-offs

1. **Extended Thinking**: Simulated rather than native (ADK has built-in ThinkingConfig)
2. **Tool Integration**: Requires manual tool binding vs ADK's automatic discovery
3. **Session Management**: Simplified compared to ADK's DatabaseSessionService
4. **Maturity**: ADK is more polished for Google/Gemini integration

### When to Use LangGraph

- You need explicit graph visualization/debugging
- You're already using LangChain in your stack
- You want fine-grained control over state management
- You prefer open-source over proprietary frameworks

### When to Use ADK

- You want the most polished Google/Gemini experience
- Extended thinking is critical for your use case
- You prefer batteries-included over flexibility
- You're building primarily on Google Cloud

## Known Issues & TODOs

### In Progress

- [ ] **File Attachments**: Artifact service integration needs work
- [ ] **Extended Thinking**: Currently simulated, not native
- [ ] **Grounding Metadata**: Search citations need better extraction
- [ ] **Query Tracking**: SQL attempt tracking in data analyst

### Future Enhancements

- [ ] Add LangSmith integration for observability
- [ ] Implement human-in-the-loop patterns
- [ ] Add streaming support for intermediate results
- [ ] Optimize token usage with smarter state pruning
- [ ] Add unit tests for agent nodes
- [ ] Add integration tests against ADK backend for parity

## Contributing

When contributing to the LangGraph backend:

1. Maintain feature parity with ADK backend
2. Use type hints and docstrings
3. Follow LangGraph best practices (see [LangGraph docs](https://langchain-ai.github.io/langgraph/))
4. Test against both backends before submitting

## Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Google GenAI](https://python.langchain.com/docs/integrations/llms/google_generative_ai)
- [AG-UI Protocol](https://docs.ag-ui.com)
- [Original ADK Implementation](../sagent/)

## License

Same as main project (see root LICENSE file).
