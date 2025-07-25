import streamlit as st
import pandas as pd
import requests
import random
import altair as alt

# Set your OddsAPI key
ODDS_API_KEY = "e1a0d3aca26d43993c899a17c319a9b1"

st.title("Sports Betting Assistant")

# Sport selection
sport = st.selectbox("Choose a sport", ["NFL", "NBA", "MLB", "WNBA", "NCAAF", "NCAAB"])

# Map display name to OddsAPI key
sport_key_map = {
    "NFL": "americanfootball_nfl",
    "NBA": "basketball_nba",
    "MLB": "baseball_mlb",
    "WNBA": "basketball_wnba",
    "NCAAF": "americanfootball_ncaaf",
    "NCAAB": "basketball_ncaab"
}

# Map sport to CSV file path
stats_files = {
    "NFL": "stats_nfl.csv",
    "NBA": "stats_nba.csv",
    "MLB": "stats_mlb.csv",
    "WNBA": "stats_wnba.csv",
    "NCAAF": "stats_ncaaf.csv",
    "NCAAB": "stats_ncaab.csv"
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

# Fetch live odds
df = fetch_odds_data(selected_key)

if df.empty:
    st.warning("No odds data available. Try again later.")
    st.stop()

# Sidebar filters
st.sidebar.header("Filters")
search_team = st.sidebar.text_input("Search Team")
min_odds, max_odds = st.sidebar.slider("Moneyline Range", -1000, 1000, (-1000, 1000))
bookmaker_filter = st.sidebar.multiselect("Bookmaker", df["Bookmaker"].unique())
min_conf, max_conf = st.sidebar.slider("Confidence Range (%)", 50, 100, (60, 100))
pick_count = st.sidebar.slider("Number of Picks", 1, 10, 3)

# Apply filters
filtered = df.copy()
if search_team:
    filtered = filtered[filtered["Matchup"].str.contains(search_team, case=False)]
filtered = filtered[(filtered["Moneyline_Home"].between(min_odds, max_odds)) &
                    (filtered["Moneyline_Away"].between(min_odds, max_odds))]
if bookmaker_filter:
    filtered = filtered[filtered["Bookmaker"].isin(bookmaker_filter)]

st.subheader("Filtered Matchups")
st.dataframe(filtered)

# Generate picks
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
            "Commence Time": row["Commence Time"],
            "Home Team": row["Home Team"],
            "Away Team": row["Away Team"]
        })

    picks_df = pd.DataFrame(picks).sort_values(by="Confidence", ascending=False)
    st.dataframe(picks_df)

    # Load stats automatically
    st.subheader("Team Stats")
    try:
        stats = pd.read_csv(stats_files[sport])
        selected_teams = list(set(picks_df["Home Team"]).union(set(picks_df["Away Team"])))
        team_stats = stats[stats["Team"].isin(selected_teams)]

        if not team_stats.empty:
            st.dataframe(team_stats)

            st.subheader("Stat Comparison Chart")
            melted = team_stats.melt(id_vars="Team", var_name="Stat", value_name="Value")
            chart = alt.Chart(melted).mark_bar().encode(
                x=alt.X('Stat:N', title="Stat Category"),
                y=alt.Y('Value:Q', title="Stat Value"),
                color='Team:N',
                column='Team:N'
            ).properties(width=120)

            st.altair_chart(chart, use_container_width=True)

            st.subheader("Download Picks + Stats")
            download_df = picks_df.merge(stats, how="left", left_on="Pick", right_on="Team")
            st.download_button(
                label="Download CSV",
                data=download_df.to_csv(index=False),
                file_name="value_picks_with_stats.csv",
                mime="text/csv"
            )
        else:
            st.info("No matching stats found for selected teams.")

    except Exception as e:
        st.error(f"Error loading stats: {e}")




