create extension if not exists vector;

create table if not exists documents (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  filename text not null,
  file_hash text not null,
  mime_type text,
  size_bytes bigint,
  storage_path text,
  status text not null default 'pending',
  summary text,
  metadata jsonb not null default '{}',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(user_id, file_hash)
);

create table if not exists document_chunks (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null references documents(id) on delete cascade,
  user_id uuid not null,
  chunk_index int not null,
  content text not null,
  token_count int,
  metadata jsonb not null default '{}',
  embedding vector(1536),
  created_at timestamptz not null default now()
);

create table if not exists conversations (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  title text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid not null references conversations(id) on delete cascade,
  user_id uuid not null,
  role text not null,
  content text not null,
  metadata jsonb not null default '{}',
  created_at timestamptz not null default now()
);

create table if not exists workflow_runs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  document_id uuid references documents(id) on delete set null,
  workflow_type text not null,
  status text not null default 'pending',
  input_payload jsonb not null default '{}',
  output_payload jsonb not null default '{}',
  approved_by_user boolean not null default false,
  error_message text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists model_events (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  task_type text,
  provider text,
  model text,
  prompt_tokens int,
  completion_tokens int,
  cost numeric,
  latency_ms int,
  status text,
  created_at timestamptz not null default now()
);

alter table documents enable row level security;
alter table document_chunks enable row level security;
alter table conversations enable row level security;
alter table messages enable row level security;
alter table workflow_runs enable row level security;
alter table model_events enable row level security;

create policy "documents_select_own"
on documents for select
using (auth.uid() = user_id);

create policy "documents_insert_own"
on documents for insert
with check (auth.uid() = user_id);

create policy "documents_update_own"
on documents for update
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

create policy "documents_delete_own"
on documents for delete
using (auth.uid() = user_id);

create policy "chunks_select_own"
on document_chunks for select
using (auth.uid() = user_id);

create policy "chunks_insert_own"
on document_chunks for insert
with check (auth.uid() = user_id);

create policy "conversations_select_own"
on conversations for select
using (auth.uid() = user_id);

create policy "conversations_insert_own"
on conversations for insert
with check (auth.uid() = user_id);

create policy "messages_select_own"
on messages for select
using (auth.uid() = user_id);

create policy "messages_insert_own"
on messages for insert
with check (auth.uid() = user_id);

create policy "workflow_runs_select_own"
on workflow_runs for select
using (auth.uid() = user_id);

create policy "workflow_runs_insert_own"
on workflow_runs for insert
with check (auth.uid() = user_id);

create policy "workflow_runs_update_own"
on workflow_runs for update
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

create policy "model_events_select_own"
on model_events for select
using (auth.uid() = user_id);

create policy "model_events_insert_own"
on model_events for insert
with check (auth.uid() = user_id);

create index if not exists idx_documents_user_id on documents(user_id);
create index if not exists idx_documents_file_hash on documents(user_id, file_hash);
create index if not exists idx_chunks_user_id on document_chunks(user_id);
create index if not exists idx_chunks_document_id on document_chunks(document_id);
create index if not exists idx_workflow_runs_user_id on workflow_runs(user_id);