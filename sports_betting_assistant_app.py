import streamlit as st
import pandas as pd
import requests
import datetime

# ------------------------------
# API Setup
# ------------------------------
SPORTSDATAIO_API_KEY = "7fb7250dacd54cb997b9fbfceb011044"
BASE_URL = "https://api.sportsdata.io/v4/mlb/stats/json"
HEADERS = {"Ocp-Apim-Subscription-Key": SPORTSDATAIO_API_KEY}

# ------------------------------
# Load MLB stats from SportsDataIO API
# ------------------------------
@st.cache_data(ttl=3600)
def load_mlb_team_stats():
    url = f"{BASE_URL}/TeamSeasonStats/2024"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error(f"Failed to fetch MLB team stats: {response.status_code}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_mlb_standings():
    url = f"{BASE_URL}/Standings/2024"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_mlb_scores():
    today = datetime.date.today()
    url = f"{BASE_URL}/GamesByDate/{today}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_mlb_odds():
    url = "https://api.sportsdata.io/v4/mlb/odds/json/GameOddsByDate/2024-JUL-23"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        return pd.DataFrame()

# ------------------------------
# Google Sheets URLs (for other sports)
# ------------------------------
sheet_urls = {
    "NFL": "https://docs.google.com/spreadsheets/d/10qHJPF7tD7eSl8sRcTDrnzpL60a1Sk8rBuv5J19z1JI/export?format=csv&gid=0",
    "NBA": "https://docs.google.com/spreadsheets/d/10qHJPF7tD7eSl8sRcTDrnzpL60a1Sk8rBuv5J19z1JI/export?format=csv&gid=1494548643",
    "WNBA": "https://docs.google.com/spreadsheets/d/10qHJPF7tD7eSl8sRcTDrnzpL60a1Sk8rBuv5J19z1JI/export?format=csv&gid=1354086104",
    "NCAAF": "https://docs.google.com/spreadsheets/d/10qHJPF7tD7eSl8sRcTDrnzpL60a1Sk8rBuv5J19z1JI/export?format=csv&gid=1807990318",
    "NCAAB": "https://docs.google.com/spreadsheets/d/10qHJPF7tD7eSl8sRcTDrnzpL60a1Sk8rBuv5J19z1JI/export?format=csv&gid=783040797"
}

@st.cache_data(ttl=600)
def load_stats_from_sheets(sport):
    url = sheet_urls.get(sport)
    if not url:
        return pd.DataFrame()
    try:
        return pd.read_csv(url)
    except Exception as e:
        st.error(f"Failed to load stats for {sport}: {e}")
        return pd.DataFrame()

# ------------------------------
# Main App
# ------------------------------
st.title("📊 Sports Betting Assistant")
sport = st.selectbox("Select a sport:", ["NFL", "NBA", "WNBA", "NCAAF", "NCAAB", "MLB"])

if sport == "MLB":
    st.header("⚾ Live MLB Stats (SportsDataIO)")
    mlb_stats = load_mlb_team_stats()
    if not mlb_stats.empty:
        st.dataframe(mlb_stats[["Team", "Wins", "Losses", "Runs", "Hits", "HomeRuns"]])

    st.subheader("📊 Standings")
    standings = load_mlb_standings()
    if not standings.empty:
        st.dataframe(standings[["Name", "Wins", "Losses", "Percentage"]])

    st.subheader("📅 Today’s Games")
    games = load_mlb_scores()
    if not games.empty:
        st.dataframe(games[["HomeTeam", "AwayTeam", "Status", "DateTime"]])

    st.subheader("💸 Game Odds")
    odds = load_mlb_odds()
    if not odds.empty:
        st.dataframe(odds[["HomeTeam", "AwayTeam", "PregameOdds"]])

else:
    stats_df = load_stats_from_sheets(sport)
    if not stats_df.empty:
        st.subheader(f"📈 {sport} Stats from Google Sheets")
        st.dataframe(stats_df)
    else:
        st.warning(f"No stats available for {sport}.")




