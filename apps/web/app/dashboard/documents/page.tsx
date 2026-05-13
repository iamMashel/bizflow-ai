import { EmptyState } from "@/src/components/state-patterns";

export default function DocumentsPage() {
  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-slate-950">Documents</h1>
        <p className="mt-2 text-sm text-slate-600">Upload and ingestion UI foundation.</p>
      </div>
      <EmptyState
        title="No documents"
        description="Document upload, ingestion status, and citation sources will be connected after the API and Supabase slices are ready."
      />
    </section>
  );
}
