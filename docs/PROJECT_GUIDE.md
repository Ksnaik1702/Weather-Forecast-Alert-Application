# Complete Project Guide

## 1. Project explanation
A Weather Forecast & Alert Application retrieves current conditions and future forecasts for selected places, then highlights weather that may affect plans.

**Simple explanation:** Enter a place to see the weather and get notices about rain, heat, wind, storms, poor visibility or air quality.

**Technical explanation:** A provider adapter requests JSON from public weather services; normalization standardizes the data and units; a rules engine evaluates forecast thresholds; SQLite stores raw provenance and normalized observations; FastAPI exposes forecasts and alerts; Streamlit provides maps, charts, and reports.

**Workflow:** user enters a city → geocoding resolves coordinates/time zone → weather and optional air-quality APIs return JSON → data is normalized → forecasts are analyzed → alert rules fire → API/dashboard presents results → SQLite and CSV retain reports.

Useful for individuals and teams in travel, farming, logistics, energy, outdoor events and public safety. This educational project does not replace official warnings.

## 2. Technology choices
| Option | Tools | Difficulty | Expected result |
|---|---|---|---|
| A · Easy | Python, requests, JSON, CSV, sample data, Matplotlib | Beginner | Terminal forecast, simple rules, saved CSV/chart |
| B · Student choice | Python 3.11+, httpx, Pydantic, FastAPI, SQLite, Streamlit, Pandas, Matplotlib, Open-Meteo | Intermediate | Live API, offline demo, dashboard, map, alerts, reports |
| C · Advanced | B plus Next.js, Tailwind, Recharts/Leaflet, Redis, scheduler, Docker, notification providers | Advanced | Multi-location, scheduled service and deployed web client |

Option B is selected: a substantial Python project that works without paid credentials. Open-Meteo forecast, geocoding and air-quality endpoints require no API key.

## 3. Architecture
```text
City + configurable thresholds
        ↓
Geocoding → Open-Meteo forecast + optional air quality
        ↓ JSON
Provider adapter → normalized current / 48-hour / 7-day data
        ↓
Rules: rain · heat/heatwave · humidity · wind · UV · storm · fog · AQI
    ├─ FastAPI: locations, forecasts, alerts, history, CSV
    ├─ Streamlit: metrics, alerts, charts, map and forecast table
    └─ SQLite: locations, raw responses, hourly/daily series, alert log
```
The project normalizes temperature to °C, rainfall to mm, wind to m/s and visibility to meters in provider payloads (visibility is stored as km). The dashboard converts wind to km/h for readability. Each location retains its timezone.

## 4. Ten implementation phases
| Phase | What and why | Expected result | Common beginner mistake |
|---|---|---|---|
| 1. Setup | Install Python 3.11+ and Git; establish a consistent interpreter | Working Python environment | Installing packages into another Python |
| 2. Folder creation | Separate API, source, data, reports and docs | Easy-to-navigate repository | Mixing generated data with source |
| 3. API setup | Use key-free Open-Meteo; keep optional messaging secrets in `.env` | Safe live provider configuration | Committing real credentials |
| 4. Fetching | Geocode city, request weather/AQI with timeout and transient retries | Provider JSON | No timeout or status check |
| 5. Parsing | Normalize current, 48 hourly and 7 daily values | Stable units and model | Mixing timezone or units |
| 6. Forecast analysis | Summarize temperatures, rain and wind | Hourly/daily outlook | Treating missing values as zero |
| 7. Alert logic | Evaluate thresholds and produce severity/advice | Rain, heat, humidity, wind, UV, storm, fog and AQI notices | Presenting demo rules as official warnings |
| 8. Visualization | Show weather, risk, charts, map and table | Streamlit dashboard | Leaving misleading sample values on a failed live lookup |
| 9. Reports | Save raw/normalized SQLite records and export CSV | Reproducible evidence | Committing generated/private data unintentionally |
| 10. GitHub | Review ignored files, README and screenshots before pushing | Portfolio-ready repository | Publishing `.env`, tokens, or personal details |

