"""Load bundled synthetic demonstration data."""

from __future__ import annotations

import json
from pathlib import Path

from app.models import WeatherUpdate

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "sample_updates.json"


def load_sample_updates() -> list[WeatherUpdate]:
    """Return validated synthetic updates bundled with the repository."""
    with DATA_FILE.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return [WeatherUpdate.model_validate(item) for item in payload]
