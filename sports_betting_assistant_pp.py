import streamlit as st
import pandas as pd
import requests
import random
import altair as alt

ODDS_API_KEY = "e1a0d3aca26d43993c899a17c319a9b1"

st.title("\ud83d\udcca Sports Betting Assistant")
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
    st.sidebar.header("\ud83d\udd0e Filters")
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

    st.subheader("\ud83d\udccb Filtered Matchups")
    st.dataframe(filtered_df)

    if not filtered_df.empty:
        st.subheader("\ud83d\udd2e Suggested Value Picks")
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

        st.subheader("\ud83d\udcca Team Stats (From CSV)")
        stats_files = {
            "NFL": "nfl_team_stats.csv",
            "NBA": "nba_team_stats.csv",
            "MLB": "mlb_team_stats.csv",
            "WNBA": "wnba_team_stats.csv",
            "NCAAF": "ncaaf_team_stats.csv",
            "NCAAB": "ncaab_team_stats.csv"
        }

        try:
            stats = pd.read_csv(stats_files[sport])
            stats.iloc[:, 1:] = stats.iloc[:, 1:].apply(pd.to_numeric, errors="coerce")
            selected_teams = list(set(picks_df["Home Team"]) | set(picks_df["Away Team"]))
            team_stats = stats[stats["Team"].isin(selected_teams)]

            if team_stats.empty:
                st.info("Stats not found for selected teams.")
            else:
                st.dataframe(team_stats)

                st.subheader("\ud83d\udcca Stat Comparison Chart")
                melted = team_stats.melt(id_vars="Team", var_name="Stat", value_name="Value")

                if not melted.empty:
                    chart = alt.Chart(melted).mark_bar().encode(
                        x=alt.X('Stat:N', title="Stat Category"),
                        y=alt.Y('Value:Q', title="Stat Value"),
                        color='Team:N',
                        column=alt.Column('Team:N', spacing=10, header=alt.Header(labelAngle=0))
                    ).properties(width=120)

                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.warning("No data available to chart.")

                st.subheader("\u2b07\ufe0f Download Picks + Stats")
                download_df = picks_df.merge(stats, how="left", left_on="Pick", right_on="Team")
                st.download_button(
                    label="\ud83d\udcbe Download (CSV)",
                    data=download_df.to_csv(index=False),
                    file_name="value_picks_with_stats.csv",
                    mime="text/csv"
                )

        except FileNotFoundError:
            st.warning("Stats file not found. Please upload the correct CSV.")
        except Exception as e:
            st.error(f"Error loading stats: {e}")


