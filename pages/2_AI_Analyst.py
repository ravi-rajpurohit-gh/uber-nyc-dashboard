import sys
import os
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from openai import OpenAI, APIConnectionError

from pipeline.ingest import load_raw
from pipeline.transform import enrich
from pipeline.aggregate import (
    hourly_counts,
    borough_counts,
    day_hour_heatmap,
    weekend_vs_weekday,
    anomaly_hours,
    peak_hour,
    peak_borough,
)

st.set_page_config(page_title="AI Analyst", page_icon="🤖", layout="wide")
st.title("AI Analyst")
st.caption("Ask questions about NYC Uber demand in plain English")


@st.cache_data(show_spinner="Loading data...")
def get_data():
    return enrich(load_raw())


data = get_data()


# ── LLM client — provider-agnostic ───────────────────────────────────────────
# Uses Groq (free cloud inference) when GROQ_API_KEY is set,
# otherwise falls back to a local Ollama instance.
def _get_client() -> tuple[OpenAI, str]:
    if os.getenv("GROQ_API_KEY"):
        return (
            OpenAI(
                api_key=os.environ["GROQ_API_KEY"],
                base_url="https://api.groq.com/openai/v1",
            ),
            "llama-3.3-70b-versatile",
        )
    return (
        OpenAI(api_key="ollama", base_url="http://localhost:11434/v1"),
        "llama3.2",
    )


