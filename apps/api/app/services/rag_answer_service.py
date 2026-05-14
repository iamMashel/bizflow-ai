from uuid import UUID

from app.core.security import CurrentUser
from app.schemas.rag import RagAnswerResponse, RagCitation, RagSearchResult
from app.services.generation_service import GenerationService, GenerationServiceError
from app.services.rag_search_service import RagSearchService, RagSearchServiceError

NOT_ENOUGH_CONTEXT_MESSAGE = (
    "The uploaded documents do not contain enough information to answer that question."
)


class RagAnswerServiceError(Exception):
    def __init__(self, message: str, *, status_code: int = 502) -> None:
        super().__init__(message)
        self.status_code = status_code


class RagAnswerService:
    def __init__(
        self,
        search_service: RagSearchService,
        generation_service: GenerationService,
    ) -> None:
        self.search_service = search_service
        self.generation_service = generation_service

    async def answer(
        self,
        *,
        query: str,
        match_count: int,
        current_user: CurrentUser,
    ) -> RagAnswerResponse:
        try:
            chunks = await self.search_service.search(
                query=query,
                match_count=match_count,
                user_id=current_user.id,
                access_token=current_user.access_token,
            )
        except RagSearchServiceError as exc:
            raise RagAnswerServiceError(str(exc), status_code=exc.status_code) from exc

        citations = [self._citation_from_chunk(chunk) for chunk in chunks]
        if not chunks:
            return RagAnswerResponse(answer=NOT_ENOUGH_CONTEXT_MESSAGE, citations=[])

        prompt = self._build_prompt(query=query, chunks=chunks)
        try:
            answer = self.generation_service.generate_text(prompt)
        except GenerationServiceError as exc:
            raise RagAnswerServiceError("Unable to generate a grounded answer.") from exc

        return RagAnswerResponse(answer=answer, citations=citations)

    @staticmethod
    def _build_prompt(*, query: str, chunks: list[RagSearchResult]) -> str:
        context_blocks = "\n\n".join(
            (
                f"Source {index}\n"
                f"Document ID: {chunk.document_id}\n"
                f"Filename: {chunk.filename}\n"
                f"Chunk index: {chunk.chunk_index}\n"
                f"Content:\n{chunk.content}"
            )
            for index, chunk in enumerate(chunks, start=1)
        )

        return (
            "You are BizFlow AI. Answer the user question only from the retrieved document "
            "context below. If the context does not contain the answer, say exactly: "
            f"'{NOT_ENOUGH_CONTEXT_MESSAGE}'\n\n"
            "Cite useful source filenames and chunk indexes in the answer when relevant.\n\n"
            f"User question:\n{query}\n\n"
            f"Retrieved document context:\n{context_blocks}\n\n"
            "Grounded answer:"
        )

    @staticmethod
    def _citation_from_chunk(chunk: RagSearchResult) -> RagCitation:
        return RagCitation(
            document_id=UUID(str(chunk.document_id)),
            filename=chunk.filename,
            chunk_index=chunk.chunk_index,
            preview=_preview(chunk.content),
        )


def _preview(content: str, limit: int = 240) -> str:
    clean_content = " ".join(content.split())
    if len(clean_content) <= limit:
        return clean_content
    return f"{clean_content[:limit].rstrip()}..."
