from uuid import UUID

from app.schemas.documents import DocumentSummary


class DocumentService:
    """Document workflow boundary."""

    async def list_documents_for_user(self, user_id: UUID | None = None) -> list[DocumentSummary]:
        # TODO: Require authenticated user and read user-owned documents from Supabase.
        _ = user_id
        return []
