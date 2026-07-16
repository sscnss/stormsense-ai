from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["app"] == "StormSense AI"
    assert payload["configured_model"]


def test_sample_updates_are_available() -> None:
    response = client.get("/api/updates")
    assert response.status_code == 200
    updates = response.json()
    assert len(updates) == 3
    assert all("source" in item for item in updates)


def test_deterministic_latest_alert() -> None:
    response = client.get("/api/alerts/latest?use_ai=false")
    assert response.status_code == 200
    alert = response.json()
    assert alert["mode"] == "deterministic"
    assert alert["severity"] in {"low", "moderate", "high", "extreme"}
    assert alert["source_count"] == 3
    assert alert["storm_name"] == "Kestrel"


def test_post_analyze_uses_sample_data_when_updates_empty() -> None:
    response = client.post("/api/analyze", json={"updates": [], "use_ai": False})
    assert response.status_code == 200
    assert response.json()["source_count"] == 3


def test_invalid_update_is_rejected() -> None:
    response = client.post(
        "/api/analyze",
        json={
            "use_ai": False,
            "updates": [
                {
                    "source": "",
                    "observed_at": "2026-07-16T00:00:00Z",
                    "title": "Example",
                    "content": "Example",
                }
            ],
        },
    )
    assert response.status_code == 422
