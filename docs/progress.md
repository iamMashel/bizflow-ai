# Progress

## Current Status

Initial repository documentation has been created. No application code has been written.

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

## Not Started

- Backend application
- Frontend application
- Supabase migrations
- RAG ingestion implementation
- Model router implementation
- n8n service implementation
- Langfuse instrumentation
- Automated tests
- CI

## Next Recommended Milestones

1. Scaffold backend with FastAPI, Python 3.12, and uv.
2. Scaffold frontend with Next.js, TypeScript, and Tailwind.
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
