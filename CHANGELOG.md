# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [0.2.0] — 2026-05-17

Major rebuild. Transformed the project from a Streamlit tutorial into a
multi-page data + AI engineering portfolio application.

### Added — Data Pipeline
- `pipeline/ingest.py` — CSV loader with schema validation; raises on missing columns
- `pipeline/transform.py` — datetime parsing, hour/day_name/is_weekend feature engineering, borough assignment via bounding-box spatial lookup
- `pipeline/aggregate.py` — pre-computed rollups: hourly counts, borough counts, hour × day heatmap, weekday vs weekend split, z-score anomaly detection
- `pipeline/ingest.py` — parquet caching on first load (~4x faster than gzip CSV on subsequent runs)
- `data.py` — single shared `get_data()` using `@st.cache_resource`; loaded once, shared across all pages and sessions

### Added — Pages
- **Home** — KPI cards (total pickups, peak hour, top borough, active bases), anomaly-highlighted hourly bar chart, hour × day demand heatmap
- **Map Explorer** — Pydeck heatmap and scatter layers, filterable by hour of day and borough
- **AI Analyst** — LLM-backed chat interface using OpenAI function/tool calling; model selects and executes the appropriate analysis function, then interprets results in plain English

### Added — AI Layer
- Five analysis tools exposed to the LLM: `get_hourly_breakdown`, `get_borough_breakdown`, `get_day_hour_heatmap`, `get_weekend_vs_weekday`, `get_peak_stats`
- Provider-agnostic LLM client: uses local Ollama (`llama3.2`) by default; switches to Groq (`llama-3.3-70b-versatile`) when `GROQ_API_KEY` is set — zero code changes required
- Token usage tracking (prompt + completion + total) and end-to-end latency displayed per response

### Added — UI & Theme
- `.streamlit/config.toml` — navy blue primary, off-white backgrounds, sans-serif font
- `style.py` — shared Plotly `"dashboard"` template (consistent font, grid, colour palette) applied to all charts; global CSS hides Streamlit footer and hamburger, polishes metric cards
- Sidebar brand header; no emoji in page titles or UI elements
- Consistent blue colour palette across all charts

### Added — Infrastructure
- `st.navigation` API for clean multi-page routing with explicit page titles
- `.github/workflows/keep-alive.yml` — scheduled ping to prevent Streamlit Cloud hibernation
- Dev Container configuration

### Changed
- `app.py` rebuilt from 41-line tutorial into navigation entry point
- `requirements.txt` expanded: added `plotly`, `pydeck`, `openai`, `pyarrow`

### Removed
- Original single-page tutorial app (bar chart, basic `st.map`, single slider)

---

## [0.1.0] — 2024 (initial)

- Streamlit tutorial app: hourly bar chart, `st.map` with hour filter, raw data toggle
- Deployed to Streamlit Cloud

---

## Planned

- [ ] Multi-month data — load all six months (April–September 2014) with month selector and month-over-month comparison
- [ ] Borough choropleth — swap bounding-box lookup for GeoPandas spatial join against NYC Open Data GeoJSON
- [ ] Demand forecasting tab — time-series model (Prophet or ARIMA) to predict next-24h pickup demand
