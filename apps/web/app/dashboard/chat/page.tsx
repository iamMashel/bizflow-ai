import { EmptyState } from "@/src/components/state-patterns";

export default function ChatPage() {
  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-slate-950">Chat</h1>
        <p className="mt-2 text-sm text-slate-600">RAG chat shell with citation-ready space.</p>
      </div>
      <EmptyState
        title="No chat session"
        description="Chat messages and citations will be loaded from the backend once retrieval endpoints exist."
      />
    </section>
  );
}
