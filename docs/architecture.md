# Architecture

## High-Level System

BizFlow AI is a full-stack web application with a FastAPI backend, Next.js frontend, Supabase data layer, LiteLLM model routing, n8n automation, and Langfuse observability.

```text
User
  -> Next.js frontend
  -> FastAPI backend
  -> Supabase Auth, Postgres, Storage, pgvector
  -> LiteLLM providers through model_router.py
  -> n8n webhooks through n8n_service.py
  -> Langfuse traces
```

## Frontend Responsibilities

- Authenticate users via Supabase Auth.
- Present real application workflows, not mock-only screens.
- Upload documents through approved backend or Supabase flows.
- Display ingestion state, chat answers, citations, extraction results, proposal drafts, and workflow approval controls.
- Never hold server-side provider credentials.

## Backend Responsibilities

- Validate requests and enforce user ownership.
- Coordinate document ingestion.
- Run RAG retrieval and generation.
- Route all model calls through `model_router.py`.
- Route all n8n calls through `n8n_service.py`.
- Write audit-relevant events for workflow approvals and triggers.
- Emit Langfuse traces for model and RAG operations.

## Data Layer

Supabase provides:

- Auth identity
- Postgres relational data
- pgvector embeddings
- Storage for uploaded documents
- Row Level Security for user-owned records

All user-owned tables require:

- `user_id uuid not null`
- RLS enabled
- Policies scoped to `auth.uid() = user_id`
- Indexes that support user-scoped access patterns

## AI Boundary

No module should call DeepSeek, OpenAI, Claude, or LiteLLM directly except `model_router.py`.

`model_router.py` is responsible for:

- Provider selection
- Model configuration
- Retries and timeouts
- Token and cost metadata capture
- Langfuse model call instrumentation
- Consistent error handling

## Automation Boundary

No module should call n8n directly except `n8n_service.py`.

`n8n_service.py` is responsible for:

- Webhook URL lookup
- Request signing or shared-secret headers if configured
- Payload validation
- Timeout and retry policy
- Recording trigger result metadata

External workflow execution must be impossible without a stored human approval event.

## Suggested Future Backend Modules

```text
app/api/              FastAPI routers
app/core/             settings, logging, auth helpers
app/db/               database clients and repositories
app/schemas/          request and response schemas
app/services/         integration services
app/services/model_router.py
app/services/n8n_service.py
app/rag/              ingestion, chunking, retrieval, citation logic
app/tests/            backend tests
```

## Suggested Future Frontend Modules

```text
app/                  Next.js routes
components/           reusable UI components
lib/                  clients and typed API helpers
tests/                frontend tests if added
```

## Observability

Langfuse should trace:

- RAG ingestion jobs
- Retrieval queries and selected chunk IDs
- Model calls and provider routing decisions
- Proposal generation
- Metadata extraction
- Workflow approval and trigger attempts

Do not log secrets, full documents, access tokens, or sensitive personal data.
