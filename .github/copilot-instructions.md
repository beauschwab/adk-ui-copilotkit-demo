# Knowsee - GitHub Copilot Instructions

## Project Overview

**Knowsee** is a fullstack reference implementation for building AI assistants with Google Agent Development Kit (ADK) and CopilotKit using AG-UI protocol, A2A (Agent-to-Agent) patterns, and Generative UI. It demonstrates multi-agent conversational AI with RAG (Retrieval-Augmented Generation), web search, and data analytics capabilities.

**Key Value Proposition:**
- Production-ready enterprise knowledge assistant
- Multi-agent orchestration with isolated contexts
- RAG with team-scoped permissions
- Real-time streaming via AG-UI protocol
- Interactive generative UI components

## Architecture

### High-Level Stack
```
Frontend: Next.js 16 + CopilotKit + AG-UI Client
Backend: FastAPI + Google ADK (Python) + AG-UI Adapter
Auth: Better Auth (email/password, OTP, TOTP 2FA)
Database: PostgreSQL (local Docker, Cloud SQL in prod)
AI: Vertex AI (Gemini 2.5 Pro/Flash, RAG Engine)
Infrastructure: Terraform + GCP Cloud Run
```

### Component Structure

**Backend (`sagent/`):**
- `main.py` - FastAPI server exposing ADK agent via AG-UI protocol
- `agents/` - Multi-agent architecture
  - `root.py` - Main orchestrator (Gemini 2.5 Pro with extended thinking)
  - `search.py` - Web search sub-agent (Google Search grounding)
  - `rag/agent.py` - Team knowledge sub-agent (Vertex AI RAG)
  - `data_analyst/` - BigQuery SQL execution and visualization
- `callbacks/` - Before/after LLM hooks for context injection
- `services/rag/` - RAG corpus sync and configuration
- `instructions/` - Agent prompt templates (Markdown)
- `tools/` - Custom ADK tools for file operations
- `converters/` - File format conversion (Office → Markdown)

**Frontend (`web/`):**
- `src/app/api/copilotkit/` - AG-UI bridge to ADK backend
- `src/app/chat/` - Chat interface pages
- `src/components/chat/` - Modular chat UI components
- `src/components/charts/` - Recharts visualizations
- `src/lib/db/` - Drizzle ORM schema and migrations
- Authentication via Better Auth with session management

### Agent Architecture

**Root Agent** (`knowsee_agent`):
- Model: Gemini 2.5 Pro with extended thinking (2048 token budget)
- Tools: file operations, AgentTool delegations
- Callbacks: user context injection, artifact injection, session title generation
- Sub-agents via AgentTool pattern (no namespace contamination):
  - **Web Search Agent**: Google Search with grounding metadata
  - **Team Knowledge Agent**: Vertex AI RAG with permission scoping
  - **Data Analyst Agent**: BigQuery queries with chart widgets

**A2A (Agent-to-Agent) Composition:**
- AgentTool wraps sub-agents for delegation
- Isolated contexts prevent namespace pollution
- Hierarchical orchestration pattern

### Data Flow

1. User sends message → CopilotKit streams to `/api/copilotkit` with `x-user-id` header
2. AG-UI bridge forwards to ADK backend via HttpAgent
3. Context injection loads user's teams and RAG corpora into state
4. Root agent delegates to sub-agents (RAG, search, analytics)
5. Gemini synthesizes responses with inline citations
6. Streaming response flows back through AG-UI to CopilotKit UI

## Development Workflow

### Prerequisites
- Node.js 20+
- Python 3.11+
- uv (Python package manager)
- Docker Desktop
- gcloud CLI (authenticated)

### Common Commands

**Development:**
```bash
make install          # Install all dependencies
make dev              # Start backend + frontend (port 8000, 3000)
make dev-debug        # Run with DEBUG logging
```

**Code Quality:**
```bash
make check            # Full pre-commit check (format + lint + types)
make fmt              # Format all code (ruff + biome + prettier)
make lint             # Run linters
```

**Database:**
```bash
make db-up            # Start local Postgres (Docker)
make db-migrate       # Apply migrations
make db-generate      # Generate Drizzle migration files
make db-ui            # Start CloudBeaver UI (localhost:8978)
```

**Testing:**
```bash
make test-e2e         # Run Playwright E2E tests (headless)
make test-e2e-ui      # Run tests with interactive UI
```

**GCP/Deployment:**
```bash
make gcp-login        # Authenticate with GCP
make tf-bootstrap     # First-time Terraform setup
make docker-build     # Build images
make docker-push      # Push to Artifact Registry
```

