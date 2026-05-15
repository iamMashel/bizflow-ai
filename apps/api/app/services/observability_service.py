import logging
import time
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any
from uuid import UUID

from langfuse import Langfuse

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


class ObservabilityService:
    def __init__(self, settings: Settings | None = None, client: Any | None = None) -> None:
        self.settings = settings or get_settings()
        self.enabled = (
            self.settings.langfuse_enabled
            and bool(self.settings.langfuse_public_key)
            and bool(self.settings.langfuse_secret_key)
        )
        self.client = client
        if self.client is None and self.enabled:
            self.client = Langfuse(
                public_key=self.settings.langfuse_public_key,
                secret_key=self.settings.langfuse_secret_key,
                host=self.settings.langfuse_host,
                tracing_enabled=True,
            )

    @contextmanager
    def trace(
        self,
        *,
        operation: str,
        user_id: UUID | None = None,
        document_id: UUID | None = None,
        workflow_id: UUID | None = None,
        model: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Iterator[None]:
        if not self.enabled or self.client is None:
            yield
            return

        safe_metadata = self._safe_metadata(
            operation=operation,
            user_id=user_id,
            document_id=document_id,
            workflow_id=workflow_id,
            model=model,
            metadata=metadata,
        )
        start = time.perf_counter()
        span = self.client.start_observation(
            name=operation,
            as_type="generation" if model else "span",
            metadata={**safe_metadata, "success": None},
            model=model,
        )
        try:
            yield
        except Exception as exc:
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            span.update(
                metadata={
                    **safe_metadata,
                    "success": False,
                    "latency_ms": latency_ms,
                    "error_type": type(exc).__name__,
                },
                level="ERROR",
                status_message=str(exc),
            )
            raise
        else:
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            span.update(
                metadata={**safe_metadata, "success": True, "latency_ms": latency_ms},
                level="DEFAULT",
            )
        finally:
            span.end()

    @staticmethod
    def _safe_metadata(
        *,
        operation: str,
        user_id: UUID | None,
        document_id: UUID | None,
        workflow_id: UUID | None,
        model: str | None,
        metadata: dict[str, Any] | None,
    ) -> dict[str, Any]:
        safe_metadata: dict[str, Any] = {
            "operation": operation,
            "user_id": str(user_id) if user_id is not None else None,
            "document_id": str(document_id) if document_id is not None else None,
            "workflow_id": str(workflow_id) if workflow_id is not None else None,
            "model": model,
        }
        if metadata:
            safe_metadata.update(metadata)
        return {key: value for key, value in safe_metadata.items() if value is not None}
