# BizFlow AI

BizFlow AI is a production-style full-stack Agentic RAG Automation Platform for SMEs. The MVP helps authenticated users upload business documents, ingest them into a retrieval pipeline, chat with cited answers, extract structured metadata, generate proposals, and trigger approved external automations through n8n.

This repository is currently in the documentation-first phase. Application code should not be added until the project contracts in `docs/` are reviewed and accepted.

## Stack

- Backend: FastAPI, Python 3.12, uv
- Frontend: Next.js, TypeScript, Tailwind
- Database, auth, storage: Supabase, Postgres, pgvector, RLS
- AI providers: LiteLLM routing to DeepSeek, OpenAI, and Claude
- Automation: n8n webhooks
- Observability: Langfuse
- Testing: Pytest, Ruff, Mypy, frontend typecheck, frontend build

## MVP Scope

- Authenticated SME user workspace
- Document upload to Supabase Storage
- RAG ingestion with chunking, embeddings, and source tracking
- RAG chat with citations
- Metadata extraction from uploaded documents
- Proposal generation from retrieved context and user inputs
- Human-approved n8n workflow trigger

## Non-Negotiable Rules

- No fake endpoints.
- No mock-only frontend.
- All model calls go through `model_router.py`.
- All n8n calls go through `n8n_service.py`.
- Every user-owned table has `user_id` and RLS.
- External workflows require explicit human approval.
- Uploaded documents are untrusted data.

## Documentation Map

- `AGENTS.md`: rules for AI coding agents working in this repo
- `docs/spec.md`: product and MVP specification
- `docs/architecture.md`: system architecture and module boundaries
- `docs/api-contract.md`: API contract principles and initial route plan
- `docs/database-schema.md`: database design, RLS requirements, and migration rules
- `docs/security.md`: security model and threat controls
- `docs/rag-design.md`: ingestion, retrieval, citations, and generation design
- `docs/testing.md`: verification strategy
- `docs/progress.md`: current project status
- `docs/decisions.md`: architecture decision record
- `docs/context-summary.md`: compact project context for future contributors

## Local Setup

Implementation has not started yet. Once code is added, setup should use `uv` for backend dependency management and the standard Next.js package workflow for the frontend.

Environment configuration starts from:

```bash
cp .env.example .env
```

Do not commit `.env` or real credentials.
