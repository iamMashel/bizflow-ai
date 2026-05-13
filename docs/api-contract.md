# API Contract

## Status

No API endpoints are implemented yet. This document defines contract rules and planned MVP surface area. When implementation begins, every route listed here must be backed by real backend behavior before the frontend depends on it.

## Contract Rules

- No fake endpoints.
- No mock-only frontend calls.
- Every route must validate the authenticated user.
- Every route that accesses user-owned data must enforce `user_id` ownership.
- Request and response bodies must use typed schemas.
- Errors must use a consistent JSON shape.
- Model-backed routes must call `model_router.py`.
- n8n-backed routes must call `n8n_service.py`.

## Authentication

The frontend uses Supabase Auth. Backend requests should include the Supabase access token. The backend validates the token and derives `user_id` from the authenticated identity, not from client-provided body fields.

## Standard Error Shape

Planned error response:

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {}
  }
}
```

Do not expose provider stack traces, secrets, SQL details, or internal webhook URLs.

## Planned MVP Routes

These are planned routes, not implemented endpoints.

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Backend health check |
| `POST` | `/documents` | Register or upload a user document |
| `GET` | `/documents` | List current user's documents |
| `GET` | `/documents/{document_id}` | Get document metadata and ingestion status |
| `POST` | `/documents/{document_id}/ingest` | Start ingestion for an uploaded document |
| `POST` | `/chat/sessions` | Create a chat session scoped to the user |
| `POST` | `/chat/sessions/{session_id}/messages` | Ask a RAG question and receive cited answer |
| `POST` | `/documents/{document_id}/extract-metadata` | Extract structured metadata from a document |
| `POST` | `/proposals` | Generate a proposal draft from user input and retrieved context |
| `POST` | `/workflow-requests` | Prepare an external workflow request for review |
| `POST` | `/workflow-requests/{request_id}/approve` | Approve and trigger an n8n workflow |

## Citation Requirements

RAG chat and proposal responses that rely on document context must return citations. A citation should include:

- `document_id`
- `chunk_id`
- Human-readable document name
- Optional page, section, or character offsets when available
- Short excerpt suitable for display

## Workflow Approval Requirements

Workflow trigger routes must:

- Load the prepared workflow request from the database.
- Confirm it belongs to the authenticated user.
- Confirm the user explicitly approved it.
- Persist approval metadata before calling n8n.
- Call n8n only through `n8n_service.py`.
- Persist the trigger result.

## Versioning

The initial API may ship unversioned during local MVP development. Before external release, prefer `/api/v1` or equivalent versioning.
