from fastapi.testclient import TestClient

from app.main import app


def test_documents_placeholder_returns_empty_list() -> None:
    client = TestClient(app)

    response = client.get("/documents")

    assert response.status_code == 200
    assert response.json() == []
