import streamlit as st

pages = [
    st.Page("pages/home.py", title="Home", icon="🏠", default=True),
    st.Page("pages/1_Map_Explorer.py", title="Map Explorer", icon="🗺️"),
    st.Page("pages/2_AI_Analyst.py", title="AI Analyst", icon="🤖"),
]

pg = st.navigation(pages)
pg.run()
