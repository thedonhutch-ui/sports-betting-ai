import requests
import os
@st.cache_data(show_spinner=False)
def fetch_odds_data(sport_key="americanfootball_nfl"):
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
    params = {
        "regions": "us",
        "markets": "h2h,spreads,totals",
        "apiKey": ODDS_API_KEY
    }
    response = requests.get(url, params=params)

    if response.status_code != 200:
        st.error("Failed to fetch odds data.")
        return pd.DataFrame()

    games = response.json()
    data = []
    for game in games:
        matchup = f"{game['home_team']} vs {game['away_team']}"
        for bookmaker in game.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                if market["key"] == "h2h":
                    outcomes = market["outcomes"]
                    row = {
                        "Matchup": matchup,
                        "Bookmaker": bookmaker["title"],
                        "Moneyline_Home": outcomes[0]["price"],
                        "Moneyline_Away": outcomes[1]["price"],
                        "Commence Time": game["commence_time"]
                    }
                    data.append(row)
    return pd.DataFrame(data)
# Replace with your actual OddsAPI key
ODDS_API_KEY = e1a0d3aca26d43993c899a17c319a9b1
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


# Merge with filtered picks
merged = pd.merge(filtered_data, odds_data, on="Matchup", how="left")

st.markdown("### 💵 Picks With Simulated Odds")
st.dataframe(merged, use_container_width=True)
# Sidebar pick-type enhanced
pick_type = st.sidebar.selectbox("Pick Type", ["All", "Moneyline", "Spread", "Over/Under"])

if pick_type != "All":
    merged = merged[merged["Pick"].str.contains(pick_type.split("/")[0], case=False)]

st.markdown(f"### Filtered Picks: {pick_type}")
st.dataframe(merged, use_container_width=True)
st.markdown("### 🔴 Live Odds Feed")

sport_key_map = {
    "NFL": "americanfootball_nfl",
    "NBA": "basketball_nba",
    "MLB": "baseball_mlb",
    "WNBA": "basketball_wnba"
}

selected_key = sport_key_map[sport]
odds_df = fetch_odds_data(selected_key)

if not odds_df.empty:
    st.dataframe(odds_df, use_container_width=True)
else:
    st.info("No live odds available or API call limit reached.")
