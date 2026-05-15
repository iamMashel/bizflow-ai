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
- Added Gemini embedding configuration and `google-genai` dependency.
- Added provider-neutral embedding service using Gemini embeddings.
- Added `POST /documents/{document_id}/ingest` for TXT/MD ingestion.
- Added TXT/MD text extraction, chunking, mocked embedding tests, chunk inserts, and document status transitions.
- Added basic authenticated RAG chunk search endpoint.
- Added Chat page search form that displays matching chunks without generating answers.
- Added basic RAG answer generation with citations from retrieved chunks.

## Not Started

- PDF/DOCX ingestion implementation
- Chat memory
- Model router implementation
- n8n service implementation
- Langfuse instrumentation

## Next Recommended Milestones

1. Smoke-test RAG answer generation against the configured Supabase project.
2. Add Langfuse instrumentation around future model and RAG calls.
3. Implement `model_router.py` through LiteLLM.
4. Implement approved workflow triggers through `n8n_service.py`.

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

## RAG Ingestion Milestone

### Completed

- Added TXT/MD ingestion flow.
- Added Gemini embedding support.
- Added `document_chunks` storage with 3072-dimensional vectors.
- Added status transition: pending -> processing -> completed / failed.
- Added Ingest action in the documents dashboard.
- Verified `bizflow-test.txt` ingests into 1 chunk.

### Verified

- `bizflow-test.txt` moved to completed.
- Chunk row created in `public.document_chunks`.
- Existing DOCX remains pending because DOCX parsing is not implemented yet.

### Key decisions

- Use Gemini embeddings for now.
- Use vector(3072) for Gemini embedding compatibility.
- Start with TXT/MD only before PDF/DOCX support.

### Next

Build basic RAG chat:
question -> embed query -> retrieve chunks -> generate answer with citations.

## RAG Search Milestone

### Completed

- Added authenticated `POST /rag/search`.
- Query embeddings use the Gemini embedding service.
- Search calls a Supabase RPC over `public.document_chunks` vector similarity.
- Results are scoped to the authenticated user through Supabase auth/RLS.
- Chat page can submit a question and display matching chunks.

### Not Included

- Final AI answer generation.
- Chat memory.
- PDF/DOCX parsing.
- Hybrid search.

### Next

Build basic RAG answer generation:
question -> embed query -> retrieve chunks -> generate answer with citations.

## RAG Answer Milestone

### Completed

- Added authenticated `POST /rag/answer`.
- Reused RAG chunk search before answer generation.
- Added a provider-neutral generation service using Gemini for text generation.
- Built grounded prompts from the user question, filenames, chunk indexes, and retrieved content.
- Returned answers with citations containing document ID, filename, chunk index, and preview.
- Updated the Chat page with Search chunks and Generate answer actions.

### Not Included

- Chat memory.
- Streaming responses.
- PDF/DOCX parsing.
- Final LiteLLM model router integration.

### Next

Build basic chat history:
question -> retrieve chunks -> generate answer -> persist message and citations.

## RAG Answer Generation Milestone

### Completed

- Added grounded RAG answer generation.
- `/rag/answer` now retrieves relevant chunks and generates an answer.
- Gemini embeddings are used for retrieval.
- Gemini 2.5 Flash is used for answer generation.
- Answers include citations/sources from retrieved chunks.

### Verified

- User can ask a question from the Chat page.
- Backend retrieves ingested chunks.
- Backend generates a grounded answer.
- Frontend displays the answer.

### Key fix

- Switched chat model from `gemini-2.0-flash` to `gemini-2.5-flash` because the former caused answer generation failures in the current API setup.

### Next

- Add OCR or richer PDF layout parsing when needed.

## Document Metadata Milestone

### Completed

- Added authenticated `POST /documents/{document_id}/metadata`.
- Metadata extraction reads existing ingested chunks for the current user's document.
- Gemini 2.5 Flash generates structured metadata through the existing generation service.
- Metadata JSON is parsed, validated, and saved to `documents.metadata`.
- Generated summaries are saved to `documents.summary` when available.
- Documents page can extract and display metadata for completed documents.

### Verified

