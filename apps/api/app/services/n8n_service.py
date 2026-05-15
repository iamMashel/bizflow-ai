from dataclasses import dataclass
from typing import Any
from uuid import UUID

import httpx

from app.core.config import Settings, get_settings


@dataclass(frozen=True)
class WorkflowTriggerRequest:
    workflow_id: UUID
    workflow_type: str
    document_id: UUID | None
    input_payload: dict[str, Any]
    output_payload: dict[str, Any]
    approved_by_user: bool


@dataclass(frozen=True)
class WorkflowTriggerResult:
    workflow_id: UUID
    status: str
    metadata: dict[str, Any]


class N8nServiceError(Exception):
    def __init__(self, message: str, *, status_code: int = 502) -> None:
        super().__init__(message)
        self.status_code = status_code


class N8nService:
    """Single boundary for all n8n webhook calls."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.webhook_url = self.settings.n8n_workflow_webhook_url
        self.webhook_secret = self.settings.n8n_webhook_secret

    async def trigger_workflow(self, request: WorkflowTriggerRequest) -> WorkflowTriggerResult:
        if not self.webhook_url:
            raise N8nServiceError("N8N_WORKFLOW_WEBHOOK_URL is not configured.")
        if not self.webhook_secret:
            raise N8nServiceError("N8N_WEBHOOK_SECRET is not configured.")
        if not request.approved_by_user:
            raise N8nServiceError("Workflow must be approved before execution.", status_code=400)

        payload = {
            "workflow_id": str(request.workflow_id),
            "workflow_type": request.workflow_type,
            "document_id": str(request.document_id) if request.document_id is not None else None,
            "input_payload": request.input_payload,
            "output_payload": request.output_payload,
            "approved_by_user": request.approved_by_user,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.webhook_url,
                    headers={"X-BizFlow-Webhook-Secret": self.webhook_secret},
                    json=payload,
                )
        except httpx.HTTPError as exc:
            raise N8nServiceError("n8n workflow call failed.") from exc

        if response.status_code >= 400:
            raise N8nServiceError(
                f"n8n workflow call failed with status {response.status_code}.",
                status_code=502,
            )

        try:
            metadata = response.json()
        except ValueError:
            metadata = {"raw_response": response.text}
        if not isinstance(metadata, dict):
            metadata = {"response": metadata}

        return WorkflowTriggerResult(
            workflow_id=request.workflow_id,
            status="completed",
            metadata=metadata,
        )
