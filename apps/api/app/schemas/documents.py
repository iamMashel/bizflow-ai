from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

DocumentStatus = Literal["pending", "ingesting", "ready", "failed"]


class DocumentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    status: DocumentStatus
    created_at: datetime
