"""FastAPI application for StormSense AI."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.models import AlertAnalysis, AnalysisRequest, HealthResponse, WeatherUpdate
from app.services.analyzer import analyze_updates
from app.services.data_loader import load_sample_updates

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Hackathon prototype for synthesizing typhoon-related updates. "
        "Not an official forecasting or warning service."
    ),
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        app=settings.app_name,
        version=settings.app_version,
        ai_enabled=settings.ai_enabled,
        configured_model=settings.openai_model,
    )


@app.get("/api/updates", response_model=list[WeatherUpdate])
def sample_updates() -> list[WeatherUpdate]:
    return load_sample_updates()


@app.post("/api/analyze", response_model=AlertAnalysis)
def analyze(request: AnalysisRequest) -> AlertAnalysis:
    updates = request.updates or load_sample_updates()
    try:
        return analyze_updates(updates, use_ai=request.use_ai)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/api/alerts/latest", response_model=AlertAnalysis)
def latest_alert(
    use_ai: bool = Query(default=True, description="Use GPT-5.6 when configured"),
) -> AlertAnalysis:
    return analyze_updates(load_sample_updates(), use_ai=use_ai)
