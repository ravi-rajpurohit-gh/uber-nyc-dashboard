import streamlit as st
import pydeck as pdk

from data import get_data

st.title("Map Explorer")

with st.spinner("Loading data..."):
    data = get_data()

# ── Sidebar controls ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")
    hour = st.slider("Hour of Day", 0, 23, 17)
    layer_type = st.radio("Map Layer", ["Heatmap", "Scatter"])
    boroughs = st.multiselect(
        "Boroughs",
        ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"],
        default=["Manhattan", "Brooklyn", "Queens"],
    )

filtered = data[(data["hour"] == hour) & (data["borough"].isin(boroughs))]
st.caption(f"{len(filtered):,} pickups at {hour:02d}:00 in {', '.join(boroughs)}")

# ── Deck ──────────────────────────────────────────────────────────────────────
view_state = pdk.ViewState(latitude=40.730, longitude=-73.935, zoom=10, pitch=45)

if layer_type == "Heatmap":
    layer = pdk.Layer(
        "HeatmapLayer",
        data=filtered[["lat", "lon"]],
        get_position="[lon, lat]",
        radiusPixels=50,
        opacity=0.85,
    )
else:
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered[["lat", "lon"]],
        get_position="[lon, lat]",
        get_radius=80,
        get_fill_color=[29, 78, 216, 160],
        pickable=True,
    )

st.pydeck_chart(
    pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/dark-v9",
        tooltip={"text": "{lat:.4f}, {lon:.4f}"},
    )
)
