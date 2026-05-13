from dataclasses import dataclass
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class WorkflowTriggerRequest:
    workflow_request_id: UUID
    workflow_type: str
    payload: dict[str, Any]
    approved_by_user: bool


@dataclass(frozen=True)
class WorkflowTriggerResult:
    workflow_request_id: UUID
    status: str
    metadata: dict[str, Any]


class N8nService:
    """Single boundary for all n8n webhook calls."""

    async def trigger_workflow(self, request: WorkflowTriggerRequest) -> WorkflowTriggerResult:
        # TODO: Validate approval, sign payloads, and call n8n webhooks.
        raise NotImplementedError("n8n workflow triggering is not implemented yet.")
