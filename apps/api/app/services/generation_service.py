from typing import Any, Protocol

from google import genai

from app.core.config import Settings, get_settings


class GenerationClient(Protocol):
    models: Any


class GenerationService:
    def __init__(
        self,
        settings: Settings | None = None,
        client: GenerationClient | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.client = client or genai.Client(api_key=self.settings.gemini_api_key)

    def generate_text(self, prompt: str) -> str:
        result = self.client.models.generate_content(
            model=self.settings.default_generation_model,
            contents=prompt,
        )
        text = getattr(result, "text", None)
        if isinstance(text, str) and text.strip():
            return text.strip()

        raise GenerationServiceError("Gemini returned an empty answer.")


class GenerationServiceError(Exception):
    pass
