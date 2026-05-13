import { EmptyState } from "@/src/components/state-patterns";

export default function WorkflowsPage() {
  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-slate-950">Workflows</h1>
        <p className="mt-2 text-sm text-slate-600">Approval-first automation shell.</p>
      </div>
      <EmptyState
        title="No workflow requests"
        description="Prepared n8n workflow requests will wait here for human approval before execution."
      />
    </section>
  );
}
