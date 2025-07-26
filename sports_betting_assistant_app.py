import streamlit as st
import pandas as pd
import requests
import random
import altair as alt

ODDS_API_KEY = "e1a0d3aca26d43993c899a17c319a9b1"
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/10qHJPF7tD7eSl8sRcTDrnzpL60a1Sk8rBuv5J19z1JI/export?format=csv&gid="

SPORTS = {
    "NFL":   {"key": "americanfootball_nfl",   "gid": "0"},
    "WNBA":  {"key": "basketball_wnba",        "gid": "1354086104"},
    "NBA":   {"key": "basketball_nba",         "gid": "1494548643"},
    "NCAAF": {"key": "americanfootball_ncaaf", "gid": "1807990318"},
    "NCAAB": {"key": "basketball_ncaab",       "gid": "783040797"},
    "MLB":   {"key": "baseball_mlb",           "gid": "1111623914"},
}


st.set_page_config(page_title="Sports Betting Assistant", layout="wide")
st.title("📊 Sports Betting Assistant")

sport = st.selectbox("Choose a sport", list(SPORTS.keys()))
sport_key = SPORTS[sport]["key"]
gid = SPORTS[sport]["gid"]

@st.cache_data(ttl=600)
def fetch_odds(sport_key):
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
    params = {"regions": "us", "markets": "h2h", "apiKey": ODDS_API_KEY}
    r = requests.get(url, params=params)
    if r.status_code != 200:
        return pd.DataFrame()
    games = r.json()
    rows = []
    for g in games:
        matchup = f"{g['home_team']} vs {g['away_team']}"
        for book in g.get("bookmakers", []):
            for market in book.get("markets", []):
                if market["key"] == "h2h":
                    outcomes = market["outcomes"]
                    if len(outcomes) < 2:
                        continue
                    rows.append({
                        "Matchup": matchup,
                        "Bookmaker": book["title"],
                        "Moneyline_Home": outcomes[0]["price"],
                        "Moneyline_Away": outcomes[1]["price"],
                        "Commence Time": g["commence_time"],
                        "Home Team": g["home_team"],
                        "Away Team": g["away_team"],
                    })
    return pd.DataFrame(rows)

@st.cache_data(ttl=600)
def fetch_team_stats(gid):
    try:
        df = pd.read_csv(f"{GOOGLE_SHEET_URL}{gid}")
        return df
    except Exception as e:
        return pd.DataFrame()

odds_df = fetch_odds(sport_key)
stats_df = fetch_team_stats(gid)

if odds_df.empty:
    st.warning("No odds data available yet.")
else:
    with st.sidebar:
        st.header("Filters")
        search = st.text_input("Search Team")
        min_odds, max_odds = st.slider("Moneyline Range", -1000, 1000, (-500, 500))
        pick_count = st.slider("Number of Picks", 1, 10, 3)
        conf_range = st.slider("Confidence Range (%)", 50, 100, (60, 100))

    df = odds_df.copy()
    if search:
        df = df[df["Matchup"].str.contains(search, case=False)]
    df = df[
        (df["Moneyline_Home"].between(min_odds, max_odds)) &
        (df["Moneyline_Away"].between(min_odds, max_odds))
    ]

    st.subheader("📋 Filtered Matchups")
    st.dataframe(df)

    if not df.empty:
        st.subheader("🔥 Suggested Picks")
        picks = []
        for _, row in df.sample(min(len(df), pick_count)).iterrows():
            side = random.choice(["Home", "Away"])
            team = row["Home Team"] if side == "Home" else row["Away Team"]
            odds = row["Moneyline_Home"] if side == "Home" else row["Moneyline_Away"]
            confidence = round(random.uniform(*conf_range), 2)
            picks.append({
                "Pick": team,
                "Side": side,
                "Odds": odds,
                "Confidence": confidence,
                "Matchup": row["Matchup"],
                "Bookmaker": row["Bookmaker"],
                "Commence Time": row["Commence Time"]
            })

        picks_df = pd.DataFrame(picks).sort_values("Confidence", ascending=False)
        st.dataframe(picks_df)

        st.subheader("📈 Team Stat Comparison")
        if stats_df.empty:
            st.error("Stats failed to load from Google Sheets.")
        else:
            selected_teams = picks_df["Pick"].unique()
            team_stats = stats_df[stats_df["Team"].isin(selected_teams)]
            if not team_stats.empty:
                st.dataframe(team_stats)

                melted = team_stats.melt(id_vars="Team", var_name="Stat", value_name="Value")
                chart = alt.Chart(melted).mark_bar().encode(
                    x=alt.X('Stat:N', title="Stat"),
                    y=alt.Y('Value:Q'),
                    color='Team:N',
                    column='Team:N'
                ).properties(width=150)
                st.altair_chart(chart, use_container_width=True)

                st.download_button(
                    "📥 Download Picks + Stats",
                    data=picks_df.merge(team_stats, left_on="Pick", right_on="Team").to_csv(index=False),
                    file_name="value_picks_with_stats.csv",
                    mime="text/csv"
                )
            else:
                st.info("No matching stats found for selected teams.")
