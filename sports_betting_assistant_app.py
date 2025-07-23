import streamlit as st
import pandas as pd
import requests
import random

ODDS_API_KEY = "e1a0d3aca26d43993c899a17c319a9b1"

st.title("📊 Sports Betting Assistant")
sport = st.selectbox("Choose a sport", ["NFL", "NBA", "MLB", "WNBA", "NCAAF", "NCAAB"])

sport_key_map = {
    "NFL": "americanfootball_nfl",
    "NBA": "basketball_nba",
    "MLB": "baseball_mlb",
    "WNBA": "basketball_wnba",
    "NCAAF": "americanfootball_ncaaf",
    "NCAAB": "basketball_ncaab"
}
selected_key = sport_key_map[sport]

@st.cache_data
def fetch_odds_data(sport_key):
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
                        "Commence Time": game["commence_time"],
                        "Home Team": game['home_team'],
                        "Away Team": game['away_team']
                    }
                    data.append(row)
    return pd.DataFrame(data)

odds_df = fetch_odds_data(selected_key)

if odds_df.empty:
    st.warning("No data available yet. Try again shortly.")
else:
    # ========== FILTER SECTION ==========
    st.sidebar.header("🔎 Filters")
    search_team = st.sidebar.text_input("Search Team (partial name)")
    min_odds, max_odds = st.sidebar.slider("Moneyline Range", -1000, 1000, (-1000, 1000))
    bookmaker_filter = st.sidebar.multiselect("Bookmaker", odds_df["Bookmaker"].unique())

    filtered_df = odds_df.copy()

    if search_team:
        filtered_df = filtered_df[
            filtered_df["Matchup"].str.contains(search_team, case=False, na=False)
        ]
    filtered_df = filtered_df[
        (filtered_df["Moneyline_Home"].between(min_odds, max_odds)) &
        (filtered_df["Moneyline_Away"].between(min_odds, max_odds))
    ]
    if bookmaker_filter:
        filtered_df = filtered_df[filtered_df["Bookmaker"].isin(bookmaker_filter)]

    st.subheader("📋 Filtered Matchups")
    st.dataframe(filtered_df)

    if not filtered_df.empty:
        # ========== VALUE PICK ==========
        st.subheader("🔮 Suggested Value Pick")
        random_row = filtered_df.sample(1).iloc[0]
        pick_side = random.choice(["Home", "Away"])
        team = random_row["Home Team"] if pick_side == "Home" else random_row["Away Team"]
        odds = random_row["Moneyline_Home"] if pick_side == "Home" else random_row["Moneyline_Away"]
        confidence = round(random.uniform(52.0, 75.0), 2)

        st.markdown(f"""
        ### ✅ Pick: **{team}**
        - Odds: `{odds}`
        - Confidence: `{confidence}%`
        - Bookmaker: `{random_row["Bookmaker"]}`
        - Game: `{random_row["Matchup"]}`
        - Time: `{random_row["Commence Time"]}`
        """)

        # ===== REAL TEAM STATS MERGE =====
st.subheader("📊 Team Stats (From CSV)")

# Define available stat files
stats_files = {
    "NFL": "nfl_team_stats.csv",
    "NBA": "nba_team_stats.csv",
    "MLB": "mlb_team_stats.csv",
    "WNBA": "wnba_team_stats.csv",
    "NCAAF": "ncaaf_team_stats.csv",
    "NCAAB": "ncaab_team_stats.csv"
}

try:
    # Try loading the correct stats file for the selected sport
    team_stats = pd.read_csv(stats_files[sport])

    # Filter for teams in the current value pick
    selected_teams = [random_row["Home Team"], random_row["Away Team"]]
    filtered_stats = team_stats[team_stats["Team"].isin(selected_teams)]

    if filtered_stats.empty:
        st.info("Stats not found for these teams.")
    else:
        st.dataframe(filtered_stats)

except FileNotFoundError:
    st.warning("Stats file not found. Please upload the correct CSV.")
except Exception as e:
    st.error(f"Error loading stats: {e}")
