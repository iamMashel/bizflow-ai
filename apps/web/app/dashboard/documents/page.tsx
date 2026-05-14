"use client";

import { ChangeEvent, FormEvent, useEffect, useState } from "react";

import { EmptyState, ErrorState, LoadingState } from "@/src/components/state-patterns";
import { apiClient } from "@/src/lib/api-client";

type DocumentStatus = "pending" | "ingesting" | "processing" | "ready" | "completed" | "failed";

type DocumentSummary = {
  id: string;
  filename: string;
  status: DocumentStatus;
  created_at: string;
};

type DocumentUploadResponse = DocumentSummary & {
  duplicate: boolean;
};

type DocumentIngestResponse = {
  id: string;
  status: DocumentStatus;
  chunks_created: number;
};

const acceptedFileTypes = ".pdf,.docx,.txt,.md,.csv";

function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function statusClasses(status: DocumentStatus) {
  switch (status) {
    case "ready":
    case "completed":
      return "bg-emerald-50 text-emerald-700 ring-emerald-200";
    case "failed":
      return "bg-red-50 text-red-700 ring-red-200";
    case "ingesting":
    case "processing":
      return "bg-blue-50 text-blue-700 ring-blue-200";
    case "pending":
      return "bg-amber-50 text-amber-700 ring-amber-200";
  }
}

function canIngest(status: DocumentStatus) {
  return status === "pending" || status === "failed";
}

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [ingestingDocumentId, setIngestingDocumentId] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  async function loadDocuments() {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const nextDocuments = await apiClient.request<DocumentSummary[]>("/documents");
      setDocuments(nextDocuments);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to load documents.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    let isMounted = true;

    async function loadInitialDocuments() {
      try {
        const nextDocuments = await apiClient.request<DocumentSummary[]>("/documents");
        if (isMounted) {
          setDocuments(nextDocuments);
        }
      } catch (error) {
        if (isMounted) {
          setErrorMessage(error instanceof Error ? error.message : "Unable to load documents.");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    void loadInitialDocuments();

    return () => {
      isMounted = false;
    };
  }, []);

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    setSelectedFile(event.target.files?.[0] ?? null);
    setSuccessMessage(null);
    setErrorMessage(null);
  }

  async function handleUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!selectedFile) {
      setErrorMessage("Select a document before uploading.");
      return;
    }

    const formData = new FormData();
    formData.set("file", selectedFile);
    setIsUploading(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      const uploaded = await apiClient.request<DocumentUploadResponse>("/documents/upload", {
        method: "POST",
        body: formData,
      });
      setSuccessMessage(
        uploaded.duplicate
          ? `${uploaded.filename} was already uploaded.`
          : `${uploaded.filename} uploaded.`,
      );
      setSelectedFile(null);
      await loadDocuments();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to upload document.");
    } finally {
      setIsUploading(false);
    }
  }

  async function handleIngest(document: DocumentSummary) {
    setIngestingDocumentId(document.id);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      const result = await apiClient.request<DocumentIngestResponse>(
        `/documents/${document.id}/ingest`,
        {
          method: "POST",
        },
      );
      setSuccessMessage(`${document.filename} ingested into ${result.chunks_created} chunk(s).`);
      await loadDocuments();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to ingest document.");
    } finally {
      setIngestingDocumentId(null);
    }
  }

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-slate-950">Documents</h1>
        <p className="mt-2 text-sm text-slate-600">
          Upload source files for metadata, proposals, and future retrieval workflows.
        </p>
      </div>

      <form className="border border-slate-200 bg-white p-5 shadow-sm" onSubmit={handleUpload}>
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div className="min-w-0 flex-1">
            <label className="text-sm font-medium text-slate-700" htmlFor="document-file">
              Document
            </label>
            <input
              accept={acceptedFileTypes}
              className="mt-2 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-700 file:mr-4 file:rounded-md file:border-0 file:bg-slate-950 file:px-3 file:py-1.5 file:text-sm file:font-semibold file:text-white"
              id="document-file"
              onChange={handleFileChange}
              type="file"
            />
            <p className="mt-2 truncate text-sm text-slate-500">
              {selectedFile ? selectedFile.name : "PDF, DOCX, TXT, MD, or CSV"}
            </p>
          </div>

          <button
            className="rounded-md bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={isUploading}
            type="submit"
          >
            {isUploading ? "Uploading" : "Upload"}
          </button>
        </div>
      </form>

      {successMessage ? (
        <div className="border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
          {successMessage}
        </div>
      ) : null}

      {errorMessage ? (
        <ErrorState
          actionLabel="Retry"
          description={errorMessage}
          onAction={loadDocuments}
          title="Documents unavailable"
        />
      ) : null}

      {isLoading ? <LoadingState label="Loading documents" /> : null}

      {!isLoading && !errorMessage && documents.length === 0 ? (
        <EmptyState
          title="No documents"
          description="Uploaded files will appear here after they are stored for your workspace."
        />
      ) : null}

      {!isLoading && !errorMessage && documents.length > 0 ? (
        <div className="overflow-hidden border border-slate-200 bg-white shadow-sm">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left font-semibold text-slate-700">Filename</th>
                <th className="px-4 py-3 text-left font-semibold text-slate-700">Status</th>
                <th className="px-4 py-3 text-left font-semibold text-slate-700">Created</th>
                <th className="px-4 py-3 text-right font-semibold text-slate-700">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {documents.map((document) => {
                const isIngesting = ingestingDocumentId === document.id;

                return (
                  <tr key={document.id}>
                    <td className="max-w-xs truncate px-4 py-3 font-medium text-slate-950">
                      {document.filename}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold capitalize ring-1 ring-inset ${statusClasses(
                          document.status,
                        )}`}
                      >
                        {isIngesting ? "processing" : document.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-600">
                      {formatDate(document.created_at)}
                    </td>
                    <td className="px-4 py-3 text-right">
                      {canIngest(document.status) ? (
                        <button
                          className="rounded-md border border-slate-300 px-3 py-1.5 text-sm font-semibold text-slate-800 transition hover:border-slate-500 disabled:cursor-not-allowed disabled:opacity-60"
                          disabled={isIngesting || ingestingDocumentId !== null}
                          onClick={() => void handleIngest(document)}
                          type="button"
                        >
                          {isIngesting ? "Ingesting" : "Ingest"}
                        </button>
                      ) : (
                        <span className="text-sm text-slate-400">-</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : null}
    </section>
  );
}
