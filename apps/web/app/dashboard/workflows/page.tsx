"use client";

import { useEffect, useState } from "react";

import { EmptyState, ErrorState, LoadingState } from "@/src/components/state-patterns";
import { apiClient } from "@/src/lib/api-client";

type WorkflowStatus = "pending" | "approved" | "failed" | "sent";

type WorkflowRun = {
  id: string;
  document_id: string | null;
  document_filename: string | null;
  workflow_type: string;
  status: WorkflowStatus;
  input_payload: Record<string, unknown>;
  output_payload: Record<string, unknown>;
  approved_by_user: boolean;
  created_at: string;
  updated_at?: string | null;
};

function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function statusClasses(status: WorkflowStatus) {
  switch (status) {
    case "approved":
    case "sent":
      return "bg-emerald-50 text-emerald-700 ring-emerald-200";
    case "failed":
      return "bg-red-50 text-red-700 ring-red-200";
    case "pending":
      return "bg-amber-50 text-amber-700 ring-amber-200";
  }
}

function workflowLabel(value: string) {
  return value.replaceAll("_", " ");
}

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<WorkflowRun[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [approvingWorkflowId, setApprovingWorkflowId] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  async function loadWorkflows() {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const nextWorkflows = await apiClient.request<WorkflowRun[]>("/workflows");
      setWorkflows(nextWorkflows);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to load workflows.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    let isMounted = true;

    async function loadInitialWorkflows() {
      try {
        const nextWorkflows = await apiClient.request<WorkflowRun[]>("/workflows");
        if (isMounted) {
          setWorkflows(nextWorkflows);
        }
      } catch (error) {
        if (isMounted) {
          setErrorMessage(error instanceof Error ? error.message : "Unable to load workflows.");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    void loadInitialWorkflows();

    return () => {
      isMounted = false;
    };
  }, []);

  async function handleApprove(workflow: WorkflowRun) {
    setApprovingWorkflowId(workflow.id);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      const approved = await apiClient.request<WorkflowRun>(
        `/workflows/${workflow.id}/approve`,
        {
          method: "POST",
        },
      );
      setSuccessMessage("Workflow approved. No external automation has been triggered yet.");
      setWorkflows((currentWorkflows) =>
        currentWorkflows.map((currentWorkflow) =>
          currentWorkflow.id === approved.id ? approved : currentWorkflow,
        ),
      );
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to approve workflow.");
    } finally {
      setApprovingWorkflowId(null);
    }
  }

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-slate-950">Workflows</h1>
        <p className="mt-2 text-sm text-slate-600">
          Review and approve prepared workflow payloads before external automation is connected.
        </p>
      </div>

      {successMessage ? (
        <div className="border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
          {successMessage}
        </div>
      ) : null}

      {errorMessage ? (
        <ErrorState
          actionLabel="Retry"
          description={errorMessage}
          onAction={loadWorkflows}
          title="Workflows unavailable"
        />
      ) : null}

      {isLoading ? <LoadingState label="Loading workflows" /> : null}

      {!isLoading && !errorMessage && workflows.length === 0 ? (
        <EmptyState
          title="No workflow requests"
          description="Prepared workflow requests will wait here for human approval before execution."
        />
      ) : null}

      {!isLoading && !errorMessage && workflows.length > 0 ? (
        <div className="space-y-4">
          {workflows.map((workflow) => {
            const isApproving = approvingWorkflowId === workflow.id;

            return (
              <article
                className="border border-slate-200 bg-white p-5 shadow-sm"
                key={workflow.id}
              >
                <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <h2 className="text-base font-semibold capitalize text-slate-950">
                        {workflowLabel(workflow.workflow_type)}
                      </h2>
                      <span
                        className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold capitalize ring-1 ring-inset ${statusClasses(
                          workflow.status,
                        )}`}
                      >
                        {workflow.status}
                      </span>
                    </div>
                    <p className="mt-1 text-sm text-slate-600">
                      {workflow.document_filename ?? "No linked document"} ·{" "}
                      {formatDate(workflow.created_at)}
                    </p>
                  </div>
                  {workflow.status === "pending" ? (
                    <button
                      className="rounded-md bg-slate-950 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
                      disabled={isApproving || approvingWorkflowId !== null}
                      onClick={() => void handleApprove(workflow)}
                      type="button"
                    >
                      {isApproving ? "Approving" : "Approve"}
                    </button>
                  ) : (
                    <span className="text-sm font-medium text-emerald-700">
                      Approved by user
                    </span>
                  )}
                </div>

                <div className="mt-4 grid gap-4 lg:grid-cols-2">
                  <PayloadCard title="Input payload" value={workflow.input_payload} />
                  <PayloadCard title="Preview payload" value={workflow.output_payload} />
                </div>
              </article>
            );
          })}
        </div>
      ) : null}
    </section>
  );
}

function PayloadCard({ title, value }: { title: string; value: Record<string, unknown> }) {
  return (
    <div className="border border-slate-200 bg-slate-50 p-4">
      <h3 className="text-sm font-semibold text-slate-950">{title}</h3>
      <pre className="mt-3 max-h-96 overflow-auto whitespace-pre-wrap break-words text-xs leading-5 text-slate-700">
        {JSON.stringify(value, null, 2)}
      </pre>
    </div>
  );
}
