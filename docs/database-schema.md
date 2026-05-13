# Database Schema

## Status

No migrations are implemented yet. This document defines the intended database model and non-negotiable database rules.

## Required Extensions

Planned Supabase/Postgres extensions:

```sql
create extension if not exists vector;
create extension if not exists pgcrypto;
```

## Global Rules

- Every user-owned table must have `user_id uuid not null`.
- Every user-owned table must enable RLS.
- RLS policies must scope user access to `auth.uid() = user_id`.
- Client-provided `user_id` must not be trusted by backend logic.
- All foreign keys should use `on delete cascade` only when data deletion behavior is intentional.
- Embedding tables must preserve source traceability.

## Planned Tables

### `documents`

Stores uploaded document metadata.

Key fields:

- `id uuid primary key`
- `user_id uuid not null`
- `storage_bucket text not null`
- `storage_path text not null`
- `filename text not null`
- `content_type text`
- `size_bytes bigint`
- `status text not null`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`

### `document_chunks`

Stores extracted text chunks and embeddings.

Key fields:

- `id uuid primary key`
- `user_id uuid not null`
- `document_id uuid not null references documents(id)`
- `chunk_index integer not null`
- `content text not null`
- `embedding vector`
- `metadata jsonb not null default '{}'`
- `created_at timestamptz not null`

Expected metadata:

- Page number when available
- Section title when available
- Character offsets when available
- Extraction parser details

### `chat_sessions`

Stores user chat sessions.

Key fields:

- `id uuid primary key`
- `user_id uuid not null`
- `title text`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`

### `chat_messages`

Stores chat messages and assistant responses.

Key fields:

- `id uuid primary key`
- `user_id uuid not null`
- `session_id uuid not null references chat_sessions(id)`
- `role text not null`
- `content text not null`
- `citations jsonb not null default '[]'`
- `model_metadata jsonb not null default '{}'`
- `created_at timestamptz not null`

### `metadata_extractions`

Stores structured extraction results.

Key fields:

- `id uuid primary key`
- `user_id uuid not null`
- `document_id uuid not null references documents(id)`
- `schema_name text not null`
- `result jsonb not null`
- `citations jsonb not null default '[]'`
- `status text not null`
- `created_at timestamptz not null`

### `proposals`

Stores generated proposal drafts.

Key fields:

- `id uuid primary key`
- `user_id uuid not null`
- `title text not null`
- `prompt jsonb not null`
- `content text not null`
- `citations jsonb not null default '[]'`
- `model_metadata jsonb not null default '{}'`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`

### `workflow_requests`

Stores prepared automation requests awaiting approval or already triggered.

Key fields:

- `id uuid primary key`
- `user_id uuid not null`
- `workflow_type text not null`
- `payload jsonb not null`
- `status text not null`
- `approval_required boolean not null default true`
- `approved_at timestamptz`
- `triggered_at timestamptz`
- `n8n_result jsonb`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`

## RLS Policy Pattern

Each user-owned table should follow this shape:

```sql
alter table table_name enable row level security;

create policy "Users can read own rows"
on table_name for select
using (auth.uid() = user_id);

create policy "Users can insert own rows"
on table_name for insert
with check (auth.uid() = user_id);

create policy "Users can update own rows"
on table_name for update
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

create policy "Users can delete own rows"
on table_name for delete
using (auth.uid() = user_id);
```

Actual migration names and policies must be reviewed per table before implementation.

## Indexing Plan

Planned indexes:

- `documents(user_id, created_at desc)`
- `document_chunks(user_id, document_id, chunk_index)`
- Vector index on `document_chunks.embedding`
- `chat_sessions(user_id, updated_at desc)`
- `chat_messages(user_id, session_id, created_at)`
- `workflow_requests(user_id, status, created_at desc)`
