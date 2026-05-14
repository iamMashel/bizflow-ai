from datetime import UTC, datetime
from uuid import UUID

from fastapi.testclient import TestClient

from app.api.routes_documents import get_document_service
from app.core.config import Settings, get_settings
from app.core.security import CurrentUser, get_current_user
from app.main import app
from app.schemas.documents import DocumentSummary, DocumentUploadResponse

USER_ID = UUID("00000000-0000-0000-0000-000000000001")
DOCUMENT_ID = UUID("00000000-0000-0000-0000-000000000101")
CREATED_AT = datetime(2026, 5, 14, 12, 0, tzinfo=UTC)


class FakeDocumentService:
    def __init__(self, *, duplicate: bool = False) -> None:
        self.duplicate = duplicate

    async def list_documents_for_user(
        self,
        *,
        user_id: UUID,
        access_token: str,
    ) -> list[DocumentSummary]:
        assert user_id == USER_ID
        assert access_token == "test-access-token"
        return [
            DocumentSummary(
                id=DOCUMENT_ID,
                filename="proposal.pdf",
                status="pending",
                created_at=CREATED_AT,
            )
        ]

    async def upload_document(
        self,
        *,
        user_id: UUID,
        access_token: str,
        filename: str,
        mime_type: str | None,
        content: bytes,
    ) -> DocumentUploadResponse:
        assert user_id == USER_ID
        assert access_token == "test-access-token"
        assert filename == "proposal.pdf"
        assert mime_type == "application/pdf"
        assert content == b"same file"
        return DocumentUploadResponse(
            id=DOCUMENT_ID,
            filename=filename,
            status="pending",
            duplicate=self.duplicate,
            created_at=CREATED_AT,
        )


def override_user() -> CurrentUser:
    return CurrentUser(
        id=USER_ID,
        email="owner@example.com",
        access_token="test-access-token",
    )


def override_settings(max_upload_bytes: int = 20 * 1024 * 1024) -> Settings:
    return Settings(
        supabase_url="https://example.supabase.co",
        supabase_anon_key="anon",
        supabase_service_role_key="service-role",
        max_upload_bytes=max_upload_bytes,
    )


def setup_overrides(
    *,
    service: FakeDocumentService | None = None,
    max_upload_bytes: int = 20 * 1024 * 1024,
) -> None:
    app.dependency_overrides[get_current_user] = override_user
    app.dependency_overrides[get_settings] = lambda: override_settings(max_upload_bytes)
    app.dependency_overrides[get_document_service] = lambda: service or FakeDocumentService()


def test_documents_rejects_missing_token() -> None:
    client = TestClient(app)

    response = client.get("/documents")

    assert response.status_code == 401


def test_document_upload_rejects_missing_token() -> None:
    client = TestClient(app)

    response = client.post(
        "/documents/upload",
        files={"file": ("proposal.pdf", b"same file", "application/pdf")},
    )

    assert response.status_code == 401


def test_document_upload_rejects_invalid_file_type() -> None:
    setup_overrides()
    client = TestClient(app)

    try:
        response = client.post(
            "/documents/upload",
            files={"file": ("malware.exe", b"same file", "application/octet-stream")},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 400


def test_document_upload_rejects_oversized_file() -> None:
    setup_overrides(max_upload_bytes=4)
    client = TestClient(app)

    try:
        response = client.post(
            "/documents/upload",
            files={"file": ("proposal.pdf", b"same file", "application/pdf")},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 413


def test_document_upload_handles_duplicate() -> None:
    setup_overrides(service=FakeDocumentService(duplicate=True))
    client = TestClient(app)

    try:
        response = client.post(
            "/documents/upload",
            files={"file": ("proposal.pdf", b"same file", "application/pdf")},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["duplicate"] is True
    assert response.json()["filename"] == "proposal.pdf"


def test_documents_returns_current_user_documents() -> None:
    setup_overrides()
    client = TestClient(app)

    try:
        response = client.get("/documents")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(DOCUMENT_ID),
            "filename": "proposal.pdf",
            "status": "pending",
            "created_at": CREATED_AT.isoformat().replace("+00:00", "Z"),
        }
    ]
