
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sports Betting Assistant", layout="wide")

st.title("🎯 Sports Betting Assistant")
st.sidebar.header("🧪 Filters & Controls")

# Sidebar filters (placeholders for now)
sport = st.sidebar.selectbox("Choose a Sport", ["NFL", "NBA", "MLB", "WNBA"])
pick_type = st.sidebar.selectbox("Pick Type", ["AI Picks", "Over/Under", "Underdog", "Favorites"])

# Main sections
st.markdown("### 🧠 AI-Generated Picks (Demo)")
st.info("This section will show AI picks once data is connected.")

st.markdown("### 📊 Team & Matchup Stats (Coming Soon)")
st.warning("Team stats and game info will appear here.")

st.markdown("### 💰 Live Betting Odds (Add API next)")
st.error("No odds API connected yet. Add OddsAPI or similar.")
