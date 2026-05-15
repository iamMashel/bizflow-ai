from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

DocumentStatus = Literal["pending", "ingesting", "processing", "ready", "completed", "failed"]
DocumentType = Literal[
    "cv",
    "client_brief",
    "invoice",
    "contract",
    "report",
    "proposal",
    "notes",
    "other",
]


class DocumentMetadata(BaseModel):
    document_type: DocumentType
    title: str | None
    summary: str
    entities: list[str]
    key_points: list[str]
    missing_information: list[str]
    recommended_actions: list[str]
    recommended_workflow: str | None
    confidence: float = Field(ge=0, le=1)


class DocumentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    status: DocumentStatus
    created_at: datetime
    summary: str | None = None
    metadata: dict[str, Any] | None = None


class DocumentUploadResponse(DocumentSummary):
    duplicate: bool


class DocumentIngestResponse(BaseModel):
    id: UUID
    status: DocumentStatus
    chunks_created: int


class DocumentMetadataResponse(BaseModel):
    id: UUID
    filename: str
    summary: str | None
    metadata: DocumentMetadata
