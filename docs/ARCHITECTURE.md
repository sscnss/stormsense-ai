# Architecture notes

## Objective

StormSense AI demonstrates a safe, reviewable pipeline for converting multiple storm-related updates into one structured risk summary.

## Components

1. **Input models** validate timestamps, text, coordinates, wind speed, and pressure.
2. **Data loader** loads bundled synthetic updates for a zero-configuration demo.
3. **Deterministic analyzer** produces reproducible output when no model is configured.
4. **GPT-5.6 analyzer** optionally synthesizes normalized updates through the OpenAI Responses API.
5. **Fallback controller** catches API, parsing, and validation failures and returns deterministic output.
6. **FastAPI layer** exposes health, source-update, and analysis endpoints.
7. **Static dashboard** provides a browser demonstration without a separate frontend build step.

## Trust boundaries

- The OpenAI API key stays on the server and is never returned to the browser.
- The demo data is explicitly synthetic.
- Model output is validated through the `AlertAnalysis` Pydantic model.
- AI failure does not prevent the application from returning a deterministic result.
- Every result includes a safety disclaimer.

## Production gaps

This prototype does not implement live agency ingestion, official forecast verification, authentication, source provenance URLs, rate limiting, persistent storage, alert delivery, audit logs, or human approval. Those are required before any operational deployment.
