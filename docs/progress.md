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
- Added backend service skeletons for model routing, n8n workflows, and documents.
- Added typed document schemas and a placeholder `GET /documents` route.
- Added Supabase auth foundation with backend Bearer token verification and `/me`.
- Protected `GET /documents` behind the auth dependency while keeping its response empty.
- Added frontend Supabase client setup, email/password login, logout, dashboard auth gate, and API token attachment.
- Updated backend auth verification to validate access tokens through the Supabase Auth user endpoint.
- Added frontend sign-up support to the login page.
- Added real `POST /documents/upload` with authenticated multipart upload validation.
- Added SHA-256 duplicate detection per user before storing uploaded originals.
- Added Supabase Storage upload and `documents` table insertion for pending documents.
- Replaced placeholder `GET /documents` with Supabase-backed user document listing.
- Updated the frontend Documents page with real upload, loading, error, duplicate, and listing states.
- Added backend route tests for document upload auth, type validation, size limits, duplicates, and listing auth.

## Not Started

- RAG ingestion implementation
- Text extraction implementation
- Embedding generation
- Model router implementation
- n8n service implementation
- Langfuse instrumentation

## Next Recommended Milestones

1. Smoke-test document upload against the configured Supabase project and `documents` Storage bucket.
2. Build document ingestion as the next vertical slice.
3. Add Langfuse instrumentation around future model and RAG calls.
4. Implement `model_router.py` through LiteLLM.
5. Implement approved workflow triggers through `n8n_service.py`.

## Rules To Preserve

- No fake endpoints.
- No mock-only frontend.
- All model calls go through `model_router.py`.
- All n8n calls go through `n8n_service.py`.
- Every user-owned table has `user_id` and RLS.
- External workflows require human approval.
- Uploaded documents are untrusted data.

## Document Upload Milestone

### Completed

- Supabase auth-protected document routes.
- Private `documents` storage bucket.
- Document upload from frontend.
- File validation.
- SHA-256 duplicate detection.
- Document metadata inserted into `public.documents`.
- Authenticated document listing.
- RLS policies and grants fixed for `authenticated` role.

### Verified

- Unauthenticated `GET /documents` returns 401.
- Authenticated user can upload `bizflow-test.txt`.
- Uploaded document appears in dashboard with status `pending`.

### Key lesson

Postgres grants and RLS are separate layers:

- Grants allow a role to access a table.
- RLS controls which rows the role can access.

### Next

Build RAG ingestion:
upload -> extract text -> chunk -> embed -> store chunks -> update status.