# ── Tool definitions (OpenAI function-calling format) ────────────────────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_hourly_breakdown",
            "description": "Get pickup counts for each hour of the day, optionally filtered by borough.",
            "parameters": {
                "type": "object",
                "properties": {
                    "borough": {
                        "type": "string",
                        "description": (
                            "Borough to filter by. One of: Manhattan, Brooklyn, Queens, "
                            "Bronx, Staten Island, All. Defaults to All."
                        ),
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_borough_breakdown",
            "description": "Get total pickup counts broken down by NYC borough.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_day_hour_heatmap",
            "description": "Get a heatmap of pickups by hour of day and day of week.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weekend_vs_weekday",
            "description": "Compare hourly pickup patterns between weekdays and weekends.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_peak_stats",
            "description": (
                "Get summary statistics: peak hour, top borough, total pickups, "
                "and any statistically anomalous hours."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


# ── Tool execution ────────────────────────────────────────────────────────────
def _run_tool(name: str, args: dict) -> tuple[str, object | None]:
    """Returns (json_string_for_llm, optional_plotly_figure)."""
    if name == "get_hourly_breakdown":
        borough = args.get("borough", "All")
        df = data if borough == "All" else data[data["borough"] == borough]
        result = hourly_counts(df)
        fig = px.bar(
            result,
            x="hour", y="pickups",
            color="pickups", color_continuous_scale="Blues",
            title=f"Pickups by Hour — {borough}",
            labels={"hour": "Hour of Day", "pickups": "Pickups"},
        )
        fig.update_layout(coloraxis_showscale=False, margin=dict(t=40, b=0))
        return result.to_json(orient="records"), fig

    if name == "get_borough_breakdown":
        result = borough_counts(data)
        fig = px.bar(
            result[result["borough"] != "Other"],
            x="borough", y="pickups",
            color="pickups", color_continuous_scale="Oranges",
            title="Pickups by Borough",
            labels={"borough": "", "pickups": "Pickups"},
        )
        fig.update_layout(coloraxis_showscale=False, margin=dict(t=40, b=0))
        return result.to_json(orient="records"), fig

    if name == "get_day_hour_heatmap":
        result = day_hour_heatmap(data)
        fig = go.Figure(
            go.Heatmap(
                z=result.values,
                x=[f"{h:02d}:00" for h in result.columns],
                y=result.index.tolist(),
                colorscale="YlOrRd",
                hovertemplate="Hour: %{x}<br>Day: %{y}<br>Pickups: %{z:,}<extra></extra>",
            )
        )
        fig.update_layout(title="Demand Heatmap: Hour × Day of Week", margin=dict(t=40, b=0))
        return result.to_json(), fig

    if name == "get_weekend_vs_weekday":
        result = weekend_vs_weekday(data)
        fig = px.line(
            result,
            x="hour", y="pickups", color="period",
            title="Weekday vs Weekend Demand",
            labels={"hour": "Hour", "pickups": "Pickups", "period": ""},
        )
        fig.update_layout(margin=dict(t=40, b=0))
        return result.to_json(orient="records"), fig

    if name == "get_peak_stats":
        ah = anomaly_hours(data)
        stats = {
            "peak_hour": peak_hour(data),
            "peak_hour_label": f"{peak_hour(data):02d}:00",
            "top_borough": peak_borough(data),
            "total_pickups": len(data),
            "anomalous_hours": ah[ah["anomaly"]]["hour"].tolist(),
        }
        return json.dumps(stats), None

    return json.dumps({"error": f"Unknown tool: {name}"}), None


# ── Sidebar: setup instructions ───────────────────────────────────────────────
with st.sidebar:
    st.header("Setup")
    if os.getenv("GROQ_API_KEY"):
        st.success("Connected via Groq")
        st.caption("Model: llama-3.3-70b-versatile")
    else:
        st.info("Using local Ollama")
        st.caption("Model: llama3.2")
        st.markdown(
            """
**Install Ollama:**
```bash
brew install ollama
ollama pull llama3.2
ollama serve
```
Or set `GROQ_API_KEY` for free cloud inference via [Groq](https://console.groq.com).
            """
        )
    st.divider()
    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ── Session state ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a concise data analyst for NYC Uber Pickups (September 2014).
Dataset: ~100,000 pickup records. Fields: date/time, lat, lon, base, hour, day_name, is_weekend, borough.
Boroughs: Manhattan, Brooklyn, Queens, Bronx, Staten Island.

When answering:
1. Call the relevant tool to get real numbers — never guess.
2. Interpret the result in 2-3 sentences.
3. Highlight the single most interesting finding."""

if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Suggestion buttons (shown only on fresh chat) ────────────────────────────
SUGGESTIONS = [
    "What's the peak pickup hour?",
    "Compare weekday vs weekend demand",
    "Which borough has the most pickups?",
    "Show hourly breakdown for Manhattan",
    "Are there any anomalous hours?",
    "Show the full demand heatmap",
]

pending = None

if not st.session_state.messages:
    st.markdown("**Try asking:**")
    cols = st.columns(3)
    for i, s in enumerate(SUGGESTIONS):
        if cols[i % 3].button(s, key=f"sug_{i}", use_container_width=True):
            pending = s

# ── Render chat history ───────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] not in ("user", "assistant"):
        continue
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("figure"):
            st.plotly_chart(msg["figure"], use_container_width=True)

# ── New input ─────────────────────────────────────────────────────────────────
chat_input = st.chat_input("Ask about the data...")
prompt = chat_input or pending

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        answer = ""
        fig = None
        try:
            client, model = _get_client()

            # Build clean API messages (no Python objects)
            api_messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
            for m in st.session_state.messages:
                if m["role"] in ("user", "assistant"):
                    api_messages.append({"role": m["role"], "content": m["content"]})

            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model=model,
                    messages=api_messages,
                    tools=TOOLS,
                    tool_choice="auto",
                )

            msg_obj = response.choices[0].message

            if msg_obj.tool_calls:
                tc = msg_obj.tool_calls[0]
                tool_name = tc.function.name
                tool_args = json.loads(tc.function.arguments or "{}")

                with st.expander(f"Tool: `{tool_name}({tool_args})`", expanded=False):
                    st.caption("Running analysis…")

                tool_result, fig = _run_tool(tool_name, tool_args)

                # Second call: model interprets tool output
                api_messages.append({
                    "role": "assistant",
                    "content": msg_obj.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                    ],
                })
                api_messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": tool_result,
                })

                with st.spinner("Interpreting results..."):
                    final = client.chat.completions.create(
                        model=model,
                        messages=api_messages,
                    )
                answer = final.choices[0].message.content or ""
            else:
                answer = msg_obj.content or ""

            st.write(answer)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

        except APIConnectionError:
            answer = (
                "Cannot reach the LLM. If running locally, start Ollama with `ollama serve`. "
                "For cloud inference, set the `GROQ_API_KEY` environment variable."
            )
            st.error(answer)
        except Exception as e:
            answer = f"Error: {e}"
            st.error(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "figure": fig,
    })
