"""Storm update analysis with deterministic and optional GPT-5.6 paths."""

from __future__ import annotations

import json
import logging
import re
from datetime import UTC, datetime
from typing import Any


from app.config import settings
from app.models import AlertAnalysis, WeatherUpdate

logger = logging.getLogger(__name__)

DISCLAIMER = (
    "Prototype output only. Verify all information against official meteorological "
    "and emergency-management authorities."
)

AREA_KEYWORDS = {
    "Okinawa": ("okinawa", "ryukyu"),
    "Miyako Islands": ("miyako",),
    "Yaeyama Islands": ("yaeyama", "ishigaki"),
    "Taiwan": ("taiwan",),
    "East China Sea": ("east china sea",),
}


def _severity_from_wind(max_wind_kph: float) -> str:
    if max_wind_kph >= 178:
        return "extreme"
    if max_wind_kph >= 118:
        return "high"
    if max_wind_kph >= 63:
        return "moderate"
    return "low"


def _affected_areas(updates: list[WeatherUpdate]) -> list[str]:
    combined = " ".join(f"{item.title} {item.content}" for item in updates).lower()
    areas = [
        area
        for area, keywords in AREA_KEYWORDS.items()
        if any(keyword in combined for keyword in keywords)
    ]
    return areas or ["Area not confidently identified"]


def _storm_name(updates: list[WeatherUpdate]) -> str:
    combined = " ".join(f"{item.title} {item.content}" for item in updates)
    match = re.search(r"(?:Typhoon|Storm|Cyclone)\s+([A-Z][A-Za-z-]+)", combined)
    return match.group(1) if match else "Demo Cyclone"


def deterministic_analysis(updates: list[WeatherUpdate]) -> AlertAnalysis:
    """Generate a reproducible analysis without calling an external model."""
    if not updates:
        raise ValueError("At least one weather update is required")

    ordered = sorted(updates, key=lambda item: item.observed_at)
    winds = [item.wind_kph for item in ordered if item.wind_kph is not None]
    pressures = [item.pressure_hpa for item in ordered if item.pressure_hpa is not None]
    max_wind = max(winds, default=0.0)
    severity = _severity_from_wind(max_wind)
    name = _storm_name(ordered)
    areas = _affected_areas(ordered)

    key_changes: list[str] = []
    if len(winds) >= 2:
        delta = winds[-1] - winds[0]
        direction = "increased" if delta > 0 else "decreased" if delta < 0 else "remained stable"
        key_changes.append(f"Reported wind speed {direction} by {abs(delta):.0f} km/h across the demo updates.")
    elif winds:
        key_changes.append(f"Latest reported wind speed is {winds[-1]:.0f} km/h.")

    if len(pressures) >= 2:
        delta = pressures[-1] - pressures[0]
        direction = "rose" if delta > 0 else "fell" if delta < 0 else "was unchanged"
        key_changes.append(f"Reported central pressure {direction} by {abs(delta):.0f} hPa.")
    elif pressures:
        key_changes.append(f"Latest reported central pressure is {pressures[-1]:.0f} hPa.")

    key_changes.append(f"Potentially affected locations mentioned by sources: {', '.join(areas)}.")

    action_map = {
        "low": [
            "Continue monitoring official forecasts.",
            "Review local emergency information before travel.",
        ],
        "moderate": [
            "Monitor official updates more frequently.",
            "Secure loose outdoor objects and review household supplies.",
            "Check transport and maritime advisories before departure.",
        ],
        "high": [
            "Follow local authority instructions and prepare for service disruption.",
            "Avoid unnecessary coastal, maritime, and exposed-area travel.",
            "Charge devices and confirm an emergency communication plan.",
        ],
        "extreme": [
            "Act immediately on evacuation or shelter instructions from authorities.",
            "Stay away from coasts, rivers, and flood-prone areas.",
            "Use only official channels for safety-critical decisions.",
        ],
    }

    headline = f"{severity.title()} demo risk signal for {name}"
    summary = (
        f"{len(ordered)} synthetic source updates indicate maximum reported winds of "
        f"{max_wind:.0f} km/h. Mentions are concentrated around {', '.join(areas)}. "
        "This result demonstrates source synthesis and is not a live forecast."
    )

    return AlertAnalysis(
        storm_name=name,
        generated_at=datetime.now(UTC),
        severity=severity,
        headline=headline,
        summary=summary,
        key_changes=key_changes,
        affected_areas=areas,
        recommended_actions=action_map[severity],
        source_count=len(ordered),
        model_used="deterministic-v1",
        mode="deterministic",
        disclaimer=DISCLAIMER,
    )


def _clean_json_text(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _ai_payload(updates: list[WeatherUpdate]) -> str:
    payload: list[dict[str, Any]] = [
        item.model_dump(mode="json") for item in sorted(updates, key=lambda item: item.observed_at)
    ]
    return json.dumps(payload, ensure_ascii=False, indent=2)


def ai_analysis(updates: list[WeatherUpdate]) -> AlertAnalysis:
    """Use GPT-5.6 to synthesize updates into a structured alert."""
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    if not updates:
        raise ValueError("At least one weather update is required")

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("The openai package is not installed") from exc

    client = OpenAI(api_key=settings.openai_api_key)
    instructions = """
You are the reasoning layer for StormSense AI, a hackathon typhoon-information prototype.
Analyze only the supplied source updates. Do not invent observations, official warnings, or certainty.
Return one valid JSON object with exactly these keys:
storm_name, severity, headline, summary, key_changes, affected_areas, recommended_actions.
severity must be one of: low, moderate, high, extreme.
key_changes, affected_areas, and recommended_actions must be JSON arrays of concise strings.
Use calm, practical language. Explicitly distinguish uncertainty and mention that official authorities are authoritative.
Do not include Markdown fences or any text outside the JSON object.
""".strip()

    response = client.responses.create(
        model=settings.openai_model,
        reasoning={"effort": settings.openai_reasoning_effort},
        instructions=instructions,
        input=f"Analyze these normalized synthetic/demo updates:\n{_ai_payload(updates)}",
    )
    parsed = json.loads(_clean_json_text(response.output_text))

    return AlertAnalysis(
        storm_name=str(parsed["storm_name"]),
        generated_at=datetime.now(UTC),
        severity=str(parsed["severity"]).lower(),
        headline=str(parsed["headline"]),
        summary=str(parsed["summary"]),
        key_changes=[str(item) for item in parsed["key_changes"]],
        affected_areas=[str(item) for item in parsed["affected_areas"]],
        recommended_actions=[str(item) for item in parsed["recommended_actions"]],
        source_count=len(updates),
        model_used=settings.openai_model,
        mode="ai",
        disclaimer=DISCLAIMER,
    )


def analyze_updates(updates: list[WeatherUpdate], use_ai: bool = True) -> AlertAnalysis:
    """Analyze updates, falling back safely when the AI path is unavailable."""
    if use_ai and settings.ai_enabled:
        try:
            return ai_analysis(updates)
        except Exception as exc:  # External API failures must not break the demo.
            logger.warning("AI analysis failed; using deterministic fallback: %s", exc)
    return deterministic_analysis(updates)
