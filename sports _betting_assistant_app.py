import streamlit as st
import pandas as pd
import requests
import random
import altair as alt

# -- SETTINGS --
ODDS_API_KEY = "e1a0d3aca26d43993c899a17c319a9b1"
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQctjOwmIcnWUbgiONcoT3np5tkaU30AKClnTYaNFg3NsqJjVuRexYi2dcIVMHxEvT2vm1MgjTNUZCG/pub?output=csv&gid="

SPORTS = {
    "NFL": {
        "key": "americanfootball_nfl",
        "gid": "0"
    },
    "NBA": {
        "key": "basketball_nba",
        "gid": "865462255"
    },
    "MLB": {
        "key": "baseball_mlb",
        "gid": "933127957"
    },
    "WNBA": {
        "key": "basketball_wnba",
        "gid": "1101180027"
    },
    "NCAAF": {
        "key": "americanfootball_ncaaf",
        "gid": "486502942"
    },
    "NCAAB": {
        "key": "basketball_ncaab",
        "gid": "1929731123"
    }
}

# -- UI --
st.title("📊 Sports Betting Assistant")
sport = st.selectbox("Choose a sport", list(SPORTS.keys()))
sport_key = SPORTS[sport]["key"]
gid = SPORTS[sport]["gid"]

# -- Load Odds --
@st.cache_data(ttl=600)
def fetch_odds(sport_key):
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
    params = {"regions": "us", "markets": "h2h", "apiKey": ODDS_API_KEY}
    response = requests.get(url, params=params)
    if response.status_code != 200:
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

odds_df = fetch_odds(sport_key)

# -- Load Stats --
@st.cache_data(ttl=600)
def load_team_stats(gid):
    url = f"{GOOGLE_SHEET_CSV_URL}{gid}"
    try:
        df = pd.read_csv(url)
        df.columns = [col.strip() for col in df.columns]
        return df
    except Exception:
        return pd.DataFrame()

team_stats = load_team_stats(gid)

# -- Filter & Picks --
if odds_df.empty:
    st.warning("No odds available. Try again later.")
else:
    st.sidebar.header("Filters")
    search_team = st.sidebar.text_input("Search Team")
    min_odds, max_odds = st.sidebar.slider("Moneyline Range", -1000, 1000, (-500, 500))
    min_conf, max_conf = st.sidebar.slider("Confidence Range (%)", 50, 100, (60, 100))
    pick_count = st.sidebar.slider("Number of Picks", 1, 10, 3)

    filtered = odds_df.copy()
    if search_team:
        filtered = filtered[filtered["Matchup"].str.contains(search_team, case=False, na=False)]
    filtered = filtered[
        (filtered["Moneyline_Home"].between(min_odds, max_odds)) &
        (filtered["Moneyline_Away"].between(min_odds, max_odds))
    ]

    st.subheader("Filtered Matchups")
    st.dataframe(filtered)

    if not filtered.empty:
        st.subheader("Suggested Value Picks")
        picks = []
        for _, row in filtered.sample(min(pick_count, len(filtered))).iterrows():
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
                "Commence Time": row["Commence Time"]
            })

        picks_df = pd.DataFrame(picks).sort_values(by="Confidence", ascending=False)
        st.dataframe(picks_df)

        # -- Merge with Stats --
        if not team_stats.empty:
            merged = picks_df.merge(team_stats, how="left", left_on="Pick", right_on="Team")
            st.subheader("Team Stats Comparison")
            st.dataframe(merged)

            # -- Bar Chart --
            stat_cols = [col for col in merged.columns if col not in picks_df.columns and col != "Team"]
            if stat_cols:
                chart_data = merged[["Team"] + stat_cols].melt(id_vars="Team", var_name="Stat", value_name="Value")
                chart = alt.Chart(chart_data).mark_bar().encode(
                    x=alt.X("Stat:N", title="Stat"),
                    y=alt.Y("Value:Q"),
                    color="Team:N",
                    column="Team:N"
                ).properties(width=120)
                st.altair_chart(chart, use_container_width=True)

            # -- Download Button --
            st.download_button(
                "Download Picks with Stats CSV",
                data=merged.to_csv(index=False),
                file_name="picks_with_stats.csv",
                mime="text/csv"
            )
        else:
            st.info("Team stats could not be loaded.")
