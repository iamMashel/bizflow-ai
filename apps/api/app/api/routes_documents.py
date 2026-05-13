from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.security import CurrentUser, get_current_user
from app.schemas.documents import DocumentSummary
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[DocumentSummary])
async def list_documents(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> list[DocumentSummary]:
    service = DocumentService()
    return await service.list_documents_for_user(current_user.id)
