import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from pipeline.ingest import load_raw
from pipeline.transform import enrich
from pipeline.aggregate import (
    hourly_counts,
    borough_counts,
    day_hour_heatmap,
    anomaly_hours,
    peak_hour,
    peak_borough,
)

st.set_page_config(
    page_title="NYC Uber Pickups",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("NYC Uber Pickups")
st.caption("September 2014 · ~100K rides · ingest → validate → enrich → aggregate")


@st.cache_data(show_spinner="Running data pipeline...")
def get_data():
    raw = load_raw()
    return enrich(raw)


data = get_data()

# ── KPI row ──────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Pickups", f"{len(data):,}")
k2.metric("Peak Hour", f"{peak_hour(data):02d}:00")
k3.metric("Top Borough", peak_borough(data))
k4.metric("Active Bases", str(data["base"].nunique()))

st.divider()

# ── Row 1: hourly bar + borough bar ──────────────────────────────────────────
col_l, col_r = st.columns(2)

with col_l:
    st.subheader("Pickups by Hour")
    ah = anomaly_hours(data)
    fig = px.bar(
        ah,
        x="hour",
        y="pickups",
        color="anomaly",
        color_discrete_map={True: "#FF4B4B", False: "#4B8BFF"},
        labels={"hour": "Hour of Day", "pickups": "Pickups", "anomaly": "Anomaly"},
        hover_data={"z_score": ":.2f"},
    )
    fig.update_layout(showlegend=True, margin=dict(t=10, b=0), height=300)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Red bars = statistical anomaly (|z-score| > 1.8)")

with col_r:
    st.subheader("Pickups by Borough")
    bc = borough_counts(data)
    fig = px.bar(
        bc[bc["borough"] != "Other"],
        x="borough",
        y="pickups",
        color="pickups",
        color_continuous_scale="Blues",
        labels={"borough": "", "pickups": "Pickups"},
    )
    fig.update_layout(coloraxis_showscale=False, margin=dict(t=10, b=0), height=300)
    st.plotly_chart(fig, use_container_width=True)

# ── Row 2: hour × day heatmap ─────────────────────────────────────────────────
st.subheader("Demand Heatmap: Hour × Day of Week")
dhm = day_hour_heatmap(data)
fig = go.Figure(
    go.Heatmap(
        z=dhm.values,
        x=[f"{h:02d}:00" for h in dhm.columns],
        y=dhm.index.tolist(),
        colorscale="YlOrRd",
        hoverongaps=False,
        hovertemplate="Hour: %{x}<br>Day: %{y}<br>Pickups: %{z:,}<extra></extra>",
    )
)
fig.update_layout(margin=dict(t=10, b=0), height=270)
st.plotly_chart(fig, use_container_width=True)
