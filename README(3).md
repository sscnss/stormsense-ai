# StormSense AI

StormSense AI is an AI-assisted typhoon monitoring and early-warning prototype designed to transform public weather reports, satellite updates, and news bulletins into clear, actionable risk summaries.

Its goal is simple: **help people understand storm risks earlier and respond more effectively.**

> **Project status:** Hackathon prototype. Forecasts and alerts produced by this project are informational and must not replace official warnings from national meteorological and emergency-management authorities.

## Features

- Consolidates typhoon-related updates from multiple public sources
- Normalizes weather bulletins into structured records
- Produces concise, human-readable risk summaries
- Highlights changes in storm track, intensity, and potentially affected regions
- Supports modular ingestion, analysis, and alert-generation components
- Provides a foundation for API and web-based interfaces

## How Codex Was Used

Codex supported the software-engineering workflow throughout development. It was used to:

- Generate the initial project structure and backend scaffolding
- Implement and refine data-ingestion and parsing utilities
- Refactor multi-file modules during rapid prototype iterations
- Draft API routes and structured alert-output formats
- Create tests, debugging checks, and technical documentation
- Review implementation details and improve code maintainability

Codex accelerated development while the project team retained responsibility for reviewing, testing, and integrating the generated code.

## How GPT-5.6 Was Used

GPT-5.6 was used as the reasoning and synthesis layer of the prototype. It helped to:

- Summarize weather updates from multiple sources
- Identify relevant risk signals in noisy or partially conflicting reports
- Compare new bulletins with earlier observations
- Generate readable alerts describing track, intensity, timing, and affected areas
- Structure multi-step analysis into concise, actionable outputs
- Support prompt iteration and evaluation of alert clarity

All AI-generated outputs should be validated against authoritative meteorological information before operational use.

## Architecture Overview

```text
Weather agencies     News bulletins     Satellite updates
        \                  |                  /
         \                 |                 /
          ---- Data ingestion and normalization ----
                              |
                              v
                    GPT-5.6 reasoning layer
                              |
                              v
                  Risk analysis and alert output
                              |
                              v
                       Web UI and API
```

## Suggested Tech Stack

- Python
- FastAPI or Flask
- Node.js
- React
- OpenAI API
- Pandas and NumPy
- Docker
- GitHub Actions

The exact dependencies should be updated to match the submitted implementation.

## Installation

```bash
git clone https://github.com/sscnss/stormsense-ai.git
cd stormsense-ai
pip install -r requirements.txt
```

## Running the Project

Backend example:

```bash
python main.py
```

Frontend example:

```bash
npm install
npm start
```

## Example API Routes

```text
GET /api/typhoon/current
GET /api/typhoon/forecast
GET /api/alerts/latest
```

These routes are illustrative and should be updated to match the implemented API.

## Project Goal

StormSense AI aims to make complex typhoon information easier to understand, helping communities prepare earlier while keeping official meteorological warnings as the authoritative source.

## Responsible Use

StormSense AI is a prototype and is not an official forecasting or emergency-warning service. Do not rely on it as the sole basis for evacuation, travel, maritime, aviation, or other safety-critical decisions.

## License

MIT License

Copyright © 2026
