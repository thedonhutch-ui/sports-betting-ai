import streamlit as st
import pandas as pd
import requests
import random

# ===== SET YOUR ODDSAPI KEY HERE =====
ODDS_API_KEY = "e1a0d3aca26d43993c899a17c319a9b1"

# ===== SPORT SELECTION =====
st.title("📊 Sports Betting Assistant")
sport = st.selectbox("Choose a sport", ["NFL", "NBA", "MLB", "WNBA", "NCAAF", "NCAAB"])

# ===== SPORT KEY MAP (FIXED COMMAS AND SPELLING) =====
sport_key_map = {
    "NFL": "americanfootball_nfl",
    "NBA": "basketball_nba",
    "MLB": "baseball_mlb",
    "WNBA": "basketball_wnba",
    "NCAAF": "americanfootball_ncaaf",
    "NCAAB": "basketball_ncaab"
}
selected_key = sport_key_map[sport]

# ===== FETCH ODDS FUNCTION (FIXED CACHE DECORATOR) =====
@st.cache_data
def fetch_odds_data(sport_key="americanfootball_nfl"):
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
    params = {
        "regions": "us",
        "markets": "h2h",
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

# ===== LOAD ODDS DATA =====
odds_df = fetch_odds_data(selected_key)

if odds_df.empty:
    st.warning("No data available yet. Try again shortly.")
else:
    st.subheader("Available Matchups and Odds")
    st.dataframe(odds_df)

    # ===== MOCK AI VALUE PICK (for now) =====
    st.subheader("🔮 Today's Value Pick")

    random_row = odds_df.sample(1).iloc[0]
    pick = random.choice(["Home", "Away"])
    team = random_row["Matchup"].split(" vs ")[0] if pick == "Home" else random_row["Matchup"].split(" vs ")[1]
    odds = random_row["Moneyline_Home"] if pick == "Home" else random_row["Moneyline_Away"]

    st.markdown(f"""
    ### ✅ Pick: **{team}**
    - Odds: `{odds}`
    - Bookmaker: `{random_row["Bookmaker"]}`
    - Game: `{random_row["Matchup"]}`
    - Time: `{random_row["Commence Time"]}`
    """)

    st.info("Advanced filters and stat-based predictions coming next!")
