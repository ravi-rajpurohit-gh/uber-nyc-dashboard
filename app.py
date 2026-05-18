import streamlit as st
from style import apply_global_css

st.set_page_config(
    page_title="NYC Uber Pickups",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_css()

with st.sidebar:
    st.markdown("**NYC Uber Pickups**")
    st.caption("September 2014 · 1M records")
    st.divider()

pages = [
    st.Page("pages/home.py", title="Home", default=True),
    st.Page("pages/1_Map_Explorer.py", title="Map Explorer"),
    st.Page("pages/2_AI_Analyst.py", title="AI Analyst"),
]

pg = st.navigation(pages)
pg.run()
