from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.core.config import Settings, get_settings
from app.core.security import CurrentUser, get_current_user
from app.schemas.documents import DocumentSummary, DocumentUploadResponse
from app.services.document_service import DocumentService, DocumentServiceError

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".csv"}


def get_document_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> DocumentService:
    return DocumentService(settings)


def _file_extension(filename: str) -> str:
    if "." not in filename:
        return ""
    return f".{filename.rsplit('.', 1)[-1].lower()}"


def _validate_filename(filename: str | None) -> str:
    if filename is None or not filename.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must include a filename.",
        )

    clean_filename = filename.strip()
    if _file_extension(clean_filename) not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Allowed types: pdf, docx, txt, md, csv.",
        )

    return clean_filename


@router.get("", response_model=list[DocumentSummary])
async def list_documents(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[DocumentService, Depends(get_document_service)],
) -> list[DocumentSummary]:
    try:
        return await service.list_documents_for_user(
            user_id=current_user.id,
            access_token=current_user.access_token,
        )
    except DocumentServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[DocumentService, Depends(get_document_service)],
    settings: Annotated[Settings, Depends(get_settings)],
    file: Annotated[UploadFile, File(...)],
) -> DocumentUploadResponse:
    filename = _validate_filename(file.filename)
    content = await file.read()

    if len(content) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"Uploaded file exceeds the {settings.max_upload_bytes} byte limit.",
        )

    try:
        return await service.upload_document(
            user_id=current_user.id,
            access_token=current_user.access_token,
            filename=filename,
            mime_type=file.content_type,
            content=content,
        )
    except DocumentServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