## 5. Folder structure
```text
api/                 FastAPI routes
src/weather_app/     provider, models, rules, service, storage, simulation
data/                local SQLite history (created on run; ignored)
outputs/              generated CSV reports (ignored)
images/               screenshots for README
reports/              project evidence
jobs/                 scheduled refresh and optional Telegram notifier
tests/                alert and normalization checks
docs/                 this project guide
README.md              project overview
requirements.txt       Python dependencies
.env.example           safe template; copy to local .env if using Telegram
.gitignore             excludes secrets, databases, outputs and caches
main.py                offline command-line demo
dashboard.py           Streamlit dashboard
Dockerfile             FastAPI container
```

## 6. Install and secure credentials
Windows PowerShell:
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```
macOS/Linux:
```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```
The live weather provider has no API key. Optional Telegram delivery reads `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` from a local `.env` file; make it by copying `.env.example` to `.env` and filling in your own values. `python-dotenv` loads it for the scheduler. `.gitignore` excludes `.env`; commit only `.env.example`. Never put credentials in source code, screenshots, reports or GitHub.

## 7. Project code map
- `provider.py`: async geocoding, forecast and optional AQI; timeouts and retries for transient errors.
- `models.py`: Pydantic validation of normalized responses.
- `service.py`: safe parsing, sorting/deduplicating timestamps, unit normalization and orchestration.
- `alerts.py`: editable threshold rules and human-readable messages.
- `storage.py`: saved locations, raw payload provenance, normalized time-series, alert log and CSV export.
- `demo.py` / `main.py`: deterministic offline alert simulation and CLI report.
- `api/app.py`: location, weather, forecast, alert, history and CSV endpoints; Swagger at `/docs`.
- `dashboard.py`: green-themed Streamlit metrics, notices, charts, OpenStreetMap and report download.
- `jobs/refresh.py`: optional refresh every two hours; alert dispatch check every 30 minutes.
- `jobs/notify.py`: optional Telegram delivery with 12-hour per-location/rule duplicate suppression.

## 8. Virtual simulation and evidence
Run `python main.py` or choose **Simulation (offline)** in the dashboard. It creates a fixed synthetic New Delhi scenario with intentionally high heat, humidity, rain, wind, UV, storm, fog and AQI so each rule can be demonstrated without internet or a key. The UI labels this as sample data. Choose **Live forecast** to retrieve the entered city’s actual provider forecast. If live retrieval fails, the dashboard clears the prior readings instead of showing stale values.

The simulated record has the same location/current/hourly/daily/alerts shape as the live pipeline. Rules compare it with thresholds in `src/weather_app/config.py`. CLI/dashboard/API can produce a CSV; snapshots and raw/live series persist in local SQLite. Real deployments replace the sample payload with a provider response through the adapter.

Never upload `.env`, API keys/tokens, private contact data or unreviewed raw data. The database and CSV outputs are ignored by Git by default; only add curated, safe report evidence deliberately.

## 9. Run instructions
```powershell
# Offline command-line report
python main.py

# API server and interactive docs
uvicorn api.app:app --reload
# open http://127.0.0.1:8000/docs

# Dashboard in another terminal
python -m streamlit run dashboard.py

