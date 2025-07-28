import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Sports Betting AI Assistant", layout="wide")
st.title("🏈 Sports Betting AI Assistant")

# --- API Setup ---
SPORTSDATAIO_API_KEY = "7fb7250dacd54cb997b9fbfceb011044"
MLB_BASE_URL = "https://api.sportsdata.io/v4/mlb/stats/json"
HEADERS = {"Ocp-Apim-Subscription-Key": SPORTSDATAIO_API_KEY}

# --- Fetch MLB Team Stats ---
@st.cache_data(ttl=3600)
def get_mlb_team_stats():
    url = f"{MLB_BASE_URL}/TeamSeasonStats/2024"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error("Failed to fetch MLB stats.")
        return pd.DataFrame()

# --- Clean and Prepare Team Stats ---
def clean_team_stats(df):
    df.columns = df.columns.str.strip().str.lower()
    if "name" in df.columns:
        df["team"] = df["name"]  # Use "Name" column as team name
    df["team_clean"] = df["team"].str.lower().str.replace(r"\W+", "", regex=True)
    return df

# --- Sample Picks ---
def get_sample_picks():
    return pd.DataFrame({
        "Matchup": ["Yankees vs Red Sox", "Dodgers vs Giants"],
        "Pick": ["Yankees", "Giants"],
        "Confidence": [0.75, 0.62]
    })

# --- Clean Pick Names ---
def clean_name(name):
    return name.lower().strip().replace(" ", "").replace("-", "")

# --- Load and Process Data ---
with st.spinner("Loading data..."):
    raw_stats_df = get_mlb_team_stats()
    stats_df = clean_team_stats(raw_stats_df)

    picks_df = get_sample_picks()
    picks_df["pick_clean"] = picks_df["Pick"].apply(clean_name)

# --- Display Matchups & Picks ---
st.subheader("🎯 Suggested Picks")
st.dataframe(picks_df)

# --- Stat Comparison ---
st.subheader("📊 Team Stat Comparison")
selected_teams = picks_df["pick_clean"].tolist()
filtered_stats = stats_df[stats_df["team_clean"].isin(selected_teams)]

if not filtered_stats.empty:
    st.dataframe(filtered_stats[["team", "wins", "losses", "runs", "earnedrunaverage"]], use_container_width=True)
else:
    st.warning("No matching stats found for selected teams")
