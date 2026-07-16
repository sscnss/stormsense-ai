from types import SimpleNamespace

import openai
from fastapi.testclient import TestClient

from app.main import app
from app.models import AIAlertContent
from app.services import analyzer
from app.services.data_loader import load_sample_updates

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


def test_ai_analysis_uses_responses_structured_output(monkeypatch) -> None:
    parsed = AIAlertContent(
        storm_name="Kestrel",
        severity="high",
        headline="Synthetic high-risk signal",
        summary="Synthetic updates indicate strengthening; official authorities remain authoritative.",
        key_changes=["Reported winds increased."],
        affected_areas=["Okinawa"],
        recommended_actions=["Monitor official warnings."],
    )
    captured: dict = {}

    class FakeResponses:
        def parse(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(output_parsed=parsed)

    class FakeOpenAI:
        def __init__(self, *, api_key: str) -> None:
            assert api_key == "test-key"
            self.responses = FakeResponses()

    monkeypatch.setattr(openai, "OpenAI", FakeOpenAI)
    monkeypatch.setattr(
        analyzer,
        "settings",
        SimpleNamespace(
            openai_api_key="test-key",
            openai_model="gpt-5.6",
            openai_reasoning_effort="medium",
        ),
    )

    result = analyzer.ai_analysis(load_sample_updates())

    assert result.mode == "ai"
    assert result.model_used == "gpt-5.6"
    assert result.severity == "high"
    assert captured["text_format"] is AIAlertContent
    assert captured["reasoning"] == {"effort": "medium"}


def test_ai_failure_falls_back_to_deterministic(monkeypatch) -> None:
    monkeypatch.setattr(analyzer, "settings", SimpleNamespace(ai_enabled=True))

    def fail(_updates):
        raise RuntimeError("simulated provider failure")

    monkeypatch.setattr(analyzer, "ai_analysis", fail)
    result = analyzer.analyze_updates(load_sample_updates(), use_ai=True)

    assert result.mode == "deterministic"
    assert result.source_count == 3
