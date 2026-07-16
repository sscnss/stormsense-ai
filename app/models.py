"""Pydantic request and response models."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class WeatherUpdate(BaseModel):
    source: str = Field(min_length=1, max_length=120)
    observed_at: datetime
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=4000)
    wind_kph: float | None = Field(default=None, ge=0, le=500)
    pressure_hpa: float | None = Field(default=None, ge=800, le=1100)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)

    @field_validator("source", "title", "content")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value


class AnalysisRequest(BaseModel):
    updates: list[WeatherUpdate] = Field(default_factory=list, max_length=50)
    use_ai: bool = True


class AIAlertContent(BaseModel):
    """Schema requested directly from the OpenAI Responses API."""

    storm_name: str = Field(min_length=1, max_length=120)
    severity: Literal["low", "moderate", "high", "extreme"]
    headline: str = Field(min_length=1, max_length=240)
    summary: str = Field(min_length=1, max_length=2000)
    key_changes: list[str] = Field(min_length=1, max_length=10)
    affected_areas: list[str] = Field(min_length=1, max_length=20)
    recommended_actions: list[str] = Field(min_length=1, max_length=10)


class AlertAnalysis(BaseModel):
    storm_name: str
    generated_at: datetime
    severity: Literal["low", "moderate", "high", "extreme"]
    headline: str
    summary: str
    key_changes: list[str]
    affected_areas: list[str]
    recommended_actions: list[str]
    source_count: int = Field(ge=1)
    model_used: str
    mode: Literal["deterministic", "ai"]
    disclaimer: str


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    app: str
    version: str
    ai_enabled: bool
    configured_model: str