### Environment Configuration

**Backend (`sagent/.env.development`):**
- `GOOGLE_CLOUD_PROJECT` - GCP project ID (required for Vertex AI)
- `GOOGLE_CLOUD_LOCATION` - GCP region (default: `europe-west1`)
- `GOOGLE_GENAI_USE_VERTEXAI=TRUE` - Use Vertex AI (not API key)
- `DATABASE_URL` - Postgres connection string
- `RAG_SIMILARITY_TOP_K` - RAG retrieval count (default: 10)

**Frontend (`web/.env.development`):**
- `AGENT_URL` - Backend URL (default: `http://localhost:8000`)
- `NEXT_PUBLIC_COPILOTKIT_PUBLIC_KEY` - CopilotKit public key
- `BETTER_AUTH_SECRET` - Session encryption key (generate with `openssl rand -base64 32`)
- `BETTER_AUTH_URL` - Auth callback URL (default: `http://localhost:3000`)
- `DATABASE_URL` - Postgres connection string
- `MAILGUN_*` - Email OTP (required for verification)

## Coding Standards & Conventions

### Python (Backend)
- **Linter:** Ruff (configured in `pyproject.toml`)
- **Style:**
  - Line length: 88 characters
  - Quote style: double quotes
  - Indentation: 4 spaces
- **Import order:** E, W, F, I, UP, B, SIM rules enabled
- **Docstrings:** Google-style docstrings for modules, classes, and functions
- **Type hints:** Required for function signatures
- **Error handling:** Explicit try/except blocks (avoid contextlib.suppress)
- **Async:** Use async/await for I/O operations

### TypeScript (Frontend)
- **Linter:** ESLint + Biome
- **Formatter:** Biome + Prettier (with Tailwind plugin)
- **Style:**
  - 2 spaces indentation
  - Semicolons required
  - Single quotes for strings
- **React patterns:**
  - Use hooks (functional components)
  - Server components by default (add 'use client' when needed)
  - Shadcn/ui components for UI primitives
- **Next.js conventions:**
  - App Router (src/app directory)
  - Server actions for mutations
  - Route handlers for API endpoints
- **State management:** React hooks + CopilotKit context

### File Organization
- One component per file
- Co-locate related files (types, styles, tests)
- Use barrel exports (`index.ts`) for public APIs
- Keep instructions in `.md` files under `sagent/instructions/`

### Commit Conventions
Follow conventional commits (see `.gitmessage.txt`):
```
<type>(<scope>): <subject>

Types: feat, fix, docs, style, refactor, perf, test, chore
```

## Key Technical Patterns

### AG-UI Protocol Integration
- **Frontend:** HttpAgent connects CopilotKit to ADK backend
- **Backend:** `add_adk_fastapi_endpoint` wraps ADK agent with AG-UI adapter
- **Headers:** User ID passed via `x-user-id` header from auth session
- **Streaming:** Bidirectional SSE (Server-Sent Events) for real-time updates

### Agent Callbacks
- **Before Model:** `inject_user_context`, `inject_artifact_content`
- **After Model:** `capture_grounding_metadata`, `auto_generate_session_title`
- **Data Analyst:** `data_analyst_after_model_callback` for query tracking

### RAG Implementation
- **Vertex AI RAG Engine** for semantic search
- **Team-scoped corpora:** Users only access corpora their teams own
- **Sync service:** Scheduled updates from Google Drive/OneDrive
- **Permission model:** Based on team membership provider (Better Auth, Google Groups, Azure AD)

### Generative UI
- Tool calls rendered as interactive components
- Custom renderers in `web/src/components/chat/tool-call/`
- Semantic tags for thoughts, tools, and results:
  - `<thinking>` for model reasoning
  - `<tool_call>` for tool invocations
  - `<tool_result>` for tool outputs

### Session Management
- PostgreSQL stores sessions, messages, artifacts
- ADK's `DatabaseSessionService` for persistence
- Better Auth for user sessions and teams
- Session titles auto-generated from first message

## Security Considerations

### Authentication & Authorization
- Email verification required (OTP via Mailgun)
- Optional TOTP 2FA
- Team-based access control for RAG corpora
- Session encryption with `BETTER_AUTH_SECRET`

### Data Access
- Row-level security via team membership
- RAG corpora scoped to team owners
- User context injected before each LLM call
- SQL queries limited to authorized BigQuery datasets

### Secret Management
- SOPS for encrypted configuration (production)
- Never commit `.env` files
- Use GCP Secret Manager in production
- KMS encryption for Terraform state

