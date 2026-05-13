# Progress

## Current Status

Initial repository documentation is complete. Backend and frontend foundations have been started under `apps/api` and `apps/web`.

## Completed

- Defined product scope and MVP requirements.
- Documented architecture boundaries.
- Documented API contract principles and planned route surface.
- Documented planned database schema and RLS requirements.
- Documented security model.
- Documented RAG design.
- Documented testing strategy.
- Added environment variable template.
- Added git ignore rules.
- Initialized the backend with uv and Python 3.12.
- Added a FastAPI application factory in `apps/api/app/main.py`.
- Added Pydantic Settings in `apps/api/app/core/config.py`.
- Added a real `/health` endpoint.
- Added a Pytest test for `/health`.
- Added Ruff, Mypy, and Pytest configuration for the API app.
- Initialized the frontend with Next.js App Router, TypeScript, and Tailwind.
- Added a clean landing page and login placeholder.
- Added a protected dashboard layout placeholder with shared navigation.
- Added placeholder pages for documents, chat, workflows, and settings.
- Added frontend loading, empty, and error component patterns.
- Added frontend API and Supabase client placeholders.

## Not Started

- Supabase migrations
- RAG ingestion implementation
- Model router implementation
- n8n service implementation
- Langfuse instrumentation
- Automated tests
- CI

## Next Recommended Milestones

1. Add CI for backend and frontend checks.
2. Replace frontend placeholders with auth-connected flows once Supabase is introduced.
3. Add Supabase migration baseline with RLS policies.
4. Implement auth-aware backend dependencies.
5. Build document upload and ingestion as the first vertical slice.

## Rules To Preserve

- No fake endpoints.
- No mock-only frontend.
- All model calls go through `model_router.py`.
- All n8n calls go through `n8n_service.py`.
- Every user-owned table has `user_id` and RLS.
- External workflows require human approval.
- Uploaded documents are untrusted data.
