from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from naish.api.main import create_app
from naish.config import Settings

pytestmark = pytest.mark.integration


def make_client() -> TestClient:
    settings = Settings(
        app_env="test",
        model_path=Path("artifacts/nasih_model.joblib"),
        store_backend="memory",
    )
    return TestClient(create_app(settings))


def test_health_and_readiness_are_separate_and_healthy() -> None:
    with make_client() as client:
        health = client.get("/health")
        ready = client.get("/ready")

    assert health.status_code == 200
    assert health.json()["data"]["status"] == "alive"
    assert ready.status_code == 200
    assert ready.json()["data"]["status"] == "ready"


def test_valid_prediction_uses_unified_envelope_and_trace_id() -> None:
    with make_client() as client:
        response = client.post(
            "/v1/predict",
            headers={"X-Trace-ID": "test-trace-123"},
            json={"monthly_cash_flow_sar": 150_000, "registration_age_months": 60},
        )

    body = response.json()
    assert response.status_code == 200
    assert response.headers["X-Trace-ID"] == "test-trace-123"
    assert body["trace_id"] == "test-trace-123"
    assert body["error"] is None
    assert body["data"]["decision"] == "auto_approve"
    assert 0.0 <= body["data"]["default_probability"] <= 1.0


def test_unknown_field_is_rejected() -> None:
    with make_client() as client:
        response = client.post(
            "/v1/predict",
            json={
                "monthly_cash_flow_sar": 50_000,
                "registration_age_months": 24,
                "unexpected": "not allowed",
            },
        )

    body = response.json()
    assert response.status_code == 422
    assert body["data"] is None
    assert body["error"]["code"] == "validation_error"
    assert body["trace_id"]


def test_numeric_range_is_enforced() -> None:
    with make_client() as client:
        response = client.post(
            "/v1/predict",
            json={"monthly_cash_flow_sar": 50_000, "registration_age_months": 0},
        )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_stats_extension_counts_predictions() -> None:
    with make_client() as client:
        before = client.get("/v1/stats").json()["data"]["predictions_processed"]
        client.post(
            "/v1/predict",
            json={"monthly_cash_flow_sar": 80_000, "registration_age_months": 36},
        )
        after = client.get("/v1/stats").json()["data"]["predictions_processed"]

    assert after == before + 1


class NotReadyStore:
    def is_ready(self) -> bool:
        return False


def test_ready_returns_503_when_supporting_service_is_unavailable() -> None:
    with make_client() as client:
        original_store = client.app.state.store
        client.app.state.store = NotReadyStore()
        response = client.get("/ready")
        client.app.state.store = original_store

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "not_ready"
