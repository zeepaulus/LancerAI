"""Smoke test — khởi động ứng dụng, kiểm tra bề mặt API và OpenAPI."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


def test_root_banner(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "LancerAI"
    assert body["status"] == "ok"
    assert body["api_prefix"] == "/api/v1"
    assert isinstance(body["endpoints"], list)


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_openapi_loads(client: TestClient) -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "/api/v1/auth/signup" in schema["paths"]
    assert "/api/v1/extraction/upload" in schema["paths"]
    assert "/api/v1/optimization/analyze" in schema["paths"]
    assert "/api/v1/jobs/match" in schema["paths"]
    assert "/api/v1/interview/sessions" in schema["paths"]


def test_interview_health(client: TestClient) -> None:
    response = client.get("/api/v1/interview/health")
    assert response.status_code == 200
    assert response.json()["module"] == "interview"
