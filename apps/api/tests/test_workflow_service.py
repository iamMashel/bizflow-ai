from uuid import UUID

import pytest

from app.core.config import Settings
from app.schemas.workflows import WorkflowRun
from app.services.n8n_service import N8nServiceError, WorkflowTriggerRequest, WorkflowTriggerResult
from app.services.workflow_service import WorkflowService, WorkflowServiceError
from tests.test_workflows import CREATED_AT, DOCUMENT_ID, USER_ID, WORKFLOW_ID, workflow_run


class FakeN8nService:
    def __init__(self, *, error: N8nServiceError | None = None) -> None:
        self.error = error
        self.requests: list[WorkflowTriggerRequest] = []

    async def trigger_workflow(self, request: WorkflowTriggerRequest) -> WorkflowTriggerResult:
        self.requests.append(request)
        if self.error is not None:
            raise self.error
        return WorkflowTriggerResult(
            workflow_id=request.workflow_id,
            status="completed",
            metadata={"ok": True, "received": True},
        )


class FakeWorkflowService(WorkflowService):
    def __init__(
        self,
        *,
        workflow: WorkflowRun,
        n8n_error: N8nServiceError | None = None,
    ) -> None:
        self.fake_n8n_service = FakeN8nService(error=n8n_error)
        super().__init__(
            Settings(
                supabase_url="https://example.supabase.co",
                supabase_anon_key="anon",
            ),
            n8n_service=self.fake_n8n_service,  # type: ignore[arg-type]
        )
        self.workflow = workflow
        self.updates: list[tuple[str, str | None]] = []

    async def _get_workflow_run(
        self,
        *,
        user_id: UUID,
        access_token: str,
        workflow_id: UUID,
    ) -> WorkflowRun:
        assert user_id == USER_ID
        assert access_token == "test-access-token"
        assert workflow_id == WORKFLOW_ID
        return self.workflow

    async def _update_workflow_run(
        self,
        *,
        user_id: UUID,
        access_token: str,
        workflow_id: UUID,
        status: str,
        output_payload: dict[str, object] | None = None,
        error_message: str | None = None,
    ) -> WorkflowRun:
        assert user_id == USER_ID
        assert access_token == "test-access-token"
        assert workflow_id == WORKFLOW_ID
        self.updates.append((status, error_message))
        return WorkflowRun(
            id=WORKFLOW_ID,
            document_id=DOCUMENT_ID,
            document_filename="proposal.pdf",
            workflow_type="proposal_follow_up",
            status=status,  # type: ignore[arg-type]
            input_payload=self.workflow.input_payload,
            output_payload=output_payload or self.workflow.output_payload,
            approved_by_user=self.workflow.approved_by_user,
            error_message=error_message,
            created_at=CREATED_AT,
            updated_at=CREATED_AT,
        )


@pytest.mark.asyncio
async def test_execute_requires_approved_workflow() -> None:
    service = FakeWorkflowService(workflow=workflow_run(status="pending", approved=False))

    with pytest.raises(WorkflowServiceError) as exc_info:
        await service.execute_workflow(
            user_id=USER_ID,
            access_token="test-access-token",
            workflow_id=WORKFLOW_ID,
        )

    assert exc_info.value.status_code == 400
    assert service.updates == []
    assert service.fake_n8n_service.requests == []


@pytest.mark.asyncio
async def test_execute_updates_running_then_completed() -> None:
    service = FakeWorkflowService(workflow=workflow_run(status="approved", approved=True))

    result = await service.execute_workflow(
        user_id=USER_ID,
        access_token="test-access-token",
        workflow_id=WORKFLOW_ID,
    )

    assert result.status == "completed"
    assert service.updates == [("running", None), ("completed", None)]
    assert service.fake_n8n_service.requests[0].workflow_id == WORKFLOW_ID
    assert result.output_payload["n8n_response"] == {"ok": True, "received": True}


@pytest.mark.asyncio
async def test_execute_marks_failed_when_n8n_fails() -> None:
    service = FakeWorkflowService(
        workflow=workflow_run(status="approved", approved=True),
        n8n_error=N8nServiceError("n8n workflow call failed."),
    )

    with pytest.raises(WorkflowServiceError) as exc_info:
        await service.execute_workflow(
            user_id=USER_ID,
            access_token="test-access-token",
            workflow_id=WORKFLOW_ID,
        )

    assert exc_info.value.status_code == 502
    assert service.updates == [
        ("running", None),
        ("failed", "n8n workflow call failed."),
    ]
