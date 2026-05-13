from fastapi import APIRouter

from app.schemas.documents import DocumentSummary
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[DocumentSummary])
async def list_documents() -> list[DocumentSummary]:
    # TODO: Inject authenticated user once auth is implemented.
    service = DocumentService()
    return await service.list_documents_for_user()
