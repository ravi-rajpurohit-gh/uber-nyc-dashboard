import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from data import get_data
from pipeline.aggregate import (
    hourly_counts,
    borough_counts,
    day_hour_heatmap,
    anomaly_hours,
    peak_hour,
    peak_borough,
)

st.title("NYC Uber Pickups")
st.caption("September 2014 · ingest → validate → enrich → aggregate")

with st.spinner("Loading data..."):
    data = get_data()

# ── KPI row ───────────────────────────────────────────────────────────────────
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
        color_discrete_map={True: "#B91C1C", False: "#1D4ED8"},
        labels={"hour": "Hour of Day", "pickups": "Pickups", "anomaly": "Anomaly"},
        hover_data={"z_score": ":.2f"},
        template="dashboard",
    )
    fig.update_layout(showlegend=True, height=300)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Highlighted bars are statistical anomalies (|z-score| > 1.8)")

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
        template="dashboard",
    )
    fig.update_layout(coloraxis_showscale=False, height=300)
    st.plotly_chart(fig, use_container_width=True)

# ── Row 2: heatmap ────────────────────────────────────────────────────────────
st.subheader("Demand Heatmap — Hour x Day of Week")
dhm = day_hour_heatmap(data)
fig = go.Figure(
    go.Heatmap(
        z=dhm.values,
        x=[f"{h:02d}:00" for h in dhm.columns],
        y=dhm.index.tolist(),
        colorscale="Blues",
        hoverongaps=False,
        hovertemplate="Hour: %{x}<br>Day: %{y}<br>Pickups: %{z:,}<extra></extra>",
    )
)
fig.update_layout(template="dashboard", height=270)
st.plotly_chart(fig, use_container_width=True)
