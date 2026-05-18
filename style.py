import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio

_GRID = "#E5E7EB"
_PALETTE = ["#1D4ED8", "#7C3AED", "#059669", "#B45309", "#DC2626"]

pio.templates["dashboard"] = go.layout.Template(
    layout=go.Layout(
        font=dict(family="system-ui, -apple-system, sans-serif", size=12, color="#374151"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=_PALETTE,
        xaxis=dict(gridcolor=_GRID, linecolor=_GRID, zeroline=False),
        yaxis=dict(gridcolor=_GRID, linecolor=_GRID, zeroline=False),
        margin=dict(t=32, b=24, l=0, r=0),
        legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0),
    )
)


def apply_global_css() -> None:
    st.markdown(
        """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        [data-testid="metric-container"] {
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            padding: 1rem 1.25rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        [data-testid="stMetricValue"] {
            font-size: 1.6rem;
            font-weight: 600;
        }
        [data-testid="stSidebar"] {
            border-right: 1px solid #E5E7EB;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
