import streamlit as st

st.set_page_config(page_title="Sports Betting Assistant", layout="wide")

st.title("🎯 Sports Betting Assistant")
st.subheader("Simple Picks + Advanced Filters (NFL, NBA, WNBA, MLB)")

st.markdown("""
This is a starter dashboard. You’ll later be able to:
- Import live odds and stats (via OddsAPI or others)
- Analyze trends and filter matchups
- View AI-generated picks and confidence scores
""")

st.info("Data will populate once APIs are connected.")
