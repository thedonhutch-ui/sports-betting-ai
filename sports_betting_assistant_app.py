import streamlit as st
import requests
import pandas as pd

# ✨ SportsDataIO MLB API settings
API_KEY = "7fb7250dacd54cb997b9fbfceb011044"
BASE_URL = "https://api.sportsdata.io/v4/mlb/stats/json"
HEADERS = {"Ocp-Apim-Subscription-Key": API_KEY}

st.title("🎾 MLB Live Team Stats (Powered by SportsDataIO)")

# Step 1: Fetch all 2024 team season stats (free endpoint)
st.write("Fetching 2024 MLB Team Stats...")
try:
    response = requests.get(f"{BASE_URL}/TeamSeasonStats/2024", headers=HEADERS)
    response.raise_for_status()
    data = response.json()
except Exception as e:
    st.error(f"Failed to fetch MLB stats: {e}")
    st.stop()

# Step 2: Convert to DataFrame
df = pd.DataFrame(data)

if df.empty:
    st.warning("No stats returned from the API.")
    st.stop()

# Step 3: Clean and filter stats
# Select key stat columns to display
numeric_columns = df.select_dtypes(include='number').columns.tolist()

# Optional: Filter down to only relevant stats
selected_columns = [
    "Name", "Wins", "Losses", "Runs", "HomeRuns", "Hits", "Walks", "Strikeouts",
    "EarnedRunAverage", "BattingAverage", "OnBasePercentage"
]
filtered_columns = [col for col in selected_columns if col in df.columns]

# Step 4: Add dropdown to select team
team_names = df["Name"].sort_values().tolist()
selected_team = st.selectbox("Select a team to view stats:", team_names)

# Step 5: Display team stats
team_stats = df[df["Name"] == selected_team][filtered_columns].T
team_stats.columns = [selected_team]

st.subheader(f"📊 Stats for {selected_team}")
st.dataframe(team_stats, use_container_width=True)

# Optional: Full table view
with st.expander("📊 View Full Stats Table"):
    st.dataframe(df[filtered_columns].sort_values("Wins", ascending=False), use_container_width=True)


