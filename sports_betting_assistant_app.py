
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
# --- Sample Data ---
sample_data = pd.DataFrame({
    "Sport": ["NFL", "NBA", "MLB", "WNBA", "NFL", "NBA"],
    "Matchup": ["Chiefs vs Bills", "Lakers vs Celtics", "Yankees vs Astros", "Aces vs Liberty", "Eagles vs 49ers", "Bucks vs Heat"],
    "Pick": ["Chiefs -3.5", "Lakers ML", "Astros Over 7.5", "Aces -4.0", "Eagles +2.5", "Heat +5.5"],
    "Confidence": [0.78, 0.65, 0.72, 0.81, 0.61, 0.69]
})

# --- Filtered View ---
filtered_data = sample_data[sample_data["Sport"] == sport]

st.markdown("### 🔍 Filtered AI Picks")
st.dataframe(filtered_data, use_container_width=True)