- Unauthenticated metadata extraction returns 401.
- Other users' documents remain hidden through user-scoped lookups.
- Documents without chunks return a useful ingest-first error.
- Metadata LLM calls are mocked in tests.
- Invalid JSON is handled safely.

### Not Included

- n8n workflow triggers.

### Next

- Generate reviewable email drafts before n8n workflow automation.

## Email Draft Generation Milestone

### Completed

- Added authenticated `POST /documents/{document_id}/email-draft`.
- Email draft generation requires a completed document with chunks.
- Gemini 2.5 Flash generates structured email draft JSON from document context, summary, metadata, and proposal draft when available.
- Email drafts include subject, body, purpose, recipient context, missing information questions, and call to action.
- Email drafts are saved to `documents.metadata.email_draft` without overwriting existing metadata.
- Documents page can generate, display, and copy email drafts.

### Verified

- Unauthenticated email draft requests return 401.
- Other users' documents remain hidden through user-scoped lookups.
- Documents without chunks return a useful ingest-first error.
- Email draft LLM calls are mocked in tests.
- Invalid email draft JSON is handled safely.

### Not Included

- n8n workflow triggers.
- Email sending.

### Next

- Add human approval and n8n workflow trigger support.

## Proposal Generation Milestone

### Completed

- Added authenticated `POST /documents/{document_id}/proposal`.
- Proposal generation requires a completed document with chunks.
- Gemini 2.5 Flash generates a structured proposal draft from document context, summary, and metadata.
- Proposal drafts include executive summary, client problem, solution, scope, deliverables, timeline, assumptions, missing information, and next steps.
- Proposal drafts are saved to `documents.metadata.proposal_draft`.
- Documents page can generate and display proposal drafts.

### Verified

- Unauthenticated proposal requests return 401.
- Other users' documents remain hidden through user-scoped lookups.
- Documents without chunks return a useful ingest-first error.
- Proposal LLM calls are mocked in tests.
- Invalid proposal JSON is handled safely.
- Backend checks pass with 53 tests.
- Frontend lint and build pass.

### Not Included

- n8n workflow triggers.
- Email sending.

### Next

- Add human approval and n8n workflow trigger support.

## Document Summary Actions Milestone

### Completed

- Added authenticated `POST /documents/{document_id}/summary`.
- Summary generation requires an ingested completed document with chunks.
- Gemini 2.5 Flash generates concise summary, detailed summary, key points, recommended actions, and suggested workflow.
- Concise summaries are saved to `documents.summary`.
- Key points, recommended actions, suggested workflow, and detailed summary are merged into `documents.metadata`.
- Documents page can generate and display summaries and recommended actions.

### Verified

- Unauthenticated summary requests return 401.
- Other users' documents remain hidden through user-scoped lookups.
- Documents without chunks return a useful ingest-first error.
- Summary LLM calls are mocked in tests.
- Existing metadata fields are preserved during summary updates.

### Not Included

- n8n workflow triggers.
- Proposal generation.

### Next

- Build proposal generation from extracted metadata and retrieved context.

## PDF Ingestion Milestone

### Completed

- Added PDF text extraction with `pypdf`.
- Existing TXT/MD/DOCX ingestion remains supported.
- PDF text is extracted page by page.
- PDF chunks preserve page number metadata where possible.
- PDF ingestion reuses the existing chunking and Gemini embedding pipeline.

### Verified

- PDF extraction unit test covers page text and page metadata.
- Mocked embeddings are used in ingestion tests.
- Document status moves to `completed` on successful PDF ingestion.

### Not Included

- OCR for scanned PDFs.
- Rich table/layout parsing.

### Next

- Add OCR or richer PDF layout parsing when needed.

## DOCX Ingestion Milestone

### Completed

- Added DOCX text extraction.
- Reused existing chunking and Gemini embedding pipeline.
- DOCX documents can now move from pending -> processing -> completed.
- Grounded RAG answers work over ingested DOCX content.

### Verified

- DOCX upload works.
- DOCX ingestion works.
- Chat can answer questions from ingested DOCX chunks.

### Next

- Add PDF ingestion support.
