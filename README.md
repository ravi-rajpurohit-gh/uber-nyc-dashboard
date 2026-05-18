# NYC Uber Pickups Dashboard

An end-to-end data + AI engineering project built on ~1M Uber pickup records from NYC (September 2014). The app demonstrates a structured data pipeline, geospatial enrichment, interactive analytics, and an LLM-powered analyst you can query in plain English.

**[Live demo →](https://uber-nyc-dashboard.streamlit.app/)**

---

## What it does

| Page | Description |
|------|-------------|
| **Home** | KPI cards, anomaly-highlighted hourly demand bar chart, and an hour × day-of-week heatmap |
| **Map Explorer** | Pydeck heatmap or scatter layer filtered by hour and borough |
| **AI Analyst** | Chat interface backed by an LLM with function calling — ask questions in plain English and get answers with live charts |

---

## Architecture

```
pipeline/
├── ingest.py      # Load CSV, validate schema (raises on missing columns)
├── transform.py   # Parse datetime, engineer features, assign borough via bounding-box lookup
└── aggregate.py   # Pre-computed rollups: hourly, borough, heatmap, z-score anomaly detection

pages/
├── home.py            # Overview: KPIs + charts
├── 1_Map_Explorer.py  # Pydeck heatmap/scatter
└── 2_AI_Analyst.py    # LLM chat with OpenAI-compatible function calling

app.py   # Navigation entry point (st.navigation)
```

The pipeline follows an **ingest → validate → enrich → aggregate** pattern. Each layer is independently cacheable and testable.

---

## AI Analyst

The AI Analyst page uses **function/tool calling** to ground the LLM's responses in real data. When you ask a question, the model selects the appropriate analysis function, the app executes it against the dataset, and the model interprets the result — no hallucinated numbers.

**Functions available to the model:**

- `get_hourly_breakdown(borough?)` — pickup counts by hour, optional borough filter
- `get_borough_breakdown()` — total pickups per borough
- `get_day_hour_heatmap()` — hour × day-of-week demand matrix
- `get_weekend_vs_weekday()` — weekday vs weekend hourly comparison
- `get_peak_stats()` — peak hour, top borough, statistically anomalous hours

Each response includes a collapsible **Usage** panel showing prompt tokens, completion tokens, total tokens, and end-to-end latency — summed across both LLM calls per turn (tool selection + result interpretation).

### LLM providers

The app is provider-agnostic. It checks for a `GROQ_API_KEY` environment variable at startup:

| Environment | Provider | Model |
|-------------|----------|-------|
| Local (default) | [Ollama](https://ollama.com) | `llama3.2` |
| Deployed / `GROQ_API_KEY` set | [Groq](https://console.groq.com) | `llama-3.3-70b-versatile` |

Same code, swapped endpoint — no provider lock-in.

---

## Running locally

**Prerequisites:** Python 3.10+

```bash
git clone https://github.com/ravi-rajpurohit-gh/uber-nyc-dashboard.git
cd uber-nyc-dashboard
pip install -r requirements.txt
```

**Option A — Local LLM via Ollama**

```bash
brew install ollama
ollama pull llama3.2
ollama serve          # runs on localhost:11434
streamlit run app.py
```

**Option B — Cloud inference via Groq (free tier)**

```bash
export GROQ_API_KEY=your_key_here
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## Tech stack

| Layer | Tools |
|-------|-------|
| Data pipeline | `pandas`, `numpy` |
| Visualisation | `plotly`, `pydeck` |
| LLM integration | `openai` SDK (OpenAI-compatible) |
| LLM providers | Ollama (local), Groq (cloud) |
| App framework | `streamlit` |

---

## Dataset

~1 million Uber pickup records for New York City, September 2014. Fields: `date/time`, `lat`, `lon`, `base`. The raw CSV is bundled in the repo; borough labels are derived at runtime via spatial lookup.

---

## License

Apache 2.0 — see [LICENSE](LICENSE).
