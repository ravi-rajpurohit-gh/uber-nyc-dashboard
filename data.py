import streamlit as st
from pipeline.ingest import load_raw
from pipeline.transform import enrich


@st.cache_resource(show_spinner=False)
def get_data():
    """Load and enrich the dataset once; shared across all pages and sessions."""
    return enrich(load_raw())
