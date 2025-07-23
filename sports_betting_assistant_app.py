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

        # ========== FAKE TEAM STATS (TO BE REPLACED) ==========
        st.subheader("📊 Mock Team Stats (Coming Soon)")
        fake_stats = pd.DataFrame({
            "Team": [random_row["Home Team"], random_row["Away Team"]],
            "Win %": [round(random.uniform(0.4, 0.75), 2) for _ in range(2)],
            "Avg PPG": [random.randint(20, 120) for _ in range(2)],
            "Last 5 Record": [f"{random.randint(2, 5)}-{random.randint(0, 3)}" for _ in range(2)]
        })
        st.dataframe(fake_stats)
    else:
        st.info("No matchups match your filters.")
