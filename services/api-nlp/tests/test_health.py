"""Test minimal qui passe dès le clone : /health répond 200."""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_returns_200() -> None:
    """GET /health retourne 200 et une structure valide même sans modèle chargé."""
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert "status" in body
    assert "model_loaded" in body
    assert body["status"] in {"ok", "loading", "error"}
    assert isinstance(body["model_loaded"], bool)