# Optional scheduler (stop with Ctrl+C)
python -m jobs.refresh
```
API examples: `/health`, `/locations`, `POST /locations?city=Pune`, `/weather?city=Pune&mode=live`, `/weather?city=Pune&mode=simulation`, `/forecast/hourly?city=Pune&hours=24`, `/forecast/daily?city=Pune&days=7`, `/alerts?city=Pune`, `/history`, and `/report.csv?city=Pune&mode=simulation`. Saved-location forecast routes also accept `location_id`. Expected CLI output includes current conditions, any fired alerts, and a CSV path under `outputs/`. Live mode needs internet; simulation works offline.

## 10. GitHub publishing
Repository name: `weather-forecast-alert-application`.
Description: `Python weather forecasting and risk alerts with FastAPI, Streamlit, Open-Meteo, SQLite, maps, charts and offline simulation.`
Suggested topics: `python`, `fastapi`, `weather-api`, `streamlit`, `open-meteo`, `data-visualization`, `alert-system`.

1. Create a GitHub repository under your account.
2. From this project directory:
```bash
git init
git add .
git status
git commit -m "Build weather forecast and alert app"
git branch -M main
git remote add origin <your-repository-url>
git push -u origin main
```
3. Check `git status` before pushing; confirm `.env`, `data/weather.db`, and generated CSVs are ignored.
4. Add curated screenshots to `images/` and link them from README.

Useful commit messages: `Set up project structure`, `Integrate Open-Meteo forecast`, `Add normalized SQLite storage`, `Add weather risk rules`, `Build Streamlit dashboard`, `Add scheduled refresh and Telegram alerts`, `Document project and usage`.

## 11. README coverage
The repository README includes project overview, problem statement, industry relevance, features, tech stack, folders, API setup, install/run commands, sample output, screenshot guidance and learning outcomes. Keep it updated when thresholds, providers or routes change.

## 12. Six-day proof-building plan and screenshots
| Day | Deliverable / commit | Screenshot evidence |
|---|---|---|
| 1 · setup | folders/environment — `Set up project structure` | project folder |
| 2 · API | city lookup/provider — `Integrate Open-Meteo forecast` | API or live mode response |
| 3 · parsing | normalized current/hourly/daily — `Parse forecast data` | current conditions and forecast |
| 4 · rules | alerts/simulation — `Add configurable risk alerts` | generated alert messages |
| 5 · visualization | charts/map/CSV — `Build dashboard and reports` | dashboard, visualization, CSV |
| 6 · publish | README/GitHub — `Document project and usage` | repository preview |

Capture exactly: project-folder view; API docs or simulation terminal; current-weather metrics; hourly and 7-day forecasts; alert messages; generated CSV/report; chart and map; GitHub repository preview. Hide private paths, credentials and account details before sharing.

## 13. Industry relevance and limits
Weather-driven planning supports logistics, agriculture, energy, travel, event planning and public safety. Timely alerts can reduce delays, spoilage and downtime. The supplied brief cites possible operational savings of 10–20%; treat this as an illustrative industry claim, not a measured result of this student project. Provider-independent storage makes future signals easier to add. Examples include delivery routing, irrigation windows, solar maintenance, outdoor events and school heat advisories. SMB and enterprise teams both use weather intelligence in planning.

## 14. Interview preparation
**1. Explain your project.** I built a Python application that fetches current and forecast weather for a city, normalizes the data, checks configurable risk rules, and presents results in FastAPI and a Streamlit dashboard. It supports live Open-Meteo data and offline simulation, stores history in SQLite, and exports CSV reports.

**2. What problem does it solve?** It brings forecasts and practical weather warnings into one view so people can plan weather-sensitive work and travel.

**3. What technologies did you use?** Python, httpx, Pydantic, FastAPI, SQLite, Streamlit, Pandas, Matplotlib and Open-Meteo.

**4. How does the app fetch data?** It geocodes a city, requests forecast/AQI JSON, validates and normalizes it, then stores a raw copy and structured series.

**5. What is JSON and why is it used?** JSON is a text format for structured data; weather APIs use it to return nested current and forecast values.

**6. How does alert logic work?** Rules compare normalized values to thresholds and return a code, severity and user-facing advice.

**7. How are API errors handled?** Requests use timeouts and bounded retry for transient failures; unknown cities and provider errors become readable messages, while optional AQI failure does not stop weather results.

**8. What output does the app produce?** Current conditions, 48-hour and seven-day forecasts, alerts, SQLite history, a dashboard and CSV reports.

**9. How could it improve?** Add more providers, radar overlays, geofencing, deployment, and email/SMS notification adapters; the optional scheduler and Telegram adapter are already included.

**10. Explain it to a nontechnical person.** It checks the weather for a place and points out conditions that might affect your plans.

**HR explanation:** I built a complete Python project that demonstrates API integration, automation, data handling and visualization, and documented it so another person can run it.

**Technical explanation:** A provider adapter fetches external JSON; Pydantic validates normalized models; a rule engine evaluates thresholds; SQLite stores raw and normalized data; FastAPI exposes routes; Streamlit visualizes forecasts; an optional scheduled worker refreshes data and de-duplicates Telegram alerts.
