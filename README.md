# StormSense AI

StormSense AI is a hackathon prototype that turns multiple typhoon-related bulletins into a single, readable risk summary. It includes a FastAPI backend, a lightweight browser dashboard, synthetic demo data, deterministic fallback analysis, and optional GPT-5.6 analysis through the OpenAI Responses API.

> **Safety notice:** StormSense AI is not an official forecasting or emergency-warning service. Never use it as the sole basis for evacuation, travel, maritime, aviation, or other safety-critical decisions. Always follow national meteorological and emergency-management authorities.

## Demo capabilities

- Loads synthetic weather, satellite, and emergency-management updates
- Normalizes source updates into a consistent schema
- Produces a severity level, headline, summary, affected areas, key changes, and recommended actions
- Runs without an API key using deterministic fallback logic
- Optionally uses GPT-5.6 when `OPENAI_API_KEY` is configured
- Exposes a documented REST API through FastAPI
- Serves a responsive single-page dashboard
- Includes automated API tests and Docker support

## How Codex was used

Codex was used as the primary software-engineering assistant during the project. It helped to:

- Design the repository and module structure
- Generate and refine the FastAPI application
- Implement request/response models and data-loading utilities
- Build the deterministic fallback analyzer
- Integrate the OpenAI Responses API
- Create the browser demo interface
- Write tests, Docker configuration, and technical documentation
- Review code paths for error handling, maintainability, and safe fallback behavior

All Codex-generated work was reviewed and integrated by the project author.

## How GPT-5.6 was used

GPT-5.6 is the optional reasoning and synthesis layer. When enabled, it receives normalized source updates and is instructed to:

- Reconcile information from multiple bulletins
- Identify changes in track, intensity, timing, and affected areas
- Produce a concise structured alert
- Separate observed information from uncertainty
- Generate practical, non-alarmist recommended actions
- Preserve a clear warning that official authorities remain authoritative

The default model is the `gpt-5.6` alias. The application never exposes the API key to the browser. If the API is unavailable or returns invalid output, the backend automatically uses deterministic fallback analysis.

## Architecture

```text
Synthetic or external bulletins
            |
            v
  Normalization and validation
            |
            +----------------------+
            |                      |
            v                      v
 Deterministic analyzer     GPT-5.6 analyzer
            |              (optional API key)
            +----------+-----------+
                       |
                       v
              Structured risk alert
                       |
                       v
             FastAPI + browser dashboard
```

## Repository structure

```text
stormsense-ai/
├── app/
│   ├── data/
│   │   └── sample_updates.json
│   ├── services/
│   │   ├── analyzer.py
│   │   └── data_loader.py
│   ├── static/
│   │   ├── app.js
│   │   ├── index.html
│   │   └── styles.css
│   ├── config.py
│   ├── main.py
│   └── models.py
├── docs/
│   └── ARCHITECTURE.md
├── tests/
│   └── test_api.py
├── .env.example
├── .gitignore
├── Dockerfile
├── LICENSE
├── docker-compose.yml
├── main.py
├── pyproject.toml
└── requirements.txt
```

## Quick start

### 1. Clone and install

```bash
git clone https://github.com/sscnss/stormsense-ai.git
cd stormsense-ai
python -m venv .venv
```

Activate the virtual environment:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS or Linux
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

The application runs without an API key. To enable GPT-5.6:

```bash
cp .env.example .env
```

Then set:

```dotenv
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5.6
```

Do not commit `.env` or any API key.

### 3. Run

```bash
python main.py
```

Open:

- Dashboard: `http://localhost:8000`
- API documentation: `http://localhost:8000/docs`
- Health endpoint: `http://localhost:8000/api/health`

## API

### `GET /api/health`

Returns application status and whether AI mode is configured.

### `GET /api/updates`

Returns the synthetic demonstration bulletins.

### `POST /api/analyze`

Analyzes supplied updates. An empty `updates` array uses the bundled demonstration data.

Example request:

```json
{
  "updates": [],
  "use_ai": false
}
```

### `GET /api/alerts/latest?use_ai=false`

Generates a current alert from the bundled demonstration data.

## Run tests

```bash
pytest
```

## Docker

```bash
docker compose up --build
```

Then open `http://localhost:8000`.

## Extending the prototype

The bundled updates are synthetic. A production-oriented extension would add source-specific adapters, timestamp validation, deduplication, provenance links, caching, authentication, observability, and human review before publishing alerts.

## License

MIT License. See [LICENSE](LICENSE).
