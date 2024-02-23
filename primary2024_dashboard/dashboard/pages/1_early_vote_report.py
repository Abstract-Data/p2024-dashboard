import streamlit as st
from primary2024_dashboard.process import EarlyVoteData

st.set_page_config(
    layout="wide",
    page_title="20204 TX GOP Primary: Early Vote Report",
    page_icon=":bar_chart:"
)

st.title("Early Vote Report")