## Testing Strategy

### E2E Tests (Playwright)
- Located in `web/e2e/`
- Test authentication flow, chat interactions, file uploads
- Run with `make test-e2e` (requires `make dev` running)
- CI/CD via GitHub Actions

### Manual Testing
- Test auth flow: signup → OTP verification → login
- Test chat: basic queries, web search, RAG, data analyst
- Test file uploads: supported formats, size limits
- Test theme toggle, session management

## Common Pitfalls & Solutions

### Backend
- **Import order:** Configure logging BEFORE importing ADK (in `main.py`)
- **Monkey patches:** Apply patches before importing patched modules (`patches/`)
- **Vertex AI region:** Ensure `GOOGLE_CLOUD_LOCATION` matches corpus region
- **User ID normalization:** Always lowercase for case-insensitive matching

### Frontend
- **Client components:** Add 'use client' for hooks, event handlers, browser APIs
- **CopilotKit props:** Pass userId via custom headers in CopilotKitProvider
- **Streaming:** Handle partial responses gracefully in UI
- **Theme:** Use next-themes with class-based dark mode

### Infrastructure
- **Database migrations:** Use Drizzle for schema changes (not manual SQL)
- **Docker networking:** Backend must access Postgres via `host.docker.internal` on Mac
- **Cloud Run:** Set min instances > 0 to avoid cold starts
- **CORS:** Configure allowed origins in FastAPI middleware

## Deployment

### GCP Setup
1. Create GCP project with billing enabled
2. Enable APIs: Vertex AI, Cloud Run, Cloud SQL, BigQuery, KMS
3. Authenticate: `make gcp-login`
4. Configure SOPS: Update `terraform/.sops.yaml` with KMS key
5. Bootstrap: `make tf-bootstrap ENV=prod`

### Terraform Workflow
- State stored in GCS bucket
- Secrets encrypted with SOPS + KMS
- Modules: `project`, `compute`, `database`
- Deploy: `make tf-apply ENV=prod`

### Monitoring
- Cloud Logging for application logs
- Cloud Monitoring for metrics
- Trace integration via OpenTelemetry (TODO)

## AI Model Configuration

### Model Selection
- **Root Agent:** Gemini 2.5 Pro (extended thinking, complex reasoning)
- **Web Search:** Gemini 2.5 Flash (fast responses)
- **Data Analyst:** Gemini 2.5 Pro (better SQL generation)
- **Team Knowledge:** Flash (fast RAG queries)

### Thinking Config
- Extended thinking enabled with budget allocation
- Thoughts included in responses for transparency
- Semantic `<thinking>` tags for frontend rendering

### Grounding
- Web search: Google Search grounding with citations
- RAG: Vertex AI RAG Engine with source attribution
- All sources embedded in responses with inline citations

## Contributing Guidelines

See [CONTRIBUTING.md](../CONTRIBUTING.md) for:
- Development setup
- Code style requirements
- Commit conventions
- PR submission process

**Key Points:**
- Run `make check` before submitting PRs
- Run `make test-e2e` to validate changes
- Solo-maintained project - response times may vary
- Be patient with review feedback

## Resources

**Documentation:**
- [Google ADK](https://github.com/google/adk-python)
- [CopilotKit](https://docs.copilotkit.ai)
- [AG-UI Protocol](https://docs.ag-ui.com)
- [Vertex AI RAG](https://cloud.google.com/vertex-ai/docs/rag-engine)
- [Better Auth](https://www.better-auth.com)

**Tools:**
- [Ruff](https://docs.astral.sh/ruff/) - Python linting/formatting
- [Biome](https://biomejs.dev/) - JavaScript linting/formatting
- [Drizzle ORM](https://orm.drizzle.team/) - Database toolkit
- [Terraform](https://www.terraform.io/) - Infrastructure as Code
- [SOPS](https://github.com/getsops/sops) - Secrets management

## Project Philosophy

**Design Principles:**
1. **Modularity:** Sub-agents as composable units via AgentTool
2. **Isolation:** A2A patterns prevent namespace pollution
3. **Explainability:** Extended thinking and source citations
4. **Security:** Team-based permissions, encrypted secrets
5. **Production-ready:** IaC, database migrations, monitoring

**Future Enhancements:**
- Scheduled RAG corpus sync from cloud storage
- Advanced chart types (scatter, heatmap, funnel)
- Multi-modal input (image analysis)
- Voice interface integration
- Plugin system for custom tools
