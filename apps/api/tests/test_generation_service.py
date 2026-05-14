from app.core.config import Settings
from app.services.generation_service import GenerationService


class FakeGenerationResult:
    text = " Generated answer. "


class FakeModels:
    def __init__(self) -> None:
        self.calls: list[dict[str, str]] = []

    def generate_content(self, *, model: str, contents: str) -> FakeGenerationResult:
        self.calls.append({"model": model, "contents": contents})
        return FakeGenerationResult()


class FakeClient:
    def __init__(self) -> None:
        self.models = FakeModels()


def test_generation_service_returns_generated_text() -> None:
    client = FakeClient()
    service = GenerationService(
        settings=Settings(
            gemini_api_key="test-key",
            default_generation_model="test-generation-model",
        ),
        client=client,
    )

    result = service.generate_text("Grounded prompt")

    assert result == "Generated answer."
    assert client.models.calls == [
        {
            "model": "test-generation-model",
            "contents": "Grounded prompt",
        }
    ]
