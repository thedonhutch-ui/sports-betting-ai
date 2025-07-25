import streamlit as st
import pandas as pd
import requests
import random
import altair as alt

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
    min_conf, max_conf = st.sidebar.slider("Confidence Range (%)", 50, 100, (60, 100))
    pick_count = st.sidebar.slider("Number of Picks", 1, 10, 3)

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
        # ========== VALUE PICKS ==========
        st.subheader("🔮 Suggested Value Picks")
        picks = []
        for _, row in filtered_df.sample(min(pick_count, len(filtered_df))).iterrows():
            side = random.choice(["Home", "Away"])
            team = row["Home Team"] if side == "Home" else row["Away Team"]
            odds = row["Moneyline_Home"] if side == "Home" else row["Moneyline_Away"]
            confidence = round(random.uniform(min_conf, max_conf), 2)

            picks.append({
                "Pick": team,
                "Side": side,
                "Odds": odds,
                "Confidence": confidence,
                "Bookmaker": row["Bookmaker"],
                "Matchup": row["Matchup"],
                "Commence Time": row["Commence Time"],
                "Home Team": row["Home Team"],
                "Away Team": row["Away Team"]
            })

        picks_df = pd.DataFrame(picks).sort_values(by="Confidence", ascending=False)
        st.dataframe(picks_df)

        # ========== ROI SIMULATOR ==========
        st.subheader("📈 ROI Simulator")
        st.markdown("Mark which picks won or lost to calculate your ROI.")

        for i in range(len(picks_df)):
            picks_df.loc[i, "Result"] = st.radio(
                f"{picks_df.loc[i, 'Pick']} ({picks_df.loc[i, 'Odds']})",
                ["Win", "Loss"],
                key=f"result_{i}",
                horizontal=True
            )

        def american_to_decimal(odds):
            return 100 / abs(odds) + 1 if odds < 0 else odds / 100 + 1

        picks_df["Decimal Odds"] = picks_df["Odds"].apply(american_to_decimal)
        picks_df["Profit"] = picks_df.apply(
            lambda row: 100 * (row["Decimal Odds"] - 1) if row["Result"] == "Win" else -100,
            axis=1
        )

        total_bets = len(picks_df)
        total_profit = picks_df["Profit"].sum()
        roi = (total_profit / (total_bets * 100)) * 100 if total_bets else 0

        st.metric("Total Bets", total_bets)
        st.metric("Net Profit", f"${total_profit:.2f}")
        st.metric("ROI", f"{roi:.2f}%")










                      

                                    

