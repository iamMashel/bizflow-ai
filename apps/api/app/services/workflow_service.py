import logging
from datetime import datetime
from typing import Any, cast
from uuid import UUID

import httpx

from app.core.config import Settings
from app.schemas.workflows import WorkflowRun, WorkflowType

logger = logging.getLogger(__name__)


class WorkflowServiceError(Exception):
    def __init__(self, message: str, *, status_code: int = 502) -> None:
        super().__init__(message)
        self.status_code = status_code


class WorkflowService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.supabase_url = settings.supabase_url.rstrip("/")
        self.supabase_anon_key = settings.supabase_anon_key

    async def create_preview(
        self,
        *,
        user_id: UUID,
        access_token: str,
        document_id: UUID,
        workflow_type: WorkflowType,
    ) -> WorkflowRun:
        document = await self._get_document(
            user_id=user_id,
            access_token=access_token,
            document_id=document_id,
        )
        status = document.get("status")
        if status not in {"completed", "ready"}:
            raise WorkflowServiceError(
                "Document must be completed before a workflow preview can be created.",
                status_code=400,
            )

        input_payload = self._build_input_payload(document=document, workflow_type=workflow_type)
        output_payload = self._build_output_payload(document=document, workflow_type=workflow_type)
        return await self._insert_workflow_run(
            user_id=user_id,
            access_token=access_token,
            document_id=document_id,
            workflow_type=workflow_type,
            input_payload=input_payload,
            output_payload=output_payload,
        )

    async def approve_workflow(
        self,
        *,
        user_id: UUID,
        access_token: str,
        workflow_id: UUID,
    ) -> WorkflowRun:
        current = await self._get_workflow_run(
            user_id=user_id,
            access_token=access_token,
            workflow_id=workflow_id,
        )
        if current.status != "pending":
            raise WorkflowServiceError("Only pending workflows can be approved.", status_code=400)

        self._require_database_config(access_token)
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.patch(
                f"{self.supabase_url}/rest/v1/workflow_runs",
                headers={
                    **self._database_headers(access_token),
                    "Content-Type": "application/json",
                    "Prefer": "return=representation",
                },
                params={
                    "id": f"eq.{workflow_id}",
                    "user_id": f"eq.{user_id}",
                    "select": self._workflow_select(),
                },
                json={
                    "status": "approved",
                    "approved_by_user": True,
                },
            )

        self._raise_for_supabase_error(response, "Unable to approve workflow.")
        payload = response.json()
        if not isinstance(payload, list) or not payload:
            raise WorkflowServiceError("Workflow not found.", status_code=404)
        return self._workflow_from_row(cast(dict[str, Any], payload[0]))

    async def list_workflows(
        self,
        *,
        user_id: UUID,
        access_token: str,
    ) -> list[WorkflowRun]:
        self._require_database_config(access_token)
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                f"{self.supabase_url}/rest/v1/workflow_runs",
                headers=self._database_headers(access_token),
                params={
                    "select": self._workflow_select(),
                    "user_id": f"eq.{user_id}",
                    "order": "created_at.desc",
                },
            )

        self._raise_for_supabase_error(response, "Unable to read workflows.")
        payload = response.json()
        if not isinstance(payload, list):
            raise WorkflowServiceError("Unexpected workflows response from Supabase.")
        return [self._workflow_from_row(row) for row in cast(list[dict[str, Any]], payload)]

    async def _get_document(
        self,
        *,
        user_id: UUID,
        access_token: str,
        document_id: UUID,
    ) -> dict[str, Any]:
        self._require_database_config(access_token)
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                f"{self.supabase_url}/rest/v1/documents",
                headers=self._database_headers(access_token),
                params={
                    "select": "id,filename,status,summary,metadata",
                    "id": f"eq.{document_id}",
                    "user_id": f"eq.{user_id}",
                    "limit": "1",
                },
            )

        self._raise_for_supabase_error(response, "Unable to read document.")
        payload = response.json()
        if not isinstance(payload, list) or not payload:
            raise WorkflowServiceError("Document not found.", status_code=404)
        return cast(dict[str, Any], payload[0])

    async def _get_workflow_run(
        self,
        *,
        user_id: UUID,
        access_token: str,
        workflow_id: UUID,
    ) -> WorkflowRun:
        self._require_database_config(access_token)
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                f"{self.supabase_url}/rest/v1/workflow_runs",
                headers=self._database_headers(access_token),
                params={
                    "select": self._workflow_select(),
                    "id": f"eq.{workflow_id}",
                    "user_id": f"eq.{user_id}",
                    "limit": "1",
                },
            )

        self._raise_for_supabase_error(response, "Unable to read workflow.")
        payload = response.json()
        if not isinstance(payload, list) or not payload:
            raise WorkflowServiceError("Workflow not found.", status_code=404)
        return self._workflow_from_row(cast(dict[str, Any], payload[0]))

    async def _insert_workflow_run(
        self,
        *,
        user_id: UUID,
        access_token: str,
        document_id: UUID,
        workflow_type: WorkflowType,
        input_payload: dict[str, Any],
        output_payload: dict[str, Any],
    ) -> WorkflowRun:
        self._require_database_config(access_token)
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                f"{self.supabase_url}/rest/v1/workflow_runs",
                headers={
                    **self._database_headers(access_token),
                    "Content-Type": "application/json",
                    "Prefer": "return=representation",
                },
                params={"select": self._workflow_select()},
                json={
                    "user_id": str(user_id),
                    "document_id": str(document_id),
                    "workflow_type": workflow_type,
                    "status": "pending",
                    "input_payload": input_payload,
                    "output_payload": output_payload,
                    "approved_by_user": False,
                },
            )

        self._raise_for_supabase_error(response, "Unable to create workflow preview.")
        payload = response.json()
        if not isinstance(payload, list) or not payload:
            raise WorkflowServiceError("Unexpected workflow insert response from Supabase.")
        return self._workflow_from_row(cast(dict[str, Any], payload[0]))

    @staticmethod
    def _build_input_payload(
        *,
        document: dict[str, Any],
        workflow_type: WorkflowType,
    ) -> dict[str, Any]:
        metadata = document.get("metadata")
        safe_metadata = metadata if isinstance(metadata, dict) else {}
        return {
            "document_id": document.get("id"),
            "filename": document.get("filename"),
            "workflow_type": workflow_type,
            "summary": document.get("summary"),
            "recommended_actions": safe_metadata.get("recommended_actions", []),
            "proposal_draft": safe_metadata.get("proposal_draft"),
            "email_draft": safe_metadata.get("email_draft"),
        }

    @staticmethod
    def _build_output_payload(
        *,
        document: dict[str, Any],
        workflow_type: WorkflowType,
    ) -> dict[str, Any]:
        metadata = document.get("metadata")
        safe_metadata = metadata if isinstance(metadata, dict) else {}
        email_draft = safe_metadata.get("email_draft")
        proposal_draft = safe_metadata.get("proposal_draft")
        return {
            "workflow_type": workflow_type,
            "document": {
                "id": document.get("id"),
                "filename": document.get("filename"),
                "summary": document.get("summary"),
            },
            "approval_required": True,
            "approved_by_user": False,
            "preview": {
                "email_draft": email_draft if isinstance(email_draft, dict) else None,
                "proposal_draft": proposal_draft if isinstance(proposal_draft, dict) else None,
                "recommended_actions": safe_metadata.get("recommended_actions", []),
            },
            "next_step": "Review and approve before any external workflow is triggered.",
        }

    def _database_headers(self, access_token: str) -> dict[str, str]:
        if not self.supabase_anon_key or not access_token:
            raise WorkflowServiceError("Supabase workflow access is not configured.")
        return {
            "apikey": self.supabase_anon_key,
            "Authorization": f"Bearer {access_token}",
        }

    def _require_database_config(self, access_token: str) -> None:
        if not self.supabase_url or not self.supabase_anon_key or not access_token:
            raise WorkflowServiceError("Supabase workflow access is not configured.")

    @staticmethod
    def _workflow_select() -> str:
        return (
            "id,document_id,workflow_type,status,input_payload,output_payload,"
            "approved_by_user,created_at,updated_at,documents(filename)"
        )

    @staticmethod
    def _workflow_from_row(row: dict[str, Any]) -> WorkflowRun:
        workflow_id = row.get("id")
        workflow_type = row.get("workflow_type")
        status = row.get("status")
        created_at = row.get("created_at")
        updated_at = row.get("updated_at")
        document_id = row.get("document_id")
        documents = row.get("documents")
        document_filename = None
        if isinstance(documents, dict) and isinstance(documents.get("filename"), str):
            document_filename = documents["filename"]

        if not isinstance(workflow_id, str):
            raise WorkflowServiceError("Workflow row is missing id.")
        if workflow_type not in {"proposal_follow_up", "email_draft_review", "lead_capture"}:
            raise WorkflowServiceError("Workflow row has invalid type.")
        if status not in {"pending", "approved", "failed", "sent"}:
            raise WorkflowServiceError("Workflow row has invalid status.")
        if not isinstance(created_at, str):
            raise WorkflowServiceError("Workflow row is missing created_at.")

        input_payload = row.get("input_payload")
        output_payload = row.get("output_payload")
        approved_by_user = row.get("approved_by_user")

        return WorkflowRun(
            id=UUID(workflow_id),
            document_id=UUID(document_id) if isinstance(document_id, str) else None,
            document_filename=document_filename,
            workflow_type=workflow_type,
            status=status,
            input_payload=input_payload if isinstance(input_payload, dict) else {},
            output_payload=output_payload if isinstance(output_payload, dict) else {},
            approved_by_user=approved_by_user if isinstance(approved_by_user, bool) else False,
            created_at=datetime.fromisoformat(created_at.replace("Z", "+00:00")),
            updated_at=(
                datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                if isinstance(updated_at, str)
                else None
            ),
        )

    @staticmethod
    def _raise_for_supabase_error(response: httpx.Response, message: str) -> None:
        if response.status_code >= 400:
            logger.warning(
                "Supabase workflow REST error: status_code=%s path=%s body=%s",
                response.status_code,
                response.request.url.path,
                response.text,
            )
            raise WorkflowServiceError(message, status_code=response.status_code)
