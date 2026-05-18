import os
import json
import time

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from openai import OpenAI, APIConnectionError

from data import get_data
from pipeline.aggregate import (
    hourly_counts,
    borough_counts,
    day_hour_heatmap,
    weekend_vs_weekday,
    anomaly_hours,
    peak_hour,
    peak_borough,
)

st.title("AI Analyst")
st.caption("Ask questions about NYC Uber demand in plain English")

with st.spinner("Loading data..."):
    data = get_data()


# ── LLM client — provider-agnostic ───────────────────────────────────────────
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


# ── Tool definitions ──────────────────────────────────────────────────────────
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
            template="dashboard",
        )
        fig.update_layout(coloraxis_showscale=False)
        return result.to_json(orient="records"), fig

    if name == "get_borough_breakdown":
        result = borough_counts(data)
        fig = px.bar(
            result[result["borough"] != "Other"],
            x="borough", y="pickups",
            color="pickups", color_continuous_scale="Blues",
            title="Pickups by Borough",
            labels={"borough": "", "pickups": "Pickups"},
            template="dashboard",
        )
        fig.update_layout(coloraxis_showscale=False)
        return result.to_json(orient="records"), fig

    if name == "get_day_hour_heatmap":
        result = day_hour_heatmap(data)
        fig = go.Figure(
            go.Heatmap(
                z=result.values,
                x=[f"{h:02d}:00" for h in result.columns],
                y=result.index.tolist(),
                colorscale="Blues",
                hovertemplate="Hour: %{x}<br>Day: %{y}<br>Pickups: %{z:,}<extra></extra>",
            )
        )
        fig.update_layout(title="Demand Heatmap — Hour x Day of Week", template="dashboard")
        return result.to_json(), fig

    if name == "get_weekend_vs_weekday":
        result = weekend_vs_weekday(data)
        fig = px.line(
            result,
            x="hour", y="pickups", color="period",
            title="Weekday vs Weekend Demand",
            labels={"hour": "Hour", "pickups": "Pickups", "period": ""},
            template="dashboard",
        )
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


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Configuration")
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
Or set `GROQ_API_KEY` for cloud inference.
            """
        )
    st.divider()
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a concise data analyst for NYC Uber Pickups (September 2014).
Dataset: ~1M pickup records. Fields: date/time, lat, lon, base, hour, day_name, is_weekend, borough.
Boroughs: Manhattan, Brooklyn, Queens, Bronx, Staten Island.

When answering:
1. Call the relevant tool to get real numbers — never guess.
2. Interpret the result in 2-3 sentences.
3. Highlight the single most interesting finding."""

if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Suggestion buttons ────────────────────────────────────────────────────────
SUGGESTIONS = [
    "What is the peak pickup hour?",
    "Compare weekday vs weekend demand",
    "Which borough has the most pickups?",
    "Show hourly breakdown for Manhattan",
    "Are there any anomalous hours?",
    "Show the full demand heatmap",
]

pending = None

if not st.session_state.messages:
    st.markdown("**Suggested questions**")
    cols = st.columns(3)
    for i, s in enumerate(SUGGESTIONS):
        if cols[i % 3].button(s, key=f"sug_{i}", use_container_width=True):
            pending = s

# ── Chat history ──────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] not in ("user", "assistant"):
        continue
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("figure"):
            st.plotly_chart(msg["figure"], use_container_width=True)
        if msg.get("usage"):
            u = msg["usage"]
            with st.expander("Usage", expanded=False):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Prompt tokens", f"{u['prompt_tokens']:,}")
                c2.metric("Completion tokens", f"{u['completion_tokens']:,}")
                c3.metric("Total tokens", f"{u['total_tokens']:,}")
                c4.metric("Latency", f"{u['latency_s']:.2f}s")

# ── New input ─────────────────────────────────────────────────────────────────
prompt = st.chat_input("Ask about the data...") or pending

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        answer = ""
        fig = None
        usage: dict | None = None

        try:
            client, model = _get_client()

            api_messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
            for m in st.session_state.messages:
                if m["role"] in ("user", "assistant"):
                    api_messages.append({"role": m["role"], "content": m["content"]})

            t0 = time.perf_counter()

            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model=model,
                    messages=api_messages,
                    tools=TOOLS,
                    tool_choice="auto",
                )

            msg_obj = response.choices[0].message
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens

            if msg_obj.tool_calls:
                tc = msg_obj.tool_calls[0]
                tool_name = tc.function.name
                tool_args = json.loads(tc.function.arguments or "{}")

                with st.expander(f"Tool call: {tool_name}", expanded=False):
                    st.json(tool_args)

                tool_result, fig = _run_tool(tool_name, tool_args)

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
                prompt_tokens += final.usage.prompt_tokens
                completion_tokens += final.usage.completion_tokens
            else:
                answer = msg_obj.content or ""

            latency = time.perf_counter() - t0
            usage = {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
                "latency_s": latency,
            }

            st.write(answer)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

            with st.expander("Usage", expanded=False):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Prompt tokens", f"{usage['prompt_tokens']:,}")
                c2.metric("Completion tokens", f"{usage['completion_tokens']:,}")
                c3.metric("Total tokens", f"{usage['total_tokens']:,}")
                c4.metric("Latency", f"{usage['latency_s']:.2f}s")

        except APIConnectionError:
            answer = (
                "Cannot reach the LLM. Start Ollama with `ollama serve`, "
                "or set the GROQ_API_KEY environment variable."
            )
            st.error(answer)
        except Exception as e:
            answer = f"Error: {e}"
            st.error(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "figure": fig,
        "usage": usage,
    })
