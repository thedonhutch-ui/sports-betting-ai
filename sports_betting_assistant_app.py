import streamlit as st
import pandas as pd
import requests
import numpy as np

# === CONFIG ===
SPORTSDATAIO_API_KEY = "7fb7250dacd54cb997b9fbfceb011044"

# === CLEANING UTIL ===
def clean_name(name):
    if pd.isna(name):
        return ""
    return str(name).lower().strip().replace(" ", "").replace("-", "").replace(".", "")

# === LOAD LIVE MLB TEAM STATS ===
def load_mlb_team_stats():
    url = f"https://api.sportsdata.io/v3/mlb/stats/json/TeamSeasonStats/2024"
    headers = {"Ocp-Apim-Subscription-Key": SPORTSDATAIO_API_KEY}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        st.error(f"❌ Failed to fetch MLB stats: {response.status_code} - {response.reason}")
        return pd.DataFrame()

    df = pd.DataFrame(response.json())
    return clean_team_stats(df)

# === CLEAN THE TEAM STATS ===
def clean_team_stats(df):
    if df.empty:
        st.warning("⚠️ No stats returned from the API.")
        return df

    df["Team_clean"] = df["Name"].apply(clean_name)  # 'Name' is team name in API
    return df

# === MOCK PICKS === (replace with actual pick logic)
def get_mock_picks():
    return pd.DataFrame({
        "Matchup": ["Yankees vs Red Sox", "Dodgers vs Giants"],
        "Pick": ["Yankees", "Giants"],
        "Confidence": [0.78, 0.65]
    })

# === MAIN APP ===
st.title("⚾ MLB Betting Assistant (Live Stats)")

# Load picks
picks_df = get_mock_picks()
picks_df["Pick_clean"] = picks_df["Pick"].apply(clean_name)

# Load MLB team stats
stats_df = load_mlb_team_stats()

# Show suggested picks
st.subheader("💡 Suggested Picks")
st.dataframe(picks_df)

# Team stat comparison
st.subheader("📈 Team Stat Comparison")
comparison_data = []

if not stats_df.empty:
    for _, row in picks_df.iterrows():
        team = row["Pick_clean"]
        team_stats = stats_df[stats_df["Team_clean"] == team]

        if not team_stats.empty:
            comparison_data.append(team_stats)
        else:
            st.warning(f"⚠️ No stats found for: {row['Pick']}")

    if comparison_data:
        full_comparison_df = pd.concat(comparison_data)
        st.dataframe(full_comparison_df)
    else:
        st.info("No matching team stats to show.")
else:
    st.stop()


